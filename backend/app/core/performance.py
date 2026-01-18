import asyncio
import time
import psutil
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
from fastapi import Request, Response
from sqlalchemy import text
from sqlalchemy.orm import Session
from prometheus_client import Counter, Histogram, Gauge, generate_latest
import tracemalloc
from functools import wraps
import json

from app.core.config import settings
from app.core.logging_config import app_logger
from app.core.database import get_db


# Prometheus metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')
ACTIVE_CONNECTIONS = Gauge('active_connections', 'Number of active connections')
MEMORY_USAGE = Gauge('memory_usage_bytes', 'Memory usage in bytes')
CPU_USAGE = Gauge('cpu_usage_percent', 'CPU usage percentage')
DATABASE_CONNECTIONS = Gauge('database_connections', 'Number of database connections')
PROCESSING_TIME = Histogram('processing_time_seconds', 'Processing time for various operations', ['operation'])


class PerformanceMonitor:
    """Performance monitoring and optimization utilities"""
    
    def __init__(self):
        self.start_time = time.time()
        self.request_metrics = {}
        self.system_metrics = {}
        self.database_metrics = {}
        self.memory_tracker = None
        self.enable_memory_tracking = settings.ENABLE_MEMORY_TRACKING
        
        if self.enable_memory_tracking:
            tracemalloc.start()
    
    def start_request_monitoring(self):
        """Start monitoring for the current request"""
        if self.enable_memory_tracking:
            self.memory_tracker = tracemalloc.take_snapshot()
        
        return {
            'start_time': time.time(),
            'start_memory': psutil.Process().memory_info().rss if psutil else 0
        }
    
    def end_request_monitoring(self, start_data: Dict[str, Any], request: Request, response: Response):
        """End monitoring and collect metrics"""
        end_time = time.time()
        duration = end_time - start_data['start_time']
        
        # Update Prometheus metrics
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code
        ).inc()
        
        REQUEST_DURATION.observe(duration)
        
        # Log slow requests
        if duration > settings.SLOW_REQUEST_THRESHOLD:
            app_logger.log_performance(
                f"Slow request detected: {request.method} {request.url.path}",
                duration=duration,
                endpoint=request.url.path,
                method=request.method,
                status_code=response.status_code
            )
        
        # Memory tracking
        if self.enable_memory_tracking and self.memory_tracker:
            current_memory = psutil.Process().memory_info().rss
            memory_delta = current_memory - start_data['start_memory']
            
            if memory_delta > settings.MEMORY_THRESHOLD:
                app_logger.log_performance(
                    f"High memory usage detected: {request.method} {request.url.path}",
                    memory_delta=memory_delta,
                    endpoint=request.url.path,
                    method=request.method
                )
    
    def collect_system_metrics(self):
        """Collect system performance metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            CPU_USAGE.set(cpu_percent)
            
            # Memory usage
            memory_info = psutil.virtual_memory()
            MEMORY_USAGE.set(memory_info.used)
            
            # Process-specific metrics
            process = psutil.Process()
            process_memory = process.memory_info().rss
            process_cpu = process.cpu_percent()
            
            self.system_metrics = {
                'cpu_percent': cpu_percent,
                'memory_percent': memory_info.percent,
                'memory_used': memory_info.used,
                'memory_available': memory_info.available,
                'process_memory': process_memory,
                'process_cpu': process_cpu,
                'uptime': time.time() - self.start_time
            }
            
            # Log high resource usage
            if cpu_percent > settings.HIGH_CPU_THRESHOLD:
                app_logger.log_performance(
                    f"High CPU usage detected: {cpu_percent}%",
                    cpu_percent=cpu_percent
                )
            
            if memory_info.percent > settings.HIGH_MEMORY_THRESHOLD:
                app_logger.log_performance(
                    f"High memory usage detected: {memory_info.percent}%",
                    memory_percent=memory_info.percent,
                    memory_used=memory_info.used
                )
            
        except Exception as e:
            app_logger.log_error(f"Error collecting system metrics: {e}")
    
    def collect_database_metrics(self, db: Session):
        """Collect database performance metrics"""
        try:
            # Database connection count
            result = db.execute(text("SELECT count(*) as connection_count FROM pg_stat_activity"))
            connection_count = result.scalar()
            DATABASE_CONNECTIONS.set(connection_count)
            
            # Database size
            result = db.execute(text("SELECT pg_database_size(current_database()) as db_size"))
            db_size = result.scalar()
            
            # Active queries
            result = db.execute(text("""
                SELECT count(*) as active_queries
                FROM pg_stat_activity 
                WHERE state = 'active' AND query != '<IDLE>'
            """))
            active_queries = result.scalar()
            
            # Long running queries
            result = db.execute(text("""
                SELECT count(*) as long_queries
                FROM pg_stat_activity 
                WHERE state = 'active' 
                AND now() - query_start > interval '5 seconds'
            """))
            long_queries = result.scalar()
            
            self.database_metrics = {
                'connection_count': connection_count,
                'database_size': db_size,
                'active_queries': active_queries,
                'long_queries': long_queries
            }
            
            # Log database issues
            if connection_count > settings.MAX_DB_CONNECTIONS:
                app_logger.log_performance(
                    f"High database connection count: {connection_count}",
                    connection_count=connection_count
                )
            
            if long_queries > 0:
                app_logger.log_performance(
                    f"Long running queries detected: {long_queries}",
                    long_queries=long_queries
                )
            
        except Exception as e:
            app_logger.log_error(f"Error collecting database metrics: {e}")
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'system_metrics': self.system_metrics,
            'database_metrics': self.database_metrics,
            'uptime': time.time() - self.start_time,
            'memory_tracking_enabled': self.enable_memory_tracking
        }
    
    def analyze_memory_leaks(self) -> Optional[Dict[str, Any]]:
        """Analyze potential memory leaks"""
        if not self.enable_memory_tracking:
            return None
        
        try:
            current_snapshot = tracemalloc.take_snapshot()
            
            if self.memory_tracker:
                top_stats = current_snapshot.compare_to(self.memory_tracker, 'lineno')
                
                # Find top memory consumers
                memory_leaks = []
                for stat in top_stats[:10]:
                    if stat.size_diff > settings.MEMORY_LEAK_THRESHOLD:
                        memory_leaks.append({
                            'file': stat.traceback.format()[0],
                            'size_diff': stat.size_diff,
                            'size': stat.size,
                            'count_diff': stat.count_diff
                        })
                
                if memory_leaks:
                    app_logger.log_performance(
                        "Potential memory leaks detected",
                        memory_leaks=memory_leaks
                    )
                    return {'memory_leaks': memory_leaks}
            
            self.memory_tracker = current_snapshot
            return None
            
        except Exception as e:
            app_logger.log_error(f"Error analyzing memory leaks: {e}")
            return None


class DatabaseOptimizer:
    """Database query optimization utilities"""
    
    def __init__(self):
        self.slow_queries = []
        self.query_cache = {}
    
    def analyze_query_performance(self, db: Session):
        """Analyze database query performance"""
        try:
            # Get slow queries
            result = db.execute(text("""
                SELECT query, mean_time, calls, total_time, rows, 100.0 * shared_blks_hit /
                       nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent
                FROM pg_stat_statements
                WHERE mean_time > 1000  -- queries taking more than 1 second
                ORDER BY mean_time DESC
                LIMIT 10
            """))
            
            slow_queries = []
            for row in result:
                slow_queries.append({
                    'query': row.query[:200] + '...' if len(row.query) > 200 else row.query,
                    'mean_time': row.mean_time,
                    'calls': row.calls,
                    'total_time': row.total_time,
                    'rows': row.rows,
                    'hit_percent': row.hit_percent
                })
            
            self.slow_queries = slow_queries
            
            if slow_queries:
                app_logger.log_performance(
                    f"Found {len(slow_queries)} slow queries",
                    slow_queries=slow_queries
                )
            
            return slow_queries
            
        except Exception as e:
            app_logger.log_error(f"Error analyzing query performance: {e}")
            return []
    
    def get_index_usage(self, db: Session):
        """Get database index usage statistics"""
        try:
            result = db.execute(text("""
                SELECT schemaname, tablename, indexname, idx_tup_read, idx_tup_fetch
                FROM pg_stat_user_indexes
                WHERE idx_tup_read = 0 OR idx_tup_fetch = 0
                ORDER BY schemaname, tablename
            """))
            
            unused_indexes = []
            for row in result:
                unused_indexes.append({
                    'schema': row.schemaname,
                    'table': row.tablename,
                    'index': row.indexname,
                    'reads': row.idx_tup_read,
                    'fetches': row.idx_tup_fetch
                })
            
            if unused_indexes:
                app_logger.log_performance(
                    f"Found {len(unused_indexes)} potentially unused indexes",
                    unused_indexes=unused_indexes
                )
            
            return unused_indexes
            
        except Exception as e:
            app_logger.log_error(f"Error analyzing index usage: {e}")
            return []
    
    def suggest_optimizations(self, db: Session) -> List[Dict[str, Any]]:
        """Suggest database optimizations"""
        suggestions = []
        
        try:
            # Check for missing indexes
            result = db.execute(text("""
                SELECT schemaname, tablename, seq_scan, seq_tup_read, 
                       idx_scan, idx_tup_fetch, n_tup_ins, n_tup_upd, n_tup_del
                FROM pg_stat_user_tables
                WHERE seq_scan > 1000 AND seq_tup_read > 100000
                ORDER BY seq_tup_read DESC
            """))
            
            for row in result:
                if row.seq_scan > row.idx_scan * 2:  # More sequential scans than index scans
                    suggestions.append({
                        'type': 'missing_index',
                        'table': f"{row.schemaname}.{row.tablename}",
                        'description': f"Table {row.tablename} has high sequential scan ratio",
                        'seq_scans': row.seq_scan,
                        'seq_reads': row.seq_tup_read,
                        'idx_scans': row.idx_scan
                    })
            
            # Check for bloated tables
            result = db.execute(text("""
                SELECT schemaname, tablename, n_tup_ins, n_tup_upd, n_tup_del
                FROM pg_stat_user_tables
                WHERE n_tup_del > n_tup_ins * 0.1  -- More than 10% deletions
                ORDER BY n_tup_del DESC
            """))
            
            for row in result:
                suggestions.append({
                    'type': 'table_bloat',
                    'table': f"{row.schemaname}.{row.tablename}",
                    'description': f"Table {row.tablename} may be bloated",
                    'inserts': row.n_tup_ins,
                    'updates': row.n_tup_upd,
                    'deletes': row.n_tup_del
                })
            
            return suggestions
            
        except Exception as e:
            app_logger.log_error(f"Error generating optimization suggestions: {e}")
            return []


class PerformanceMiddleware:
    """Performance monitoring middleware"""
    
    def __init__(self):
        self.monitor = PerformanceMonitor()
        self.db_optimizer = DatabaseOptimizer()
    
    async def __call__(self, request: Request, call_next):
        """Process request with performance monitoring"""
        start_data = self.monitor.start_request_monitoring()
        
        # Execute request
        response = await call_next(request)
        
        # End monitoring
        self.monitor.end_request_monitoring(start_data, request, response)
        
        return response
    
    def get_metrics_endpoint(self):
        """Get Prometheus metrics endpoint"""
        return generate_latest()


def performance_timer(operation_name: str):
    """Decorator to time operations"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                PROCESSING_TIME.labels(operation=operation_name).observe(duration)
                
                # Log slow operations
                if duration > settings.SLOW_OPERATION_THRESHOLD:
                    app_logger.log_performance(
                        f"Slow operation: {operation_name}",
                        duration=duration,
                        operation=operation_name
                    )
                
                return result
            except Exception as e:
                duration = time.time() - start_time
                app_logger.log_error(
                    f"Error in operation {operation_name}: {e}",
                    duration=duration,
                    operation=operation_name
                )
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                PROCESSING_TIME.labels(operation=operation_name).observe(duration)
                
                if duration > settings.SLOW_OPERATION_THRESHOLD:
                    app_logger.log_performance(
                        f"Slow operation: {operation_name}",
                        duration=duration,
                        operation=operation_name
                    )
                
                return result
            except Exception as e:
                duration = time.time() - start_time
                app_logger.log_error(
                    f"Error in operation {operation_name}: {e}",
                    duration=duration,
                    operation=operation_name
                )
                raise
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator


@asynccontextmanager
async def performance_context(operation_name: str):
    """Context manager for performance monitoring"""
    start_time = time.time()
    start_memory = psutil.Process().memory_info().rss if psutil else 0
    
    try:
        yield
    finally:
        duration = time.time() - start_time
        end_memory = psutil.Process().memory_info().rss if psutil else 0
        memory_delta = end_memory - start_memory
        
        PROCESSING_TIME.labels(operation=operation_name).observe(duration)
        
        app_logger.log_performance(
            f"Operation completed: {operation_name}",
            duration=duration,
            memory_delta=memory_delta,
            operation=operation_name
        )


class PerformanceOptimizer:
    """Performance optimization utilities"""
    
    def __init__(self):
        self.cache = {}
        self.cache_hits = 0
        self.cache_misses = 0
    
    def cached_operation(self, cache_key: str, ttl: int = 300):
        """Cache decorator for expensive operations"""
        def decorator(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                # Check cache
                if cache_key in self.cache:
                    cached_data, timestamp = self.cache[cache_key]
                    if time.time() - timestamp < ttl:
                        self.cache_hits += 1
                        return cached_data
                
                # Execute function
                self.cache_misses += 1
                result = await func(*args, **kwargs)
                
                # Cache result
                self.cache[cache_key] = (result, time.time())
                return result
            
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                # Check cache
                if cache_key in self.cache:
                    cached_data, timestamp = self.cache[cache_key]
                    if time.time() - timestamp < ttl:
                        self.cache_hits += 1
                        return cached_data
                
                # Execute function
                self.cache_misses += 1
                result = func(*args, **kwargs)
                
                # Cache result
                self.cache[cache_key] = (result, time.time())
                return result
            
            return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
        return decorator
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.cache_hits + self.cache_misses
        hit_rate = self.cache_hits / total_requests if total_requests > 0 else 0
        
        return {
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'hit_rate': hit_rate,
            'cached_items': len(self.cache)
        }
    
    def clear_cache(self):
        """Clear all cached data"""
        self.cache.clear()
        app_logger.log_performance("Cache cleared")


# Global instances
performance_monitor = PerformanceMonitor()
performance_middleware = PerformanceMiddleware()
performance_optimizer = PerformanceOptimizer()
database_optimizer = DatabaseOptimizer()


# Background task for system monitoring
async def system_monitoring_task():
    """Background task for continuous system monitoring"""
    while True:
        try:
            # Collect system metrics
            performance_monitor.collect_system_metrics()
            
            # Analyze memory leaks
            if performance_monitor.enable_memory_tracking:
                performance_monitor.analyze_memory_leaks()
            
            # Sleep for monitoring interval
            await asyncio.sleep(settings.MONITORING_INTERVAL)
            
        except Exception as e:
            app_logger.log_error(f"Error in system monitoring task: {e}")
            await asyncio.sleep(60)  # Wait 1 minute before retrying


# Utility functions
def get_performance_metrics() -> Dict[str, Any]:
    """Get comprehensive performance metrics"""
    return {
        'system_metrics': performance_monitor.system_metrics,
        'database_metrics': performance_monitor.database_metrics,
        'cache_stats': performance_optimizer.get_cache_stats(),
        'uptime': time.time() - performance_monitor.start_time,
        'prometheus_metrics': performance_middleware.get_metrics_endpoint()
    }


def optimize_database_queries(db: Session) -> Dict[str, Any]:
    """Run database optimization analysis"""
    slow_queries = database_optimizer.analyze_query_performance(db)
    unused_indexes = database_optimizer.get_index_usage(db)
    suggestions = database_optimizer.suggest_optimizations(db)
    
    return {
        'slow_queries': slow_queries,
        'unused_indexes': unused_indexes,
        'optimization_suggestions': suggestions
    }

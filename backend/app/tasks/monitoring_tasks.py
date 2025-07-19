from celery import shared_task
from celery.utils.log import get_task_logger
from typing import Dict, Any
from datetime import datetime, timedelta
import traceback

from app.core.database import SessionLocal
from app.models.resume import Resume
from app.models.job_description import JobDescription
from app.models.match import Match
from app.models.candidate import Candidate

logger = get_task_logger(__name__)


@shared_task(bind=True)
def cleanup_old_tasks(self, days_old: int = 30) -> Dict[str, Any]:
    """
    Clean up old task results and temporary files
    """
    try:
        logger.info(f"Starting cleanup of tasks older than {days_old} days")
        
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        with SessionLocal() as db:
            # Clean up old failed resumes
            old_failed_resumes = db.query(Resume).filter(
                Resume.status == "failed",
                Resume.upload_date < cutoff_date
            ).count()
            
            if old_failed_resumes > 0:
                db.query(Resume).filter(
                    Resume.status == "failed",
                    Resume.upload_date < cutoff_date
                ).delete()
                
            # Clean up old inactive job descriptions
            old_inactive_jobs = db.query(JobDescription).filter(
                JobDescription.status == "inactive",
                JobDescription.scraped_date < cutoff_date
            ).count()
            
            if old_inactive_jobs > 0:
                db.query(JobDescription).filter(
                    JobDescription.status == "inactive",
                    JobDescription.scraped_date < cutoff_date
                ).delete()
            
            db.commit()
            
            logger.info(f"Cleaned up {old_failed_resumes} failed resumes and {old_inactive_jobs} inactive jobs")
            
            return {
                'status': 'success',
                'cleaned_resumes': old_failed_resumes,
                'cleaned_jobs': old_inactive_jobs,
                'cutoff_date': cutoff_date.isoformat()
            }
            
    except Exception as exc:
        logger.error(f"Error during cleanup: {str(exc)}")
        logger.error(traceback.format_exc())
        return {
            'status': 'failed',
            'error': str(exc)
        }


@shared_task(bind=True)
def generate_system_report(self) -> Dict[str, Any]:
    """
    Generate system health and usage report
    """
    try:
        logger.info("Generating system report")
        
        with SessionLocal() as db:
            # Resume statistics
            total_resumes = db.query(Resume).count()
            processed_resumes = db.query(Resume).filter(Resume.status == "completed").count()
            failed_resumes = db.query(Resume).filter(Resume.status == "failed").count()
            processing_resumes = db.query(Resume).filter(Resume.status == "processing").count()
            
            # Job statistics
            total_jobs = db.query(JobDescription).count()
            active_jobs = db.query(JobDescription).filter(JobDescription.status == "active").count()
            scraped_jobs = db.query(JobDescription).filter(JobDescription.source.isnot(None)).count()
            
            # Match statistics
            total_matches = db.query(Match).count()
            high_score_matches = db.query(Match).filter(Match.overall_score >= 80).count()
            medium_score_matches = db.query(Match).filter(
                Match.overall_score >= 60,
                Match.overall_score < 80
            ).count()
            
            # Candidate statistics
            total_candidates = db.query(Candidate).count()
            candidates_with_email = db.query(Candidate).filter(Candidate.email.isnot(None)).count()
            
            # Recent activity (last 7 days)
            week_ago = datetime.utcnow() - timedelta(days=7)
            recent_resumes = db.query(Resume).filter(Resume.upload_date >= week_ago).count()
            recent_jobs = db.query(JobDescription).filter(JobDescription.created_at >= week_ago).count()
            recent_matches = db.query(Match).filter(Match.created_at >= week_ago).count()
            
            # Calculate processing success rate
            if total_resumes > 0:
                success_rate = (processed_resumes / total_resumes) * 100
            else:
                success_rate = 0
            
            # Calculate average match score
            avg_match_score = db.query(Match).with_entities(
                db.func.avg(Match.overall_score)
            ).scalar() or 0
            
            report = {
                'status': 'success',
                'generated_at': datetime.utcnow().isoformat(),
                'system_health': {
                    'total_resumes': total_resumes,
                    'processed_resumes': processed_resumes,
                    'failed_resumes': failed_resumes,
                    'processing_resumes': processing_resumes,
                    'processing_success_rate': round(success_rate, 2)
                },
                'job_statistics': {
                    'total_jobs': total_jobs,
                    'active_jobs': active_jobs,
                    'scraped_jobs': scraped_jobs,
                    'manual_jobs': total_jobs - scraped_jobs
                },
                'matching_statistics': {
                    'total_matches': total_matches,
                    'high_score_matches': high_score_matches,
                    'medium_score_matches': medium_score_matches,
                    'low_score_matches': total_matches - high_score_matches - medium_score_matches,
                    'average_match_score': round(float(avg_match_score), 2)
                },
                'candidate_statistics': {
                    'total_candidates': total_candidates,
                    'candidates_with_email': candidates_with_email,
                    'contact_completion_rate': round((candidates_with_email / total_candidates) * 100, 2) if total_candidates > 0 else 0
                },
                'recent_activity': {
                    'recent_resumes': recent_resumes,
                    'recent_jobs': recent_jobs,
                    'recent_matches': recent_matches
                }
            }
            
            logger.info("System report generated successfully")
            return report
            
    except Exception as exc:
        logger.error(f"Error generating system report: {str(exc)}")
        logger.error(traceback.format_exc())
        return {
            'status': 'failed',
            'error': str(exc)
        }


@shared_task(bind=True)
def monitor_system_health(self) -> Dict[str, Any]:
    """
    Monitor system health and alert on issues
    """
    try:
        logger.info("Monitoring system health")
        
        alerts = []
        
        with SessionLocal() as db:
            # Check for high number of failed resumes
            failed_resumes = db.query(Resume).filter(Resume.status == "failed").count()
            total_resumes = db.query(Resume).count()
            
            if total_resumes > 0:
                failure_rate = (failed_resumes / total_resumes) * 100
                if failure_rate > 10:  # Alert if more than 10% failed
                    alerts.append({
                        'type': 'high_failure_rate',
                        'message': f'High resume processing failure rate: {failure_rate:.1f}%',
                        'severity': 'warning'
                    })
            
            # Check for stuck processing jobs
            stuck_processing = db.query(Resume).filter(
                Resume.status == "processing",
                Resume.processed_date < datetime.utcnow() - timedelta(hours=2)
            ).count()
            
            if stuck_processing > 0:
                alerts.append({
                    'type': 'stuck_processing',
                    'message': f'{stuck_processing} resumes stuck in processing state',
                    'severity': 'error'
                })
            
            # Check for low match quality
            recent_matches = db.query(Match).filter(
                Match.created_at >= datetime.utcnow() - timedelta(days=1)
            ).all()
            
            if recent_matches:
                avg_score = sum(match.overall_score for match in recent_matches) / len(recent_matches)
                if avg_score < 40:  # Alert if average match score is too low
                    alerts.append({
                        'type': 'low_match_quality',
                        'message': f'Low average match score in last 24h: {avg_score:.1f}',
                        'severity': 'warning'
                    })
            
            # Check for system capacity
            processing_queue = db.query(Resume).filter(Resume.status == "processing").count()
            if processing_queue > 50:  # Alert if too many items in processing queue
                alerts.append({
                    'type': 'high_processing_queue',
                    'message': f'High processing queue: {processing_queue} items',
                    'severity': 'warning'
                })
            
            health_status = 'healthy' if len(alerts) == 0 else 'warning'
            if any(alert['severity'] == 'error' for alert in alerts):
                health_status = 'error'
            
            logger.info(f"System health check completed - Status: {health_status}")
            
            return {
                'status': 'success',
                'health_status': health_status,
                'alerts': alerts,
                'checked_at': datetime.utcnow().isoformat(),
                'metrics': {
                    'total_resumes': total_resumes,
                    'failed_resumes': failed_resumes,
                    'processing_queue': processing_queue,
                    'recent_matches': len(recent_matches)
                }
            }
            
    except Exception as exc:
        logger.error(f"Error monitoring system health: {str(exc)}")
        logger.error(traceback.format_exc())
        return {
            'status': 'failed',
            'error': str(exc)
        }

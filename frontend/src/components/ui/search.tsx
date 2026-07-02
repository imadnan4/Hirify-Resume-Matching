import React, { useState, useCallback, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Search as SearchIcon, X, Filter, SortDesc } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Input } from './input';
import { Button } from './button';
import { Badge } from './badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './select';

interface SearchProps {
  onSearch: (query: string) => void;
  placeholder?: string;
  className?: string;
  debounceMs?: number;
  showFilters?: boolean;
  filters?: SearchFilter[];
  onFilterChange?: (filters: Record<string, any>) => void;
}

interface SearchFilter {
  key: string;
  label: string;
  type: 'select' | 'multiselect' | 'range' | 'date';
  options?: { value: string; label: string }[];
  min?: number;
  max?: number;
}

interface SearchWithResultsProps extends SearchProps {
  results: any[];
  isLoading?: boolean;
  totalResults?: number;
  onResultClick?: (result: any) => void;
  renderResult?: (result: any, index: number) => React.ReactNode;
  noResultsMessage?: string;
}

export const Search: React.FC<SearchProps> = ({
  onSearch,
  placeholder = "Search...",
  className,
  debounceMs = 300,
  showFilters = false,
  filters = [],
  onFilterChange,
}) => {
  const [query, setQuery] = useState('');
  const [activeFilters, setActiveFilters] = useState<Record<string, any>>({});
  const [showFilterPanel, setShowFilterPanel] = useState(false);

  // Debounced search
  useEffect(() => {
    const timer = setTimeout(() => {
      onSearch(query);
    }, debounceMs);

    return () => clearTimeout(timer);
  }, [query, debounceMs, onSearch]);

  const handleFilterChange = useCallback((filterKey: string, value: any) => {
    const newFilters = { ...activeFilters, [filterKey]: value };
    setActiveFilters(newFilters);
    onFilterChange?.(newFilters);
  }, [activeFilters, onFilterChange]);

  const clearFilter = useCallback((filterKey: string) => {
    const newFilters = { ...activeFilters };
    delete newFilters[filterKey];
    setActiveFilters(newFilters);
    onFilterChange?.(newFilters);
  }, [activeFilters, onFilterChange]);

  const clearAllFilters = useCallback(() => {
    setActiveFilters({});
    onFilterChange?.({});
  }, [onFilterChange]);

  const activeFilterCount = Object.keys(activeFilters).length;

  return (
    <div className={cn('w-full space-y-4', className)}>
      {/* Search Bar */}
      <motion.div
        className="relative"
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.2 }}
      >
        <div className="relative">
          <SearchIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
          <Input
            type="text"
            placeholder={placeholder}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="pl-10 pr-20"
          />
          
          <div className="absolute right-2 top-1/2 transform -translate-y-1/2 flex items-center gap-1">
            {query && (
              <motion.button
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.8 }}
                onClick={() => setQuery('')}
                className="p-1 hover:bg-muted rounded-sm transition-colors"
              >
                <X className="h-4 w-4" />
              </motion.button>
            )}
            
            {showFilters && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowFilterPanel(!showFilterPanel)}
                className="h-8 w-8 p-0 relative"
              >
                <Filter className="h-4 w-4" />
                {activeFilterCount > 0 && (
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    className="absolute -top-1 -right-1 h-4 w-4 bg-primary text-primary-foreground rounded-full text-xs flex items-center justify-center"
                  >
                    {activeFilterCount}
                  </motion.div>
                )}
              </Button>
            )}
          </div>
        </div>
      </motion.div>

      {/* Active Filters */}
      <AnimatePresence>
        {activeFilterCount > 0 && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="flex flex-wrap gap-2 items-center"
          >
            <span className="text-sm text-muted-foreground">Filters:</span>
            {Object.entries(activeFilters).map(([key, value]) => (
              <motion.div
                key={key}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.8 }}
              >
                <Badge variant="secondary" className="gap-1">
                  {filters.find(f => f.key === key)?.label}: {String(value)}
					<Button
						onClick={() => clearFilter(key)}
						variant="ghost"
						size="icon-xs"
						className="ml-1 rounded-full"
					>
						<X className="h-3 w-3" />
					</Button>
                </Badge>
              </motion.div>
            ))}
            <Button
              variant="ghost"
              size="sm"
              onClick={clearAllFilters}
              className="h-6 px-2 text-xs"
            >
              Clear all
            </Button>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Filter Panel */}
      <AnimatePresence>
        {showFilterPanel && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="border rounded-lg p-4 bg-card"
          >
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filters.map((filter) => (
                <motion.div
                  key={filter.key}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.1 }}
                  className="space-y-2"
                >
                  <label className="text-sm font-medium">{filter.label}</label>
                  {filter.type === 'select' && (
                    <Select
                      value={activeFilters[filter.key] || ''}
                      onValueChange={(value) => handleFilterChange(filter.key, value)}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select..." />
                      </SelectTrigger>
                      <SelectContent>
                        {filter.options?.map((option) => (
                          <SelectItem key={option.value} value={option.value}>
                            {option.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  )}
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export const SearchWithResults: React.FC<SearchWithResultsProps> = ({
  results,
  isLoading = false,
  totalResults = 0,
  onResultClick,
  renderResult,
  noResultsMessage = "No results found",
  ...searchProps
}) => {
  return (
    <div className="space-y-4">
      <Search {...searchProps} />
      
      {/* Results Summary */}
      <motion.div
        className="flex items-center justify-between text-sm text-muted-foreground"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
      >
        <span>
          {isLoading ? 'Searching...' : `${totalResults} results found`}
        </span>
        <div className="flex items-center gap-2">
          <span>Sort by:</span>
          <Button variant="ghost" size="sm" className="h-6 px-2">
            Relevance <SortDesc className="h-3 w-3 ml-1" />
          </Button>
        </div>
      </motion.div>

      {/* Results */}
      <AnimatePresence mode="wait">
        {isLoading ? (
          <motion.div
            key="loading"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="space-y-4"
          >
            {[...Array(3)].map((_, i) => (
              <div key={i} className="animate-pulse space-y-2">
                <div className="h-4 bg-muted rounded w-3/4"></div>
                <div className="h-3 bg-muted rounded w-1/2"></div>
              </div>
            ))}
          </motion.div>
        ) : results.length === 0 ? (
          <motion.div
            key="no-results"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="text-center py-8"
          >
            <SearchIcon className="h-12 w-12 mx-auto text-muted-foreground/50 mb-4" />
            <p className="text-muted-foreground">{noResultsMessage}</p>
          </motion.div>
        ) : (
          <motion.div
            key="results"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="space-y-2"
          >
            {results.map((result, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
                className="cursor-pointer hover:bg-muted/50 p-3 rounded-lg transition-colors"
                onClick={() => onResultClick?.(result)}
              >
                {renderResult ? (
                  renderResult(result, index)
                ) : (
                  <div>
                    <p className="font-medium">{result.title || result.name}</p>
                    <p className="text-sm text-muted-foreground">
                      {result.description || result.summary}
                    </p>
                  </div>
                )}
              </motion.div>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default Search;

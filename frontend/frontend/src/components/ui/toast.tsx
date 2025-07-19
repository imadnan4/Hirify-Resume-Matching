import React, { createContext, useContext, useReducer, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, CheckCircle, AlertCircle, AlertTriangle, Info } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from './button';

export interface Toast {
  id: string;
  title?: string;
  description?: string;
  type: 'success' | 'error' | 'warning' | 'info';
  duration?: number;
  action?: {
    label: string;
    onClick: () => void;
  };
}

interface ToastState {
  toasts: Toast[];
}

type ToastAction = 
  | { type: 'ADD_TOAST'; payload: Toast }
  | { type: 'REMOVE_TOAST'; payload: string }
  | { type: 'CLEAR_TOASTS' };

const toastReducer = (state: ToastState, action: ToastAction): ToastState => {
  switch (action.type) {
    case 'ADD_TOAST':
      return {
        ...state,
        toasts: [action.payload, ...state.toasts],
      };
    case 'REMOVE_TOAST':
      return {
        ...state,
        toasts: state.toasts.filter(toast => toast.id !== action.payload),
      };
    case 'CLEAR_TOASTS':
      return {
        ...state,
        toasts: [],
      };
    default:
      return state;
  }
};

interface ToastContextType {
  toasts: Toast[];
  addToast: (toast: Omit<Toast, 'id'>) => void;
  removeToast: (id: string) => void;
  clearToasts: () => void;
}

const ToastContext = createContext<ToastContextType | undefined>(undefined);

export const ToastProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [state, dispatch] = useReducer(toastReducer, { toasts: [] });

  const addToast = useCallback((toast: Omit<Toast, 'id'>) => {
    const id = Math.random().toString(36).substring(2, 9);
    const newToast: Toast = {
      ...toast,
      id,
      duration: toast.duration ?? 5000,
    };

    dispatch({ type: 'ADD_TOAST', payload: newToast });

    // Auto-remove after duration
    if (newToast.duration && newToast.duration > 0) {
      setTimeout(() => {
        dispatch({ type: 'REMOVE_TOAST', payload: id });
      }, newToast.duration);
    }
  }, []);

  const removeToast = useCallback((id: string) => {
    dispatch({ type: 'REMOVE_TOAST', payload: id });
  }, []);

  const clearToasts = useCallback(() => {
    dispatch({ type: 'CLEAR_TOASTS' });
  }, []);

  return (
    <ToastContext.Provider value={{ toasts: state.toasts, addToast, removeToast, clearToasts }}>
      {children}
      <ToastContainer />
    </ToastContext.Provider>
  );
};

export const useToast = () => {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
};

const ToastContainer: React.FC = () => {
  const { toasts } = useToast();

  return (
    <div className="fixed top-4 right-4 z-50 flex flex-col gap-2 max-w-sm w-full">
      <AnimatePresence mode="popLayout">
        {toasts.map((toast) => (
          <ToastItem key={toast.id} toast={toast} />
        ))}
      </AnimatePresence>
    </div>
  );
};

const ToastItem: React.FC<{ toast: Toast }> = ({ toast }) => {
  const { removeToast } = useToast();

  const icons = {
    success: CheckCircle,
    error: AlertCircle,
    warning: AlertTriangle,
    info: Info,
  };

  const Icon = icons[toast.type];

  const variants = {
    success: 'bg-green-50 text-green-800 border-green-200 dark:bg-green-900/20 dark:text-green-400 dark:border-green-800',
    error: 'bg-red-50 text-red-800 border-red-200 dark:bg-red-900/20 dark:text-red-400 dark:border-red-800',
    warning: 'bg-yellow-50 text-yellow-800 border-yellow-200 dark:bg-yellow-900/20 dark:text-yellow-400 dark:border-yellow-800',
    info: 'bg-blue-50 text-blue-800 border-blue-200 dark:bg-blue-900/20 dark:text-blue-400 dark:border-blue-800',
  };

  const iconColors = {
    success: 'text-green-500',
    error: 'text-red-500',
    warning: 'text-yellow-500',
    info: 'text-blue-500',
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: -20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: -20, scale: 0.95 }}
      layout
      className={cn(
        'relative flex items-start gap-3 p-4 rounded-lg border shadow-lg',
        variants[toast.type]
      )}
    >
      <div className="flex-shrink-0">
        <Icon className={cn('h-5 w-5', iconColors[toast.type])} />
      </div>
      
      <div className="flex-1 min-w-0">
        {toast.title && (
          <h4 className="font-medium text-sm">{toast.title}</h4>
        )}
        {toast.description && (
          <p className="text-sm opacity-90 mt-1">{toast.description}</p>
        )}
        
        {toast.action && (
          <div className="mt-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={toast.action.onClick}
              className="h-8 px-3 text-xs"
            >
              {toast.action.label}
            </Button>
          </div>
        )}
      </div>
      
      <button
        onClick={() => removeToast(toast.id)}
        className="flex-shrink-0 p-1 hover:bg-black/5 rounded-sm transition-colors"
      >
        <X className="h-4 w-4" />
      </button>
    </motion.div>
  );
};

// Convenience functions
export const toast = {
  success: (message: string, options?: Partial<Toast>) => {
    const { addToast } = useToast();
    addToast({
      type: 'success',
      description: message,
      ...options,
    });
  },
  error: (message: string, options?: Partial<Toast>) => {
    const { addToast } = useToast();
    addToast({
      type: 'error',
      description: message,
      ...options,
    });
  },
  warning: (message: string, options?: Partial<Toast>) => {
    const { addToast } = useToast();
    addToast({
      type: 'warning',
      description: message,
      ...options,
    });
  },
  info: (message: string, options?: Partial<Toast>) => {
    const { addToast } = useToast();
    addToast({
      type: 'info',
      description: message,
      ...options,
    });
  },
};

export default ToastProvider;

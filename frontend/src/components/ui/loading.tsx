import React from 'react';
import { motion } from 'framer-motion';
import { Loader2, FileText, Search, Zap } from 'lucide-react';
import { cn } from '@/lib/utils';

interface LoadingProps {
  size?: 'sm' | 'md' | 'lg';
  variant?: 'spinner' | 'pulse' | 'dots' | 'progress';
  className?: string;
  text?: string;
}

interface LoadingScreenProps {
  message?: string;
  submessage?: string;
  progress?: number;
  className?: string;
}

export const Loading: React.FC<LoadingProps> = ({
  size = 'md',
  variant = 'spinner',
  className,
  text,
}) => {
  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-6 w-6',
    lg: 'h-8 w-8',
  };

  const renderSpinner = () => (
    <motion.div
      className={cn('flex items-center gap-2', className)}
      role="status"
      aria-live="polite"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.2 }}
    >
      <Loader2 className={cn(sizeClasses[size], 'animate-spin')} />
      {text && <span className="text-sm text-muted-foreground">{text}</span>}
    </motion.div>
  );

  const renderPulse = () => (
    <motion.div
      className={cn('flex items-center gap-2', className)}
      role="status"
      aria-live="polite"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.2 }}
    >
      <motion.div
        className={cn('rounded-full bg-primary', sizeClasses[size])}
        animate={{ scale: [1, 1.2, 1] }}
        transition={{ duration: 1.5, repeat: Infinity, ease: 'easeInOut' }}
      />
      {text && <span className="text-sm text-muted-foreground">{text}</span>}
    </motion.div>
  );

  const renderDots = () => (
    <motion.div
      className={cn('flex items-center gap-2', className)}
      role="status"
      aria-live="polite"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.2 }}
    >
      <div className="flex gap-1">
        {[0, 1, 2].map((i) => (
          <motion.div
            key={i}
            className={cn('rounded-full bg-primary', size === 'sm' ? 'h-2 w-2' : size === 'md' ? 'h-3 w-3' : 'h-4 w-4')}
            animate={{ y: [0, -8, 0] }}
            transition={{
              duration: 0.8,
              repeat: Infinity,
              delay: i * 0.2,
              ease: 'easeInOut',
            }}
          />
        ))}
      </div>
      {text && <span className="text-sm text-muted-foreground ml-2">{text}</span>}
    </motion.div>
  );

  const renderProgress = () => (
    <motion.div
      className={cn('flex items-center gap-2', className)}
      role="status"
      aria-live="polite"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.2 }}
    >
      <div className={cn('border-2 border-primary border-t-transparent rounded-full', sizeClasses[size], 'animate-spin')} />
      {text && <span className="text-sm text-muted-foreground">{text}</span>}
    </motion.div>
  );

  const variants = {
    spinner: renderSpinner,
    pulse: renderPulse,
    dots: renderDots,
    progress: renderProgress,
  };

  return variants[variant]();
};

/**
 * LoadingScreen must be rendered inside Framer Motion's AnimatePresence
 * for the root and nested exit animations to run. The caller controls
 * mount/unmount; do not wrap with a local AnimatePresence.
 */
export const LoadingScreen: React.FC<LoadingScreenProps> = ({
  message = 'Processing your resume...',
  submessage = 'This may take a few moments',
  progress,
  className,
}) => {
  const processingSteps = [
    { icon: FileText, label: 'Analyzing document structure' },
    { icon: Search, label: 'Extracting key information' },
    { icon: Zap, label: 'Generating insights' },
  ];

  return (
    <motion.div
      className={cn(
        'fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm',
        className
      )}
      role="status"
      aria-live="polite"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.3 }}
    >
      <motion.div
        className="flex flex-col items-center space-y-6 p-8 rounded-lg bg-card border shadow-lg max-w-md w-full mx-4"
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.9, opacity: 0 }}
        transition={{ duration: 0.3, delay: 0.1 }}
      >
        {/* Main loading animation */}
        <div className="relative">
          <motion.div
            className="h-16 w-16 rounded-full border-4 border-primary/20 border-t-primary"
            animate={{ rotate: 360 }}
            transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
          />
          <motion.div
            className="absolute inset-0 h-16 w-16 rounded-full border-4 border-transparent border-r-primary/40"
            animate={{ rotate: -360 }}
            transition={{ duration: 3, repeat: Infinity, ease: 'linear' }}
          />
        </div>

        {/* Messages */}
        <div className="text-center space-y-2">
          <motion.h3
            className="text-lg font-semibold"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            {message}
          </motion.h3>
          <motion.p
            className="text-sm text-muted-foreground"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            {submessage}
          </motion.p>
        </div>

        {/* Progress bar */}
        {typeof progress === 'number' && (
          <motion.div
            className="w-full space-y-2"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <div className="flex justify-between text-xs text-muted-foreground">
              <span>Progress</span>
              <span>{progress}%</span>
            </div>
            <div className="w-full bg-muted rounded-full h-2">
              <motion.div
                className="bg-primary h-2 rounded-full"
                initial={{ width: 0 }}
                animate={{ width: `${progress}%` }}
                transition={{ duration: 0.5 }}
              />
            </div>
          </motion.div>
        )}

        {/* Processing steps */}
        <motion.div
          className="space-y-3 w-full"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          {processingSteps.map((step, index) => (
            <motion.div
              key={index}
              className="flex items-center gap-3 text-sm"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.6 + index * 0.1 }}
            >
              <motion.div
                className="flex-shrink-0 p-1.5 rounded-full bg-primary/10"
                animate={{ scale: [1, 1.1, 1] }}
                transition={{
                  duration: 2,
                  repeat: Infinity,
                  delay: index * 0.3,
                  ease: 'easeInOut',
                }}
              >
                <step.icon className="h-4 w-4 text-primary" />
              </motion.div>
              <span className="text-muted-foreground">{step.label}</span>
            </motion.div>
          ))}
        </motion.div>
      </motion.div>
    </motion.div>
  );
};

export default Loading;

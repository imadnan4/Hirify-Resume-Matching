import React, { useCallback, useRef, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, File, X, CheckCircle, AlertCircle } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from './button';
import { Progress } from './progress';

interface FileUploadProps {
  onFilesSelect: (files: File[]) => void;
  accept?: string;
  maxSize?: number; // in MB
  multiple?: boolean;
  className?: string;
  disabled?: boolean;
}

interface FileStatus {
  file: File;
  status: 'pending' | 'uploading' | 'success' | 'error';
  progress?: number;
  error?: string;
}

export const FileUpload: React.FC<FileUploadProps> = ({
  onFilesSelect,
  accept = '.pdf,.doc,.docx',
  maxSize = 5,
  multiple = false,
  className,
  disabled = false,
}) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const [files, setFiles] = useState<FileStatus[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const validateFile = (file: File): string | null => {
    const maxSizeBytes = maxSize * 1024 * 1024;
    if (file.size > maxSizeBytes) {
      return `File size exceeds ${maxSize}MB limit`;
    }
    
    if (accept) {
      const acceptedTypes = accept.split(',').map(type => type.trim());
      const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase();
      if (!acceptedTypes.includes(fileExtension)) {
        return `File type not supported. Accepted types: ${accept}`;
      }
    }
    
    return null;
  };

  const handleFiles = useCallback((selectedFiles: FileList | null) => {
    if (!selectedFiles || disabled) return;

    const fileArray = Array.from(selectedFiles);
    const validFiles: File[] = [];
    const newFileStatuses: FileStatus[] = [];

    fileArray.forEach(file => {
      const error = validateFile(file);
      if (error) {
        newFileStatuses.push({
          file,
          status: 'error',
          error,
        });
      } else {
        validFiles.push(file);
        newFileStatuses.push({
          file,
          status: 'pending',
        });
      }
    });

    setFiles(prev => multiple ? [...prev, ...newFileStatuses] : newFileStatuses.slice(0, 1));
    
    if (validFiles.length > 0) {
      onFilesSelect(multiple ? validFiles : validFiles.slice(0, 1));
    }
  }, [onFilesSelect, multiple, disabled, accept, maxSize]);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    if (!disabled) {
      setIsDragOver(true);
    }
  }, [disabled]);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    if (!disabled) {
      handleFiles(e.dataTransfer.files);
    }
  }, [handleFiles, disabled]);

  const handleInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    handleFiles(e.target.files);
  }, [handleFiles]);

  const removeFile = useCallback((index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  }, []);

  const updateFileStatus = useCallback((index: number, status: FileStatus['status'], progress?: number, error?: string) => {
    setFiles(prev => prev.map((file, i) => 
      i === index ? { ...file, status, progress, error } : file
    ));
  }, []);

  return (
    <div className={cn('w-full', className)}>
      <motion.div
        className={cn(
          'relative border-2 border-dashed rounded-lg p-8 text-center transition-colors',
          isDragOver && !disabled
            ? 'border-primary bg-primary/5'
            : 'border-muted-foreground/25 hover:border-muted-foreground/50',
          disabled && 'opacity-50 cursor-not-allowed'
        )}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        animate={{
          scale: isDragOver ? 1.02 : 1,
          borderColor: isDragOver ? 'hsl(var(--primary))' : 'hsl(var(--muted-foreground) / 0.25)',
        }}
        transition={{ duration: 0.2 }}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept={accept}
          multiple={multiple}
          onChange={handleInputChange}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          disabled={disabled}
        />
        
        <motion.div
          className="flex flex-col items-center gap-4"
          animate={{ y: isDragOver ? -5 : 0 }}
          transition={{ duration: 0.2 }}
        >
          <motion.div
            className="p-3 rounded-full bg-muted"
            animate={{ rotate: isDragOver ? 360 : 0 }}
            transition={{ duration: 0.5 }}
          >
            <Upload className="h-8 w-8 text-muted-foreground" />
          </motion.div>
          
          <div className="space-y-2">
            <h3 className="text-lg font-semibold">
              {isDragOver ? 'Drop files here' : 'Upload your resume'}
            </h3>
            <p className="text-sm text-muted-foreground">
              Drag and drop your files here, or click to browse
            </p>
            <p className="text-xs text-muted-foreground">
              Supported formats: {accept} • Max size: {maxSize}MB
            </p>
          </div>
          
          <Button variant="outline" disabled={disabled} onClick={() => fileInputRef.current?.click()} type="button">
            Choose Files
          </Button>
        </motion.div>
      </motion.div>

      <AnimatePresence>
        {files.length > 0 && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="mt-4 space-y-2"
          >
            {files.map((fileStatus, index) => (
              <motion.div
                key={`${fileStatus.file.name}-${index}`}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                className="flex items-center gap-3 p-3 rounded-lg border bg-card"
              >
                <div className="shrink-0">
                  <File className="h-5 w-5 text-muted-foreground" />
                </div>
                
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">
                    {fileStatus.file.name}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {(fileStatus.file.size / (1024 * 1024)).toFixed(2)} MB
                  </p>
                  
                  {fileStatus.status === 'uploading' && typeof fileStatus.progress === 'number' && (
                    <div className="mt-2">
                      <Progress value={fileStatus.progress} className="h-1" />
                    </div>
                  )}
                  
                  {fileStatus.status === 'error' && fileStatus.error && (
                    <p className="text-xs text-destructive mt-1">
                      {fileStatus.error}
                    </p>
                  )}
                </div>
                
                <div className="flex items-center gap-2">
                  {fileStatus.status === 'success' && (
                    <CheckCircle className="h-4 w-4 text-green-500" />
                  )}
                  {fileStatus.status === 'error' && (
                    <AlertCircle className="h-4 w-4 text-destructive" />
                  )}
                  
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => removeFile(index)}
                    className="h-8 w-8 p-0"
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              </motion.div>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default FileUpload;

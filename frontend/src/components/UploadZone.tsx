'use client';

import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileArchive, X, CheckCircle, AlertCircle } from 'lucide-react';
import { DatasetAPI } from '@/services/api';

interface UploadZoneProps {
  onUploadSuccess?: () => void;
}

export default function UploadZone({ onUploadSuccess }: UploadZoneProps) {
  const [uploading, setUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [uploadMessage, setUploadMessage] = useState('');

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (!file) return;

    setUploading(true);
    setUploadStatus('idle');
    setUploadMessage('');

    try {
      await DatasetAPI.uploadDataset(file);
      setUploadStatus('success');
      setUploadMessage('Dataset uploaded successfully!');
      onUploadSuccess?.();
    } catch (error) {
      setUploadStatus('error');
      setUploadMessage(error instanceof Error ? error.message : 'Upload failed');
    } finally {
      setUploading(false);
    }
  }, [onUploadSuccess]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/zip': ['.zip'],
    },
    maxFiles: 1,
    disabled: uploading,
  });

  const resetStatus = () => {
    setUploadStatus('idle');
    setUploadMessage('');
  };

  return (
    <div className="w-full max-w-2xl mx-auto">
      <div
        {...getRootProps()}
        className={`
          relative border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
          ${isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'}
          ${uploading ? 'opacity-50 cursor-not-allowed' : ''}
        `}
      >
        <input {...getInputProps()} />
        
        <div className="space-y-4">
          <div className="flex justify-center">
            {uploading ? (
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
            ) : (
              <FileArchive className="h-12 w-12 text-gray-400" />
            )}
          </div>
          
          <div>
            <h3 className="text-lg font-medium text-gray-900">
              {uploading ? 'Uploading...' : 'Upload Dataset'}
            </h3>
            <p className="text-gray-500 mt-1">
              {isDragActive
                ? 'Drop the ZIP file here'
                : 'Drag and drop a ZIP file here, or click to select'}
            </p>
            <p className="text-sm text-gray-400 mt-2">
              Supports ZIP files containing YOLO format datasets
            </p>
          </div>
        </div>
      </div>

      {/* Status Messages */}
      {uploadStatus !== 'idle' && (
        <div className={`
          mt-4 p-4 rounded-lg flex items-center justify-between
          ${uploadStatus === 'success' ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'}
        `}>
          <div className="flex items-center space-x-2">
            {uploadStatus === 'success' ? (
              <CheckCircle className="h-5 w-5" />
            ) : (
              <AlertCircle className="h-5 w-5" />
            )}
            <span>{uploadMessage}</span>
          </div>
          <button
            onClick={resetStatus}
            className="p-1 hover:bg-gray-200 rounded"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      )}
    </div>
  );
} 
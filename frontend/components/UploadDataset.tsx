'use client';

import { useState, useRef } from 'react';
import { Upload, FileText, X, CheckCircle, AlertCircle, Sparkles } from 'lucide-react';
import { datasetApi } from '@/services/api';
import DataCleaningModal from './DataCleaningModal';

interface Dataset {
  id: number;
  name: string;
  table_name: string;
  columns: string[];
  needs_cleaning?: boolean;
  quality_issues?: string[];
}

interface UploadDatasetProps {
  onUploadComplete: (dataset: Dataset) => void;
  onError: (error: string) => void;
}

export default function UploadDataset({ onUploadComplete, onError }: UploadDatasetProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [description, setDescription] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [uploadedDataset, setUploadedDataset] = useState<Dataset | null>(null);
  const [showCleaningModal, setShowCleaningModal] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile && droppedFile.name.endsWith('.csv')) {
      setFile(droppedFile);
      setUploadStatus('idle');
    } else {
      onError('Please upload a CSV file');
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
      setUploadStatus('idle');
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setIsUploading(true);
    setProgress(0);
    setUploadStatus('idle');

    try {
      const dataset = await datasetApi.upload(
        file,
        description,
        (progress) => setProgress(progress)
      );
      
      setUploadStatus('success');
      setUploadedDataset(dataset);
      
      // If dataset needs cleaning, don't auto-close
      if (dataset.needs_cleaning) {
        // Keep modal open to show cleaning option
      } else {
        // Auto-close after success
        setFile(null);
        setDescription('');
        onUploadComplete(dataset);
        
        setTimeout(() => {
          setUploadStatus('idle');
          setProgress(0);
        }, 3000);
      }
    } catch (error: any) {
      setUploadStatus('error');
      let errorMessage = 'Upload failed';
      const detail = error.response?.data?.detail;

      if (typeof detail === 'string') {
        errorMessage = detail;
      }

      onError(errorMessage);
    } finally {
      setIsUploading(false);
    }
  };

  const handleRemoveFile = () => {
    setFile(null);
    setUploadStatus('idle');
    setUploadedDataset(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <>
      <div className="bg-gray-800 rounded-xl p-4 border border-gray-700">
        <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          <Upload className="w-5 h-5 text-blue-400" />
          Upload Dataset
        </h3>

        {!file ? (
          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
              isDragging
                ? 'border-blue-500 bg-blue-500/10'
                : 'border-gray-600 hover:border-gray-500'
            }`}
          >
            <FileText className="w-10 h-10 mx-auto mb-3 text-gray-500" />
            <p className="text-white mb-1">Drag & drop a CSV file here</p>
            <p className="text-gray-500 text-sm">or click to browse</p>
            <input
              ref={fileInputRef}
              type="file"
              accept=".csv"
              onChange={handleFileSelect}
              className="hidden"
            />
          </div>
        ) : (
          <div className="space-y-4">
            {/* File info */}
            <div className="flex items-center justify-between bg-gray-900 rounded-lg p-3">
              <div className="flex items-center gap-3">
                <FileText className="w-8 h-8 text-green-400" />
                <div>
                  <p className="text-white font-medium">{file.name}</p>
                  <p className="text-gray-500 text-sm">{formatFileSize(file.size)}</p>
                </div>
              </div>
              {!uploadedDataset && (
                <button
                  onClick={handleRemoveFile}
                  className="text-gray-500 hover:text-red-400 transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              )}
            </div>

            {/* Description input */}
            {!uploadedDataset && (
              <div>
                <label className="block text-gray-400 text-sm mb-1">
                  Description (optional)
                </label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="e.g., Q4 2024 sales data..."
                  className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 resize-none"
                  rows={2}
                />
              </div>
            )}

            {/* Progress bar */}
            {isUploading && (
              <div>
                <div className="flex justify-between text-sm text-gray-400 mb-1">
                  <span>Uploading...</span>
                  <span>{progress}%</span>
                </div>
                <div className="bg-gray-900 rounded-full h-2 overflow-hidden">
                  <div
                    className="bg-blue-500 h-full transition-all duration-300"
                    style={{ width: `${progress}%` }}
                  />
                </div>
              </div>
            )}

            {/* Status messages */}
            {uploadStatus === 'success' && uploadedDataset && (
              <>
                <div className="flex items-center gap-2 text-green-400">
                  <CheckCircle className="w-5 h-5" />
                  <span>Dataset uploaded successfully!</span>
                </div>

                {/* Data Quality Warning */}
                {uploadedDataset.needs_cleaning && (
                  <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-4">
                    <div className="flex items-start gap-3">
                      <AlertCircle className="w-5 h-5 text-yellow-400 flex-shrink-0 mt-0.5" />
                      <div className="flex-1">
                        <h4 className="font-medium text-yellow-400 mb-2">
                          Data Quality Issues Detected
                        </h4>
                        <ul className="space-y-1 text-sm text-gray-300 mb-3">
                          {uploadedDataset.quality_issues?.slice(0, 3).map((issue, idx) => (
                            <li key={idx}>• {issue}</li>
                          ))}
                          {(uploadedDataset.quality_issues?.length || 0) > 3 && (
                            <li className="text-gray-500">
                              ...and {uploadedDataset.quality_issues!.length - 3} more issues
                            </li>
                          )}
                        </ul>
                        <button
                          onClick={() => setShowCleaningModal(true)}
                          className="flex items-center gap-2 px-4 py-2 bg-yellow-600 hover:bg-yellow-700 text-white rounded-lg transition-colors w-full justify-center"
                        >
                          <Sparkles className="w-4 h-4" />
                          Clean Dataset
                        </button>
                      </div>
                    </div>
                  </div>
                )}

                <button
                  onClick={handleRemoveFile}
                  className="w-full px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors"
                >
                  Upload Another Dataset
                </button>
              </>
            )}

            {uploadStatus === 'error' && (
              <div className="flex items-center gap-2 text-red-400">
                <AlertCircle className="w-5 h-5" />
                <span>Upload failed. Please try again.</span>
              </div>
            )}

            {/* Upload button */}
            {!uploadedDataset && (
              <button
                onClick={handleUpload}
                disabled={isUploading}
                className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 disabled:opacity-50 text-white font-medium py-2 px-4 rounded-lg transition-colors flex items-center justify-center gap-2"
              >
                {isUploading ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    Uploading...
                  </>
                ) : (
                  <>
                    <Upload className="w-4 h-4" />
                    Upload Dataset
                  </>
                )}
              </button>
            )}
          </div>
        )}
      </div>

      {/* Data Cleaning Modal */}
      {showCleaningModal && uploadedDataset && (
        <DataCleaningModal
          datasetId={uploadedDataset.id}
          datasetName={uploadedDataset.name}
          qualityIssues={uploadedDataset.quality_issues || []}
          onClose={() => {
            setShowCleaningModal(false);
            handleRemoveFile();
            onUploadComplete(uploadedDataset);
          }}
          onCleaned={() => {
            setShowCleaningModal(false);
            handleRemoveFile();
            onUploadComplete(uploadedDataset);
          }}
        />
      )}
    </>
  );
}
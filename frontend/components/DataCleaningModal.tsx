'use client';

import { useState, useEffect } from 'react';
import { X, AlertTriangle, CheckCircle, Download, Eye, Sparkles, Loader2 } from 'lucide-react';
import api from '@/services/api';

interface DataCleaningModalProps {
  datasetId: number;
  datasetName: string;
  qualityIssues: string[];
  onClose: () => void;
  onCleaned: () => void;
}

interface CleaningPreview {
  needs_cleaning: boolean;
  issues: string[];
  original_shape: { rows: number; columns: number };
  estimated_cleaned_shape: { rows: number; columns: number };
  estimated_changes: {
    duplicates_to_remove: number;
    columns_with_missing_data: number;
    outliers_to_fix?: number;
  };
  sample_data_before: any[];
  sample_data_after: any[];
  columns_before: string[];  // ✅ Changed from columns
  columns_after: string[];   // ✅ Added
  cleaning_actions?: string[];
}

export default function DataCleaningModal({
  datasetId,
  datasetName,
  qualityIssues,
  onClose,
  onCleaned,
}: DataCleaningModalProps) {
  const [preview, setPreview] = useState<CleaningPreview | null>(null);
  const [isLoadingPreview, setIsLoadingPreview] = useState(true);
  const [isCleaning, setIsCleaning] = useState(false);
  const [showPreview, setShowPreview] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadPreview();
  }, [datasetId]);

  const loadPreview = async () => {
    setIsLoadingPreview(true);
    setError(null);
    try {
      const response = await api.get(`/api/v1/datasets/${datasetId}/preview-cleaning`);
      console.log('Preview data:', response.data); // Debug log
      setPreview(response.data);
    } catch (error: any) {
      console.error('Failed to load preview:', error);
      setError(error.response?.data?.detail || 'Failed to load preview');
    } finally {
      setIsLoadingPreview(false);
    }
  };

  const handleClean = async () => {
    setIsCleaning(true);
    setError(null);
    try {
      await api.post(`/api/v1/datasets/${datasetId}/clean`);
      onCleaned();
      onClose();
    } catch (error: any) {
      console.error('Failed to clean dataset:', error);
      setError(error.response?.data?.detail || 'Failed to clean dataset');
    } finally {
      setIsCleaning(false);
    }
  };

  const handleDownloadCleaned = async () => {
    try {
      const response = await api.get(`/api/v1/datasets/${datasetId}/download-cleaned`, {
        responseType: 'blob',
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `cleaned_${datasetName}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('Failed to download cleaned dataset:', error);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-800 rounded-xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col border border-gray-700">
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-700 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Sparkles className="w-6 h-6 text-blue-400" />
            <div>
              <h2 className="text-xl font-semibold text-white">Clean Dataset</h2>
              <p className="text-sm text-gray-400">{datasetName}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {error && (
            <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4">
              <p className="text-red-400">{error}</p>
            </div>
          )}

          {isLoadingPreview ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-8 h-8 text-blue-400 animate-spin" />
            </div>
          ) : preview ? (
            <>
              {/* Issues Found */}
              {preview.issues && preview.issues.length > 0 && (
                <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-4">
                  <div className="flex items-start gap-3">
                    <AlertTriangle className="w-5 h-5 text-yellow-400 flex-shrink-0 mt-0.5" />
                    <div className="flex-1">
                      <h3 className="font-medium text-yellow-400 mb-2">
                        Data Quality Issues Detected
                      </h3>
                      <ul className="space-y-1 text-sm text-gray-300">
                        {preview.issues.map((issue, idx) => (
                          <li key={idx}>• {issue}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              )}

              {/* Changes Summary */}
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-gray-900 rounded-lg p-4">
                  <h4 className="text-sm font-medium text-gray-400 mb-2">Original</h4>
                  <div className="space-y-1">
                    <p className="text-2xl font-bold text-white">
                      {preview.original_shape.rows} rows
                    </p>
                    <p className="text-sm text-gray-400">
                      {preview.original_shape.columns} columns
                    </p>
                  </div>
                </div>

                <div className="bg-gray-900 rounded-lg p-4">
                  <h4 className="text-sm font-medium text-gray-400 mb-2">After Cleaning</h4>
                  <div className="space-y-1">
                    <p className="text-2xl font-bold text-green-400">
                      {preview.estimated_cleaned_shape.rows} rows
                    </p>
                    <p className="text-sm text-gray-400">
                      {preview.estimated_cleaned_shape.columns} columns
                    </p>
                  </div>
                </div>
              </div>

              {/* Cleaning Actions */}
              {preview.cleaning_actions && preview.cleaning_actions.length > 0 && (
                <div className="bg-gray-900 rounded-lg p-4">
                  <h4 className="font-medium text-white mb-3">Cleaning Actions to be Performed</h4>
                  <ul className="space-y-2 text-sm text-gray-300">
                    {preview.cleaning_actions.map((action, idx) => (
                      <li key={idx} className="flex items-start gap-2">
                        <CheckCircle className="w-4 h-4 text-green-400 flex-shrink-0 mt-0.5" />
                        <span>{action}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Preview Toggle */}
              <button
                onClick={() => setShowPreview(!showPreview)}
                className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors"
              >
                <Eye className="w-4 h-4" />
                {showPreview ? 'Hide' : 'Show'} Before/After Preview
              </button>

              {/* Data Preview */}
              {showPreview && preview.columns_before && preview.sample_data_before && (
                <div className="space-y-4">
                  {/* Before */}
                  <div className="bg-gray-900 rounded-lg p-4">
                    <h4 className="font-medium text-white mb-3">Before Cleaning</h4>
                    <div className="overflow-x-auto">
                      <table className="w-full text-xs">
                        <thead>
                          <tr className="border-b border-gray-700">
                            {preview.columns_before.slice(0, 5).map((col) => (
                              <th key={col} className="text-left py-2 px-2 text-gray-400">
                                {col}
                              </th>
                            ))}
                          </tr>
                        </thead>
                        <tbody>
                          {preview.sample_data_before.slice(0, 5).map((row, idx) => (
                            <tr key={idx} className="border-b border-gray-800">
                              {preview.columns_before.slice(0, 5).map((col) => (
                                <td key={col} className="py-2 px-2 text-gray-300">
                                  {row[col] !== null && row[col] !== undefined ? 
                                    String(row[col]) : 
                                    <span className="text-red-400">NULL</span>
                                  }
                                </td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>

                  {/* After */}
                  {preview.columns_after && preview.sample_data_after && (
                    <div className="bg-gray-900 rounded-lg p-4">
                      <h4 className="font-medium text-green-400 mb-3">After Cleaning</h4>
                      <div className="overflow-x-auto">
                        <table className="w-full text-xs">
                          <thead>
                            <tr className="border-b border-gray-700">
                              {preview.columns_after.slice(0, 5).map((col) => (
                                <th key={col} className="text-left py-2 px-2 text-gray-400">
                                  {col}
                                </th>
                              ))}
                            </tr>
                          </thead>
                          <tbody>
                            {preview.sample_data_after.slice(0, 5).map((row, idx) => (
                              <tr key={idx} className="border-b border-gray-800">
                                {preview.columns_after.slice(0, 5).map((col) => (
                                  <td key={col} className="py-2 px-2 text-gray-300">
                                    {row[col] !== null && row[col] !== undefined ? 
                                      String(row[col]) : 
                                      <span className="text-yellow-400">FILLED</span>
                                    }
                                  </td>
                                ))}
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </>
          ) : (
            <div className="text-center py-8 text-gray-400">
              No preview available
            </div>
          )}
        </div>

        {/* Footer Actions */}
        <div className="px-6 py-4 border-t border-gray-700 flex items-center justify-end gap-3">
          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-400 hover:text-white transition-colors"
            disabled={isCleaning}
          >
            Cancel
          </button>
          <button
            onClick={handleDownloadCleaned}
            className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors flex items-center gap-2"
            disabled={isCleaning || !preview}
          >
            <Download className="w-4 h-4" />
            Download Preview
          </button>
          <button
            onClick={handleClean}
            disabled={isCleaning || !preview}
            className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isCleaning ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Cleaning...
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                Clean Dataset
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}

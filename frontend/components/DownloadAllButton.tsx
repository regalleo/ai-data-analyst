'use client';

import { useState } from 'react';
import { Download, FileText, Loader2 } from 'lucide-react';
import { downloadDashboardAsPDF, sanitizeFilename } from '@/utils/downloadUtils';

interface DownloadAllButtonProps {
  messageIndex: number;
  datasetName?: string;
}

export default function DownloadAllButton({ messageIndex, datasetName }: DownloadAllButtonProps) {
  const [isDownloading, setIsDownloading] = useState(false);

  const handleDownloadAll = async () => {
    setIsDownloading(true);
    
    try {
      // Find all chart elements in this message
      const messageElement = document.querySelector(`[data-message-index="${messageIndex}"]`);
      if (!messageElement) {
        console.error('Message element not found');
        return;
      }

      const elements: HTMLElement[] = [];
      
      // Get KPI cards
      const kpiElement = messageElement.querySelector('[data-kpi-cards]') as HTMLElement;
      if (kpiElement) elements.push(kpiElement);
      
      // Get chart
      const chartElement = messageElement.querySelector('[data-chart]') as HTMLElement;
      if (chartElement) elements.push(chartElement);
      
      // Get text content
      const textElement = messageElement.querySelector('[data-text-content]') as HTMLElement;
      if (textElement) elements.push(textElement);

      if (elements.length === 0) {
        console.error('No elements to download');
        return;
      }

      const filename = sanitizeFilename(`${datasetName || 'report'}-${Date.now()}`);
      await downloadDashboardAsPDF(elements, filename);
    } catch (error) {
      console.error('Download failed:', error);
    } finally {
      setIsDownloading(false);
    }
  };

  return (
    <button
      onClick={handleDownloadAll}
      disabled={isDownloading}
      className="flex items-center gap-2 px-3 py-1.5 text-xs bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 disabled:opacity-50 text-white rounded-lg transition-colors"
    >
      {isDownloading ? (
        <>
          <Loader2 className="w-3 h-3 animate-spin" />
          Downloading...
        </>
      ) : (
        <>
          <FileText className="w-3 h-3" />
          Download Report
        </>
      )}
    </button>
  );
}
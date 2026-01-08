'use client';

import { useRef, useState } from 'react';
import { Download, FileImage, FileText, Loader2 } from 'lucide-react';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { downloadAsPNG, downloadAsPDF, downloadAsCSV, sanitizeFilename } from '@/utils/downloadUtils';

interface ChartRendererProps {
  chartType: string;
  data: any[];
  columns: string[];
  title?: string;
}

const COLORS = [
  '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6',
  '#ec4899', '#06b6d4', '#84cc16', '#f97316', '#6366f1',
];

export default function ChartRenderer({ chartType, data, columns, title }: ChartRendererProps) {
  const chartRef = useRef<HTMLDivElement>(null);
  const [isDownloading, setIsDownloading] = useState(false);
  const [showDownloadMenu, setShowDownloadMenu] = useState(false);

  if (!data || data.length === 0) {
    return (
      <div className="h-64 flex items-center justify-center bg-gray-900 rounded-lg">
        <p className="text-gray-500">No chart data available</p>
      </div>
    );
  }

  const chartData = data.map((row, index) => ({
    ...row,
    _index: index + 1,
  }));

  const labelKey = columns[0];
  const valueKey = columns[1] || columns[0];
  const chartTitle = title || `${chartType.charAt(0).toUpperCase() + chartType.slice(1)} Chart`;

  const handleDownloadPNG = async () => {
    if (!chartRef.current) return;
    setIsDownloading(true);
    try {
      await downloadAsPNG(chartRef.current, sanitizeFilename(chartTitle));
    } catch (error) {
      console.error('Download failed:', error);
    } finally {
      setIsDownloading(false);
      setShowDownloadMenu(false);
    }
  };

  const handleDownloadPDF = async () => {
    if (!chartRef.current) return;
    setIsDownloading(true);
    try {
      await downloadAsPDF(chartRef.current, sanitizeFilename(chartTitle));
    } catch (error) {
      console.error('Download failed:', error);
    } finally {
      setIsDownloading(false);
      setShowDownloadMenu(false);
    }
  };

  const handleDownloadCSV = () => {
    try {
      downloadAsCSV(data, columns, sanitizeFilename(chartTitle));
    } catch (error) {
      console.error('Download failed:', error);
    } finally {
      setShowDownloadMenu(false);
    }
  };

  const renderChart = () => {
    switch (chartType.toLowerCase()) {
      case 'bar':
        return (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey={labelKey} stroke="#9ca3af" fontSize={12} />
              <YAxis stroke="#9ca3af" fontSize={12} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1f2937',
                  border: '1px solid #374151',
                  borderRadius: '8px',
                }}
                labelStyle={{ color: '#fff' }}
              />
              <Legend />
              <Bar dataKey={valueKey} fill="#3b82f6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        );

      case 'line':
        return (
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey={labelKey} stroke="#9ca3af" fontSize={12} />
              <YAxis stroke="#9ca3af" fontSize={12} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1f2937',
                  border: '1px solid #374151',
                  borderRadius: '8px',
                }}
                labelStyle={{ color: '#fff' }}
              />
              <Legend />
              <Line
                type="monotone"
                dataKey={valueKey}
                stroke="#10b981"
                strokeWidth={2}
                dot={{ fill: '#10b981' }}
              />
            </LineChart>
          </ResponsiveContainer>
        );

      case 'pie':
      case 'doughnut':
        return (
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={chartData}
                dataKey={valueKey}
                nameKey={labelKey}
                cx="50%"
                cy="50%"
                outerRadius={100}
                label={({ name, percent }: { name?: string; percent?: number }) =>
                  `${name || 'Data'}: ${((percent || 0) * 100).toFixed(0)}%`
                }
                labelLine={false}
              >
                {chartData.map((_, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={COLORS[index % COLORS.length]}
                  />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1f2937',
                  border: '1px solid #374151',
                  borderRadius: '8px',
                }}
                labelStyle={{ color: '#fff' }}
              />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        );

      case 'table':
      default:
        return (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-700">
                  {columns.map((col) => (
                    <th
                      key={col}
                      className="text-left py-2 px-3 font-medium text-gray-400"
                    >
                      {col}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {chartData.slice(0, 10).map((row, index) => (
                  <tr
                    key={index}
                    className="border-b border-gray-800 hover:bg-gray-800/50"
                  >
                    {columns.map((col) => (
                      <td key={col} className="py-2 px-3 text-gray-300">
                        {typeof row[col] === 'number'
                          ? row[col].toLocaleString()
                          : String(row[col] || '-')}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
            {chartData.length > 10 && (
              <p className="text-gray-500 text-xs mt-2 text-center">
                Showing 10 of {chartData.length} rows
              </p>
            )}
          </div>
        );
    }
  };

  return (
    <div ref={chartRef} className="bg-gray-900 rounded-lg p-4 relative">
      {/* Header with Download Button */}
      <div className="flex items-center justify-between mb-3">
        <h4 className="text-sm font-medium text-gray-400 capitalize">
          {chartTitle}
        </h4>
        
        {/* Download Menu */}
        <div className="relative">
          <button
            onClick={() => setShowDownloadMenu(!showDownloadMenu)}
            disabled={isDownloading}
            className="flex items-center gap-2 px-3 py-1.5 text-xs bg-gray-800 hover:bg-gray-700 text-gray-300 rounded-lg transition-colors disabled:opacity-50"
          >
            {isDownloading ? (
              <>
                <Loader2 className="w-3 h-3 animate-spin" />
                Downloading...
              </>
            ) : (
              <>
                <Download className="w-3 h-3" />
                Export
              </>
            )}
          </button>

          {/* Download Dropdown */}
          {showDownloadMenu && !isDownloading && (
            <div className="absolute right-0 mt-2 w-48 bg-gray-800 border border-gray-700 rounded-lg shadow-lg z-10">
              <button
                onClick={handleDownloadPNG}
                className="w-full flex items-center gap-2 px-4 py-2 text-sm text-gray-300 hover:bg-gray-700 transition-colors"
              >
                <FileImage className="w-4 h-4" />
                Download as PNG
              </button>
              <button
                onClick={handleDownloadPDF}
                className="w-full flex items-center gap-2 px-4 py-2 text-sm text-gray-300 hover:bg-gray-700 transition-colors"
              >
                <FileText className="w-4 h-4" />
                Download as PDF
              </button>
              <button
                onClick={handleDownloadCSV}
                className="w-full flex items-center gap-2 px-4 py-2 text-sm text-gray-300 hover:bg-gray-700 transition-colors border-t border-gray-700"
              >
                <FileText className="w-4 h-4" />
                Download Data (CSV)
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Chart Content */}
      {renderChart()}
    </div>
  );
}
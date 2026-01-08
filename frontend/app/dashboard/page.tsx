'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';
import { datasetApi, Dataset } from '@/services/api';
import Chat from '@/components/Chat';
import UploadDataset from '@/components/UploadDataset';
import { BarChart3, Database, LogOut, Plus, FileText, Trash2 } from 'lucide-react';

export default function DashboardPage() {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [selectedDataset, setSelectedDataset] = useState<Dataset | null>(null);
  const [activeTab, setActiveTab] = useState<'chat' | 'upload'>('chat');
  const { user, token, logout } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!token) {
      router.push('/login');
    } else {
      fetchDatasets();
    }
  }, [router, token]);

  const fetchDatasets = async () => {
    try {
      const data = await datasetApi.list();
      setDatasets(data);
      if (data.length > 0 && !selectedDataset) {
        setSelectedDataset(data[0]);
      }
    } catch (err) {
      console.error('Failed to fetch datasets:', err);
    }
  };

  const handleDeleteDataset = async (datasetId: number) => {
    if (!confirm('Are you sure you want to delete this dataset?')) return;
    
    try {
      await datasetApi.delete(datasetId);
      setDatasets((prev) => prev.filter((d) => d.id !== datasetId));
      if (selectedDataset?.id === datasetId) {
        setSelectedDataset(null);
      }
    } catch (err) {
      console.error('Failed to delete dataset:', err);
    }
  };

  const handleUploadComplete = (dataset: Dataset) => {
    fetchDatasets();
    setSelectedDataset(dataset);
    setActiveTab('chat');
  };

  if (!token) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      {/* Header */}
      <header className="bg-gray-900 border-b border-gray-800">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <BarChart3 className="w-6 h-6 text-blue-400" />
            <h1 className="text-xl font-bold">AI Data Analyst</h1>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-gray-400">{user?.email || 'User'}</span>
            <button
              onClick={() => {
                logout();
                router.push('/login');
              }}
              className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors"
            >
              <LogOut className="w-4 h-4" />
              Sign out
            </button>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Sidebar - Dataset List */}
          <div className="lg:col-span-1 space-y-4">
            <div className="bg-gray-900 rounded-xl border border-gray-800 p-4">
              <div className="flex items-center justify-between mb-4">
                <h2 className="font-semibold flex items-center gap-2">
                  <Database className="w-4 h-4 text-blue-400" />
                  Datasets
                </h2>
                <button
                  onClick={() => setActiveTab('upload')}
                  className="p-1.5 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors"
                  title="Upload dataset"
                >
                  <Plus className="w-4 h-4" />
                </button>
              </div>

              {datasets.length === 0 ? (
                <p className="text-sm text-gray-500 text-center py-8">
                  No datasets yet. Upload your first CSV file.
                </p>
              ) : (
                <div className="space-y-2">
                  {datasets.map((dataset) => (
                    <div
                      key={dataset.id}
                      onClick={() => {
                        setSelectedDataset(dataset);
                        setActiveTab('chat');
                      }}
                      className={`p-3 rounded-lg cursor-pointer transition-all ${
                        selectedDataset?.id === dataset.id
                          ? 'bg-blue-600/20 border border-blue-500/30'
                          : 'bg-gray-800/50 border border-transparent hover:bg-gray-800'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2 min-w-0">
                          <FileText className="w-4 h-4 text-gray-400 flex-shrink-0" />
                          <div className="min-w-0">
                            <p className="text-sm font-medium truncate">{dataset.name}</p>
                            <p className="text-xs text-gray-500">
                              {dataset.columns?.length || 0} columns
                            </p>
                          </div>
                        </div>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleDeleteDataset(dataset.id);
                          }}
                          className="text-gray-500 hover:text-red-400 p-1 rounded transition-colors"
                          title="Delete dataset"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Upload Panel */}
            {activeTab === 'upload' && (
              <UploadDataset
                onUploadComplete={handleUploadComplete}
                onError={(err) => console.error(err)}
              />
            )}
          </div>

          {/* Main Content - Chat */}
          <div className="lg:col-span-3">
            {selectedDataset ? (
              <div className="h-[calc(100vh-180px)]">
                <Chat
                  datasetId={selectedDataset.id}
                  datasetName={selectedDataset.name}
                />
              </div>
            ) : (
              <div className="h-[calc(100vh-180px)] bg-gray-900 rounded-xl border border-gray-800 flex flex-col items-center justify-center text-center p-8">
                <div className="w-16 h-16 bg-blue-600/20 rounded-full flex items-center justify-center mb-4">
                  <BarChart3 className="w-8 h-8 text-blue-400" />
                </div>
                <h2 className="text-xl font-semibold mb-2">Welcome to AI Data Analyst</h2>
                <p className="text-gray-400 mb-4 max-w-md">
                  Upload a CSV dataset to get started. I can help you analyze your data,
                  generate insights, and create visualizations using natural language.
                </p>
                <button
                  onClick={() => setActiveTab('upload')}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2.5 rounded-lg font-medium transition-colors flex items-center gap-2"
                >
                  <Plus className="w-4 h-4" />
                  Upload Dataset
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}


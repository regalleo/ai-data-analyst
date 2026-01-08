'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { BarChart3, ArrowRight } from 'lucide-react';

export default function HomePage() {
  const router = useRouter();

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      router.push('/dashboard');
    }
  }, [router]);

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      {/* Navigation */}
      <nav className="max-w-7xl mx-auto px-4 py-6 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <BarChart3 className="w-7 h-7 text-blue-400" />
          <h1 className="text-xl font-bold">AI Data Analyst</h1>
        </div>
        <div className="flex items-center gap-4">
          <a
            href="/login"
            className="text-gray-400 hover:text-white transition-colors"
          >
            Sign in
          </a>
          <a
            href="/register"
            className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg font-medium transition-colors"
          >
            Get Started
          </a>
        </div>
      </nav>

      {/* Hero Section */}
      <main className="max-w-7xl mx-auto px-4 py-20 text-center">
        <div className="inline-flex items-center gap-2 bg-blue-600/20 border border-blue-500/30 px-4 py-1.5 rounded-full text-blue-400 text-sm mb-6">
          <span className="w-2 h-2 bg-blue-400 rounded-full animate-pulse" />
          Powered by LangChain + OpenAI
        </div>

        <h2 className="text-5xl md:text-6xl font-bold mb-6 leading-tight">
          Analyze Data with
          <span className="text-blue-400"> AI Power</span>
        </h2>

        <p className="text-xl text-gray-400 max-w-2xl mx-auto mb-10">
          Upload your CSV files and chat with AI to generate insights,
          discover patterns, and create beautiful visualizations instantly.
        </p>

        <div className="flex items-center justify-center gap-4">
          <a
            href="/register"
            className="bg-blue-600 hover:bg-blue-700 px-6 py-3 rounded-lg font-medium text-lg transition-colors flex items-center gap-2"
          >
            Start Free
            <ArrowRight className="w-5 h-5" />
          </a>
          <a
            href="/login"
            className="bg-gray-800 hover:bg-gray-700 px-6 py-3 rounded-lg font-medium text-lg transition-colors"
          >
            Sign In
          </a>
        </div>

        {/* Features */}
        <div className="grid md:grid-cols-3 gap-6 mt-24">
          <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 text-left">
            <div className="w-12 h-12 bg-blue-600/20 rounded-lg flex items-center justify-center mb-4">
              <BarChart3 className="w-6 h-6 text-blue-400" />
            </div>
            <h3 className="text-xl font-semibold mb-2">Smart Charts</h3>
            <p className="text-gray-400">
              AI automatically selects the best chart type for your data and generates
              visualizations on demand.
            </p>
          </div>

          <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 text-left">
            <div className="w-12 h-12 bg-green-600/20 rounded-lg flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold mb-2">Safe SQL</h3>
            <p className="text-gray-400">
              Execute natural language queries on your data with enterprise-grade
              security and user isolation.
            </p>
          </div>

          <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 text-left">
            <div className="w-12 h-12 bg-purple-600/20 rounded-lg flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold mb-2">Hybrid RAG</h3>
            <p className="text-gray-400">
              Combines BM25 keyword search with vector embeddings for accurate,
              context-aware answers.
            </p>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-800 mt-20 py-8">
        <div className="max-w-7xl mx-auto px-4 text-center text-gray-500 text-sm">
          <p>AI Data Analyst - Built with FastAPI, Next.js, and LangChain</p>
        </div>
      </footer>
    </div>
  );
}


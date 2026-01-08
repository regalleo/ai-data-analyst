'use client';

import { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Loader2, BarChart3 } from 'lucide-react';
import { chatApi, ChatMessage } from '@/services/api';
import ChartRenderer from './ChartRenderer';
import KPICards from './KPICards';
import DownloadAllButton from './DownloadAllButton';

interface ChatProps {
  datasetId?: number;
  datasetName?: string;
}

export default function Chat({ datasetId, datasetName }: ChatProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      role: 'user',
      content: input.trim(),
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await chatApi.ask({
        message: input.trim(),
        dataset_id: datasetId,
      });

      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: response.answer,
        chart_type: response.chart_type,
        chart_data: response.chart_data,
        columns: response.columns,
        chart_reason: response.chart_reason,
        kpis: response.kpis,
        filters: response.filters,
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error: any) {
      let errorContent = 'Sorry, I encountered an error. Please try again.';
      const detail = error.response?.data?.detail;

      if (typeof detail === 'string') {
        errorContent = detail;
      }

      const errorMessage: ChatMessage = {
        role: 'assistant',
        content: errorContent,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // Quick action suggestions
  const quickActions = [
    "Show me a dashboard overview",
    "Create a pie chart by vendor",
    "Compare prices across vendors",
    "Show top 5 products",
  ];

  const handleQuickAction = (action: string) => {
    setInput(action);
  };

  return (
    <div className="flex flex-col h-full bg-gray-900 rounded-xl overflow-hidden border border-gray-800">
      {/* Header */}
      <div className="px-4 py-3 bg-gray-800 border-b border-gray-700">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Bot className="w-5 h-5 text-blue-400" />
            <span className="font-medium text-white">
              AI Analyst {datasetName && `- ${datasetName}`}
            </span>
          </div>
          <div className="flex items-center gap-2 text-xs text-gray-400">
            <BarChart3 className="w-4 h-4" />
            
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full">
            <Bot className="w-16 h-16 mb-4 text-blue-400 opacity-50" />
            <p className="text-sm text-gray-400 mb-4">Ask me anything about your data</p>
            
            {/* Quick Actions */}
            <div className="grid grid-cols-2 gap-2 max-w-md">
              {quickActions.map((action, idx) => (
                <button
                  key={idx}
                  onClick={() => handleQuickAction(action)}
                  className="text-xs bg-gray-800 hover:bg-gray-700 text-gray-300 px-3 py-2 rounded-lg transition-colors text-left"
                >
                  {action}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex gap-3 ${
              message.role === 'user' ? 'justify-end' : 'justify-start'
            }`}
          >
            {message.role === 'assistant' && (
              <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center flex-shrink-0">
                <Bot className="w-4 h-4 text-white" />
              </div>
            )}
            
            <div
              className={`max-w-[85%] rounded-lg ${
                message.role === 'user'
                  ? 'bg-blue-600 text-white px-4 py-3'
                  : 'bg-transparent'
              }`}
              data-message-index={index}
            >
              {message.role === 'assistant' && (
                <div className="space-y-4">
                  {/* Download All Button */}
                  {(message.kpis || message.chart_data) && (
                    <div className="flex justify-end mb-2">
                      <DownloadAllButton 
                        messageIndex={index}
                        datasetName={datasetName}
                      />
                    </div>
                  )}
                  
                  {/* KPI Cards */}
                  {message.kpis && message.kpis.length > 0 && (
                    <div data-kpi-cards>
                      <KPICards kpis={message.kpis} />
                    </div>
                  )}
                  
                  {/* Text Answer */}
                  <div className="bg-gray-800 rounded-lg px-4 py-3" data-text-content>
                    <p className="text-sm text-gray-100 whitespace-pre-wrap">
                      {message.content}
                    </p>
                    {message.timestamp && (
                      <p className="text-xs text-gray-500 mt-2">
                        {new Date(message.timestamp).toLocaleTimeString()}
                      </p>
                    )}
                  </div>
                  
                  {/* Chart */}
                  {message.chart_type && message.chart_data && (
                    <div className="space-y-2" data-chart>
                      {message.chart_reason && (
                        <p className="text-xs text-gray-400 px-2">
                          💡 {message.chart_reason}
                        </p>
                      )}
                      <ChartRenderer
                        chartType={message.chart_type}
                        data={message.chart_data}
                        columns={message.columns || []}
                        title={`${datasetName || 'Chart'} - ${message.chart_type}`}
                      />
                    </div>
                  )}
                </div>
              )}
              
              {message.role === 'user' && (
                <>
                  <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                  {message.timestamp && (
                    <p className="text-xs opacity-70 mt-1">
                      {new Date(message.timestamp).toLocaleTimeString()}
                    </p>
                  )}
                </>
              )}
            </div>

            {message.role === 'user' && (
              <div className="w-8 h-8 rounded-full bg-gray-700 flex items-center justify-center flex-shrink-0">
                <User className="w-4 h-4 text-white" />
              </div>
            )}
          </div>
        ))}

        {isLoading && (
          <div className="flex gap-3 justify-start">
            <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center flex-shrink-0">
              <Bot className="w-4 h-4 text-white" />
            </div>
            <div className="bg-gray-800 rounded-lg px-4 py-3">
              <Loader2 className="w-4 h-4 text-blue-400 animate-spin" />
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 bg-gray-800 border-t border-gray-700">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask for dashboards, comparisons, trends..."
            className="flex-1 bg-gray-900 border border-gray-700 rounded-lg px-4 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
            disabled={isLoading}
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 disabled:opacity-50 text-white rounded-lg px-4 py-2 transition-colors"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
}
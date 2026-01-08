import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Types
export interface Dataset {
  id: number;
  name: string;
  table_name: string;
  columns: string[];
  needs_cleaning?: boolean;
  quality_issues?: string[];
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  chart_type?: string;
  chart_data?: any[];
  columns?: string[];
  chart_reason?: string;
  kpis?: KPICard[];
  filters?: Record<string, any[]>;
  timestamp?: string;
}

export interface KPICard {
  title: string;
  value: string;
  change?: string;
  trend?: 'up' | 'down' | 'neutral';
  icon?: string;
}

export interface AskRequest {
  message: string;
  dataset_id?: number;
}

export interface AskResponse {
  answer: string;
  chart_type?: string;
  chart_data?: any[];
  columns?: string[];
  chart_reason?: string;
  kpis?: KPICard[];
  filters?: Record<string, any[]>;
}

export interface ChartResponse {
  chart_type: string;
  data: any[];
  columns: string[];
  title: string;
  x_label?: string;
  y_label?: string;
}

// Auth API
export const authApi = {
  register: async (email: string, password: string) => {
    const response = await api.post('/api/v1/auth/register', { email, password });
    const { access_token } = response.data;
    localStorage.setItem('token', access_token);
    return response.data;
  },

  login: async (email: string, password: string) => {
    const response = await api.post('/api/v1/auth/login', { email, password });
    const { access_token } = response.data;
    localStorage.setItem('token', access_token);
    return response.data;
  },

  logout: () => {
    localStorage.removeItem('token');
  },

  getMe: async () => {
    const response = await api.get('/api/v1/auth/me');
    return response.data;
  },
};

// Dataset API
export const datasetApi = {
  upload: async (
    file: File,
    description?: string,
    onProgress?: (progress: number) => void
  ): Promise<Dataset> => {
    const formData = new FormData();
    formData.append('file', file);
    if (description) {
      formData.append('description', description);
    }

    const response = await api.post('/api/v1/datasets/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (progressEvent.total && onProgress) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(progress);
        }
      },
    });

    return response.data;
  },

  list: async (): Promise<Dataset[]> => {
    const response = await api.get('/api/v1/datasets');
    return response.data;
  },

  delete: async (id: number) => {
    const response = await api.delete(`/api/v1/datasets/${id}`);
    return response.data;
  },
};

// Chat API
export const chatApi = {
  ask: async (request: AskRequest): Promise<AskResponse> => {
    const response = await api.post('/api/v1/chat', request);
    return response.data;
  },

  visualize: async (query: string, datasetId?: number): Promise<ChartResponse> => {
    const response = await api.post('/api/v1/visualize', {
      query,
      dataset_id: datasetId,
    });
    return response.data;
  },
};

export default api;
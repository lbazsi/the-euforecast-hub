/**
 * API Client for EU Forecast Hub Backend
 */

// Determine API base URL based on environment
function getApiBaseUrl(): string {
  // Always check for explicit environment variable first
  if (import.meta.env.VITE_API_BASE_URL) {
    return import.meta.env.VITE_API_BASE_URL;
  }
  
  // In production (Vercel), backend is deployed separately
  // The VITE_API_BASE_URL should be set in Vercel environment variables before build
  if (import.meta.env.PROD) {
    // Fallback: This should not be used in production
    // Log warning to help with debugging
    console.warn(
      'VITE_API_BASE_URL not set in production. ' +
      'Please configure it in Vercel environment variables (Settings → Environment Variables)'
    );
    // Try to infer - this is a last resort and likely won't work
    const host = window.location.host;
    const protocol = window.location.protocol;
    return `${protocol}//${host}/api/v1`;
  }
  
  // Development: default to localhost
  return 'http://localhost:8000/api/v1';
}

const API_BASE_URL = getApiBaseUrl();

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: any;
  };
}

class ApiError extends Error {
  constructor(
    public code: string,
    public message: string,
    public status: number,
    public details?: any
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

async function handleResponse<T>(response: Response): Promise<ApiResponse<T>> {
  const contentType = response.headers.get('content-type');
  const isJson = contentType?.includes('application/json');
  
  if (!response.ok) {
    let errorData: any = {};
    if (isJson) {
      try {
        errorData = await response.json();
      } catch {
        // Fall through
      }
    }
    
    const error = errorData.error || errorData.detail || {};
    throw new ApiError(
      error.code || 'UNKNOWN_ERROR',
      error.message || response.statusText,
      response.status,
      error.details
    );
  }
  
  if (!isJson) {
    return { success: true } as ApiResponse<T>;
  }
  
  const data = await response.json();
  return data;
}

export const api = {
  async get<T = any>(endpoint: string): Promise<T> {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    const result = await handleResponse<T>(response);
    return result.data as T;
  },

  async post<T = any>(endpoint: string, data: any): Promise<T> {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    const result = await handleResponse<T>(response);
    return result.data as T;
  },

  async put<T = any>(endpoint: string, data: any): Promise<T> {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    const result = await handleResponse<T>(response);
    return result.data as T;
  },

  async delete<T = any>(endpoint: string): Promise<T> {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    const result = await handleResponse<T>(response);
    return result.data as T;
  },

  async uploadFile<T = any>(endpoint: string, file: File): Promise<T> {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
      body: formData,
    });
    const result = await handleResponse<T>(response);
    return result.data as T;
  },
};

// DBN-specific API calls
export const dbnApi = {
  async build(spec: any, settings: any = {}) {
    return api.post('/dbn/build', { spec, settings });
  },

  async fit(modelSpecId: string, dataBindings: any = {}, weights: any = {}) {
    return api.post('/dbn/fit', {
      model_spec_id: modelSpecId,
      data_bindings: dataBindings,
      weights,
    });
  },

  async infer(modelVersionId: string, evidence: any = {}, interventions: any = {}) {
    return api.post('/dbn/infer', {
      model_version_id: modelVersionId,
      evidence,
      interventions,
    });
  },
};

// Forecasts-specific API calls
export const forecastsApi = {
  async generate(prompt: string, stageConfigs: any = {}) {
    return api.post('/forecasts/generate', {
      prompt,
      stage_configs: stageConfigs,
    });
  },
};

// Builder-specific API calls
export const builderApi = {
  async createProject(name: string, stageConfigurations: any, messageHistory: any[] = []) {
    return api.post('/builder/projects', {
      name,
      stageConfigurations,
      messageHistory,
    });
  },

  async getProject(projectId: string) {
    return api.get(`/builder/projects/${projectId}`);
  },

  async runBuilder(projectId: string | null, stageConfigurations: any, message: string = '') {
    // Backend expects: { projectId?, stageConfigurations? }
    // Remove 'message' as backend doesn't expect it
    const payload: any = {};
    if (projectId) {
      payload.projectId = projectId;
    }
    if (stageConfigurations && Object.keys(stageConfigurations).length > 0) {
      payload.stageConfigurations = stageConfigurations;
    }
    return api.post('/builder/run', payload);
  },

  async sendMessage(projectId: string | null, message: string, sessionId: string | null = null, stageConfigurations: any = {}) {
    // Backend expects: { message, stageConfigurations, projectId?, sessionId? }
    // stageConfigurations is required
    const payload: any = {
      message,
      stageConfigurations: stageConfigurations || {},
    };
    if (projectId) {
      payload.projectId = projectId;
    }
    if (sessionId) {
      payload.sessionId = sessionId;
    }
    return api.post('/builder/message', payload);
  },
};

export { ApiError };

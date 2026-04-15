import apiClient from './api';

export interface Project {
  id: string;
  name: string;
  description?: string;
  repo_url?: string;
  zip_file?: string | null;
  status: 'uploaded' | 'building_filesystem' | 'filesystem_created' | 'processing_classes' | 'analysing' | 'failed' | 'completed';
  created: string;
  file_structure?: FileStructureItem[];
  [key: string]: any;
}

export interface FileStructureItem {
  name: string;
  path: string;
  type: 'file' | 'directory';
  children?: FileStructureItem[];
}

// Interfaccia per la paginazione standard di DRF
export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export default {
  /**
   * Get list of projects with pagination
   * @param params Query parameters (e.g., { page: 1, search: 'query' })
   */
  getProjects(params: Record<string, any> = {}) {
    return apiClient.get<PaginatedResponse<Project>>('/projects/', { params: { ...params, page_size: 10 } });
  },

  /**
   * Get project details
   * @param id Project ID
   */
  getProject(id: string) {
    return apiClient.get<Project>(`/projects/${id}/`);
  },

  /**
   * Create a new project
   * @param data FormData
   */
  createProject(data: FormData) {
    return apiClient.post<Project>('/projects/', data, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  /**
   * Update project details
   * @param id Project ID
   * @param data Updated data
   */
  updateProject(id: string, data: Partial<Project>) {
    return apiClient.patch<Project>(`/projects/${id}/`, data);
  },

  /**
   * Delete a project
   * @param id Project ID
   */
  deleteProject(id: string) {
    return apiClient.delete(`/projects/${id}/`);
  },

  /**
   * Manually trigger filesystem build
   */
  buildFilesystem(id: string) {
    return apiClient.post(`/projects/${id}/build_filesystem/`);
  },
    /**
   * Get Project by secret token (used for public access)
   */
  getProjectByToken(secretToken: string) {
    return apiClient.get(`/analyses/${secretToken}/project/`);
  },

  runAnalysisByToken(payload: Record<string, any>) {
    return apiClient.post(`/analyses/`, payload);
  },
  /**
   * Ottieni le statistiche dell'analisi (per il polling)
   */
  getAnalysisStats(analysisId: string) {
    return apiClient.get(`/analyses/${analysisId}/stats/`);
  },
  /**
   * Ottieni la lista delle analisi filtrate (es. per project ID)
   */
  getAnalyses(params: Record<string, any> = {}) {
    return apiClient.get(`/analyses/`, { params });
  },
  /**
   * Ottieni la lista dei mutanti generati dall'analisi
   */
  getMutantResults(analysisId: string) {
    return apiClient.get(`/mutation-results/?analysis=${analysisId}`);
  }
};

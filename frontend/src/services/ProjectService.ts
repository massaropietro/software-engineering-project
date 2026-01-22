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

export default {
  /**
   * Get list of projects
   */
  getProjects() {
    return apiClient.get<Project[]>('/projects/');
  },

  /**
   * Get project details
   * @param id Project ID
   */
  getProject(id: string) {
    return apiClient.get<Project>(`/projects/${id}`);
  },

  /**
   * Create a new project (upload zip or provide repo url)
   * @param data FormData containing project details and file/url
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
   * Manually trigger filesystem build (if needed, usually auto via signal)
   * This is just a placeholder example if we added an explicit action endpoint
   */
  buildFilesystem(id: string) {
    return apiClient.post(`/projects/${id}/build_filesystem/`);
  }
};

import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

export interface ProjectCreate {
  name: string;
  description?: string;
  target_domain: string;
  scope_rules?: string[];
}

export interface Project {
  id: number;
  name: string;
  description?: string;
  target_domain: string;
  scope_rules: string[];
  owner_id: number;
  created_at: string;
  updated_at: string;
}

class ProjectService {
  private getAuthHeaders() {
    const token = localStorage.getItem('authToken') || sessionStorage.getItem('authToken') || localStorage.getItem('supabase.auth.token');
    return token ? { Authorization: `Bearer ${token}` } : {};
  }

  async createProject(projectData: ProjectCreate): Promise<Project> {
    try {
      const response = await axios.post(`${API_BASE_URL}/projects`, projectData, {
        headers: {
          'Content-Type': 'application/json',
          ...this.getAuthHeaders()
        }
      });
      return response.data;
    } catch (error) {
      console.error('Failed to create project:', error);
      throw new Error('Failed to create project. Please try again.');
    }
  }

  async getProjects(): Promise<Project[]> {
    try {
      const response = await axios.get(`${API_BASE_URL}/projects`, {
        headers: this.getAuthHeaders()
      });
      return response.data;
    } catch (error) {
      console.error('Failed to fetch projects:', error);
      throw new Error('Failed to fetch projects. Please try again.');
    }
  }

  async getProject(projectId: number): Promise<Project> {
    try {
      const response = await axios.get(`${API_BASE_URL}/projects/${projectId}`, {
        headers: this.getAuthHeaders()
      });
      return response.data;
    } catch (error) {
      console.error('Failed to fetch project:', error);
      throw new Error('Failed to fetch project. Please try again.');
    }
  }

  async updateProject(projectId: number, projectData: Partial<ProjectCreate>): Promise<Project> {
    try {
      const response = await axios.put(`${API_BASE_URL}/projects/${projectId}`, projectData, {
        headers: {
          'Content-Type': 'application/json',
          ...this.getAuthHeaders()
        }
      });
      return response.data;
    } catch (error) {
      console.error('Failed to update project:', error);
      throw new Error('Failed to update project. Please try again.');
    }
  }

  async deleteProject(projectId: number): Promise<void> {
    try {
      await axios.delete(`${API_BASE_URL}/projects/${projectId}`, {
        headers: this.getAuthHeaders()
      });
    } catch (error) {
      console.error('Failed to delete project:', error);
      throw new Error('Failed to delete project. Please try again.');
    }
  }
}

export const projectService = new ProjectService();
export default projectService;
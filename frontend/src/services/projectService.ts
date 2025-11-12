import http from './httpClient.ts';

export interface ProjectCreate {
  name: string;
  description?: string;
  target_domain: string;
  scope_rules?: string[];
}

export interface Project {
  id: string;
  name: string;
  description?: string;
  target_domain: string;
  scope_rules: string[];
  owner_id: string;
  created_at: string;
  updated_at: string;
}

class ProjectService {

  async createProject(projectData: ProjectCreate): Promise<Project> {
    try {
      const response = await http.post(`/projects`, projectData);
      return response.data;
    } catch (error) {
      // Normalize Axios error
      console.error('Failed to create project:', error);
      throw new Error('Failed to create project. Please try again.');
    }
  }

  async getProjects(): Promise<Project[]> {
    try {
      const response = await http.get(`/projects`);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch projects:', error);
      throw new Error('Failed to fetch projects. Please try again.');
    }
  }

  async getProject(projectId: string): Promise<Project> {
    try {
      const response = await http.get(`/projects/${projectId}`);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch project:', error);
      throw new Error('Failed to fetch project. Please try again.');
    }
  }

  async updateProject(projectId: string, projectData: Partial<ProjectCreate>): Promise<Project> {
    try {
      const response = await http.put(`/projects/${projectId}`, projectData);
      return response.data;
    } catch (error) {
      console.error('Failed to update project:', error);
      throw new Error('Failed to update project. Please try again.');
    }
  }

  async deleteProject(projectId: string): Promise<void> {
    try {
      await http.delete(`/projects/${projectId}`);
    } catch (error) {
      console.error('Failed to delete project:', error);
      throw new Error('Failed to delete project. Please try again.');
    }
  }
}

export const projectService = new ProjectService();
export default projectService;
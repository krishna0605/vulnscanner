import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

export interface DashboardMetrics {
  total_projects: number;
  active_scans: number;
  total_vulnerabilities: number;
  scan_completion_rate: number;
  avg_scan_duration: number;
  urls_per_scan: number;
  forms_per_scan: number;
}

export interface ProjectSummary {
  id: string;
  name: string;
  target_domain: string;
  last_scan_date?: string;
  vulnerability_count: {
    critical: number;
    high: number;
    medium: number;
    low: number;
  };
  scan_status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  progress?: number;
}

export interface ScanStatistics {
  total_scans: number;
  active_scans: number;
  completed_scans: number;
  failed_scans: number;
  avg_duration: number;
  success_rate: number;
}

export interface VulnerabilityTrend {
  date: string;
  critical: number;
  high: number;
  medium: number;
  low: number;
}

export interface ActivityItem {
  id: string;
  type: 'scan_completed' | 'scan_started' | 'vulnerability_found' | 'project_created' | 'scan_failed';
  title: string;
  description?: string;
  timestamp: string;
  project_name?: string;
  severity?: 'critical' | 'high' | 'medium' | 'low';
  metadata?: Record<string, any>;
}

class DashboardService {
  private getAuthHeaders() {
    const token = localStorage.getItem('authToken') || sessionStorage.getItem('authToken') || localStorage.getItem('supabase.auth.token');
    return token ? { Authorization: `Bearer ${token}` } : {};
  }

  private async checkBackendHealth(): Promise<boolean> {
    try {
      // Use the public health endpoint that doesn't require authentication
      const response = await axios.get('http://localhost:8000/api/health', {
        timeout: 5000
      });
      return response.status === 200;
    } catch (error) {
      console.warn('Backend health check failed:', error);
      return false;
    }
  }

  async getDashboardOverview(): Promise<{
    metrics: DashboardMetrics;
    projects: ProjectSummary[];
    recent_activity: ActivityItem[];
  }> {
    try {
      // Check if backend is available
      const isBackendHealthy = await this.checkBackendHealth();
      if (!isBackendHealthy) {
        throw new Error('Backend service is unavailable');
      }

      // Use the correct /overview endpoint from backend
      const response = await axios.get(`${API_BASE_URL}/overview`, {
        headers: this.getAuthHeaders(),
        timeout: 10000
      });
      
      // The backend returns the data in the expected format
      return {
        metrics: response.data.metrics,
        projects: response.data.projects || [],
        recent_activity: response.data.recent_activity || []
      };
    } catch (error) {
      console.error('Failed to fetch dashboard overview:', error);
      
      // Return empty state instead of mock data
      return {
        metrics: {
          total_projects: 0,
          active_scans: 0,
          total_vulnerabilities: 0,
          scan_completion_rate: 0,
          avg_scan_duration: 0,
          urls_per_scan: 0,
          forms_per_scan: 0
        },
        projects: [],
        recent_activity: []
      };
    }
  }

  async getScanStatistics(): Promise<ScanStatistics> {
    try {
      const isBackendHealthy = await this.checkBackendHealth();
      if (!isBackendHealthy) {
        throw new Error('Backend service is unavailable');
      }

      const response = await axios.get(`${API_BASE_URL}/dashboard/scan-statistics`, {
        headers: this.getAuthHeaders(),
        timeout: 10000
      });
      return response.data;
    } catch (error) {
      console.error('Failed to fetch scan statistics:', error);
      
      // Return empty state instead of throwing
      return {
        total_scans: 0,
        active_scans: 0,
        completed_scans: 0,
        failed_scans: 0,
        avg_duration: 0,
        success_rate: 0
      };
    }
  }

  async getVulnerabilityTrends(days: number = 30): Promise<VulnerabilityTrend[]> {
    try {
      const isBackendHealthy = await this.checkBackendHealth();
      if (!isBackendHealthy) {
        throw new Error('Backend service is unavailable');
      }

      const response = await axios.get(`${API_BASE_URL}/dashboard/vulnerability-trends`, {
        params: { days },
        headers: this.getAuthHeaders(),
        timeout: 10000
      });
      return response.data;
    } catch (error) {
      console.error('Failed to fetch vulnerability trends:', error);
      
      // Return empty array instead of throwing
      return [];
    }
  }

  async getProjectsSummary(): Promise<ProjectSummary[]> {
    try {
      const isBackendHealthy = await this.checkBackendHealth();
      if (!isBackendHealthy) {
        throw new Error('Backend service is unavailable');
      }

      const response = await axios.get(`${API_BASE_URL}/dashboard/projects-summary`, {
        headers: this.getAuthHeaders(),
        timeout: 10000
      });
      return response.data;
    } catch (error) {
      console.error('Failed to fetch projects summary:', error);
      
      // Return empty array instead of throwing
      return [];
    }
  }

  async getRecentActivity(limit: number = 10): Promise<ActivityItem[]> {
    try {
      const isBackendHealthy = await this.checkBackendHealth();
      if (!isBackendHealthy) {
        throw new Error('Backend service is unavailable');
      }

      const response = await axios.get(`${API_BASE_URL}/dashboard/recent-activity`, {
        params: { limit },
        headers: this.getAuthHeaders(),
        timeout: 10000
      });
      return response.data;
    } catch (error) {
      console.error('Failed to fetch recent activity:', error);
      
      // Return empty array instead of throwing
      return [];
    }
  }

  async getLiveMetrics(): Promise<{
    active_scans: number;
    queue_depth: number;
    system_load: number;
    memory_usage: number;
  }> {
    try {
      const isBackendHealthy = await this.checkBackendHealth();
      if (!isBackendHealthy) {
        throw new Error('Backend service is unavailable');
      }

      const response = await axios.get(`${API_BASE_URL}/dashboard/live-metrics`, {
        headers: this.getAuthHeaders(),
        timeout: 10000
      });
      return response.data;
    } catch (error) {
      console.error('Failed to fetch live metrics:', error);
      
      // Return empty state instead of throwing
      return {
        active_scans: 0,
        queue_depth: 0,
        system_load: 0,
        memory_usage: 0
      };
    }
  }


}

export const dashboardService = new DashboardService();
export default dashboardService;
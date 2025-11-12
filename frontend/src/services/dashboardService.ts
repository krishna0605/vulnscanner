import http from './httpClient.ts';

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

  

  async getDashboardOverview(): Promise<{
    metrics: DashboardMetrics;
    projects: ProjectSummary[];
    recent_activity: ActivityItem[];
  }> {
    try {
      // Use the correct /dashboard/overview endpoint from backend
      const response = await http.get(`/dashboard/overview`, {
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
      const response = await http.get(`/dashboard/scan-statistics`, {
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
      const response = await http.get(`/dashboard/vulnerability-trends`, {
        params: { days },
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
      const response = await http.get(`/dashboard/projects-summary`, {
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
      const response = await http.get(`/dashboard/recent-activity`, {
        params: { limit },
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
      const response = await http.get(`/dashboard/live-metrics`, {
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
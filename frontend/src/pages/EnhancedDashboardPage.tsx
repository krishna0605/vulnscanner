import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext.tsx';
import { useSelector } from 'react-redux';
import { RootState } from '../store/index.ts';
import MetricCard from '../components/dashboard/MetricCard.tsx';
import ActivityFeed, { ActivityItem } from '../components/dashboard/ActivityFeed.tsx';
import ChartContainer from '../components/dashboard/ChartContainer.tsx';
import VulnerabilityTrendsChart from '../components/dashboard/VulnerabilityTrendsChart.tsx';
import ScanMetricsChart from '../components/dashboard/ScanMetricsChart.tsx';
import ProjectDistributionChart from '../components/dashboard/ProjectDistributionChart.tsx';
import dashboardService, { DashboardMetrics, ProjectSummary } from '../services/dashboardService.ts';
import projectService from '../services/projectService.ts';
import '../styles/dashboard.css';
// Removed strict backend health gating to avoid blocking UI on transient aborts

const EnhancedDashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const { user, loading: authLoading } = useAuth();

  const loadProjects = async () => {
    try {
      const projectsData = await projectService.getProjects();
      // Convert Project[] to ProjectSummary[] format for dashboard
      const projectSummaries: ProjectSummary[] = projectsData.map(project => ({
        id: project.id,
        name: project.name,
        target_domain: project.target_domain,
        last_scan_date: project.updated_at,
        vulnerability_count: {
          critical: 0,
          high: 0,
          medium: 0,
          low: 0
        },
        scan_status: 'pending' as const,
        progress: 0
      }));
      setProjects(projectSummaries);
    } catch (error) {
      console.error('Failed to load projects:', error);
      setProjects([]);
    }
  };
  const { isAuthenticated, loading: reduxLoading } = useSelector((state: RootState) => state.auth);
  const [profileOpen, setProfileOpen] = useState(false);
  const profileRef = React.useRef<HTMLDivElement>(null);

  // Dashboard data state
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [projects, setProjects] = useState<ProjectSummary[]>([]);
  const [activities, setActivities] = useState<ActivityItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Chart data state - only real data, no mock data
  const [vulnerabilityTrends, setVulnerabilityTrends] = useState<any[]>([]);
  const [scanMetrics, setScanMetrics] = useState<any[]>([]);
  const [projectDistribution, setProjectDistribution] = useState<any[]>([]);

  // Check for stored authentication tokens as fallback
  const hasStoredAuth = React.useMemo(() => {
    try {
      const token = localStorage.getItem('authToken') || sessionStorage.getItem('authToken');
      const email = localStorage.getItem('authUserEmail') || sessionStorage.getItem('authUserEmail');
      return !!(token && email);
    } catch {
      return false;
    }
  }, []);

  // Refresh projects when component mounts or user returns
  useEffect(() => {
    loadProjects();
  }, []);

  // Create a unified user object that works with both auth methods
  const currentUser = React.useMemo(() => {
    if (user) {
      // Supabase user
      return user;
    } else if (hasStoredAuth) {
      // Backend API user - create a user-like object
      const email = localStorage.getItem('authUserEmail') || sessionStorage.getItem('authUserEmail');
      return {
        id: email, // Use email as ID for backend API auth
        email: email,
        user_metadata: {}
      };
    }
    return null;
  }, [user, hasStoredAuth]);

  // Load initial dashboard data - only real data from backend
  useEffect(() => {
    const loadDashboardData = async () => {
      // Wait for authentication to complete
      const isLoading = authLoading || reduxLoading;
      if (isLoading && !hasStoredAuth) {
        return;
      }

      // Check authentication from multiple sources
      const isUserAuthenticated = user || isAuthenticated || hasStoredAuth;

      // Redirect to login if not authenticated
      if (!isUserAuthenticated || !currentUser) {
        setIsLoading(false);
        navigate('/login');
        return;
      }

      try {
        setIsLoading(true);
        setError(null);
        
        // Validate user session and permissions
        if (!currentUser.id || !currentUser.email) {
          throw new Error('Invalid user session');
        }

        // Load real data from backend API
        try {
          // Proceed without strict health gating; individual calls handle failures gracefully

          // Load dashboard overview data
          const data = await dashboardService.getDashboardOverview();
          setMetrics(data.metrics);
          setProjects(data.projects);
          setActivities(data.recent_activity.map(activity => ({
            ...activity,
            timestamp: new Date(activity.timestamp)
          })));

          // Load chart data
          const [trendsData, scanStatsData, projectsData] = await Promise.all([
            dashboardService.getVulnerabilityTrends(),
            dashboardService.getScanStatistics(),
            dashboardService.getProjectsSummary()
          ]);

          setVulnerabilityTrends(trendsData || []);
          
          // Load projects separately for better control
          await loadProjects();
          
          // Convert scan statistics to chart format
          if (scanStatsData) {
            setScanMetrics([
              { name: 'Total', value: scanStatsData.total_scans, color: '#4A90E2' },
              { name: 'Completed', value: scanStatsData.completed_scans, color: '#00C853' },
              { name: 'Failed', value: scanStatsData.failed_scans, color: '#FF4C4C' },
              { name: 'Active', value: scanStatsData.active_scans, color: '#FFB833' }
            ]);
          }

          // Convert projects data to distribution format
          if (projectsData && projectsData.length > 0) {
            const statusCounts = projectsData.reduce((acc, project) => {
              acc[project.scan_status] = (acc[project.scan_status] || 0) + 1;
              return acc;
            }, {} as Record<string, number>);

            setProjectDistribution([
              { name: 'Completed', value: statusCounts.completed || 0, color: '#00C853' },
              { name: 'Running', value: statusCounts.running || 0, color: '#4A90E2' },
              { name: 'Failed', value: statusCounts.failed || 0, color: '#FF4C4C' },
              { name: 'Pending', value: statusCounts.pending || 0, color: '#FFB833' }
            ]);
          } else {
            setProjectDistribution([]);
          }

        } catch (apiError) {
          console.warn('Dashboard API not available:', apiError);
          // Initialize empty state on API error
          const emptyMetrics: DashboardMetrics = {
            total_projects: 0,
            active_scans: 0,
            total_vulnerabilities: 0,
            scan_completion_rate: 0,
            avg_scan_duration: 0,
            urls_per_scan: 0,
            forms_per_scan: 0
          };

          setMetrics(emptyMetrics);
          setProjects([]);
          setActivities([]);
          setVulnerabilityTrends([]);
          setScanMetrics([]);
          setProjectDistribution([]);
          setError('Dashboard service is currently unavailable. Please try again later.');
        }

      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to load dashboard data';
        setError(errorMessage);
        console.error('Dashboard data loading error:', err);
        // If authentication error, redirect to login
        if (errorMessage.includes('session') || errorMessage.includes('authentication')) {
          navigate('/login');
        }
      } finally {
        setIsLoading(false);
      }
    };

    loadDashboardData();
  }, [user, authLoading, isAuthenticated, reduxLoading, hasStoredAuth, currentUser, navigate]);

  // Handle profile dropdown
  useEffect(() => {
    const onDocMouseDown = (e: MouseEvent) => {
      if (profileRef.current && !profileRef.current.contains(e.target as Node)) {
        setProfileOpen(false);
      }
    };
    document.addEventListener('mousedown', onDocMouseDown);
    return () => document.removeEventListener('mousedown', onDocMouseDown);
  }, []);

  const formatTimeAgo = (date: string) => {
    const now = new Date();
    const scanDate = new Date(date);
    const diffInHours = Math.floor((now.getTime() - scanDate.getTime()) / (1000 * 60 * 60));
    if (diffInHours < 1) return 'Just now';
    if (diffInHours < 24) return `${diffInHours}h ago`;
    return `${Math.floor(diffInHours / 24)}d ago`;
  };

  if (error) {
    return (
      <div className="bg-[#0A0B14] text-[#E0E0E0] font-sans min-h-screen w-full flex items-center justify-center">
        <div className="text-center">
          <span className="material-symbols-outlined text-6xl text-[#FF4C4C] mb-4 block">error</span>
          <h1 className="text-2xl font-bold mb-2">Dashboard Error</h1>
          <p className="text-[#888888] mb-4">{error}</p>
          <button 
            onClick={() => window.location.reload()} 
            className="px-6 py-3 bg-[#4A90E2] text-white rounded-lg font-medium hover:bg-[#4A90E2]/80 transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-[#0A0B14] text-[#E0E0E0] font-sans min-h-screen w-full">
      {/* Background effects */}
      <div className="absolute inset-0 -z-10 h-full w-full bg-transparent bg-[radial-gradient(#1A1A2E_1px,transparent_1px)] [background-size:32px_32px]" />
      <div className="absolute top-0 left-0 -z-10 h-1/2 w-full bg-[radial-gradient(ellipse_80%_80%_at_50%_-20%,rgba(74,144,226,0.3),rgba(255,255,255,0))]" />

      <div className="relative flex min-h-screen w-full overflow-hidden">
        <main className="flex-1 flex flex-col overflow-y-auto">
          {/* Top navbar */}
          <header className="sticky top-0 z-30 w-full border-b border-[#2E2E3F]/50 bg-[#0A0B14]/80 px-4 py-3 backdrop-blur-sm sm:px-6 lg:px-10">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-6">
                <div className="flex items-center gap-3 cursor-pointer" onClick={() => navigate('/dashboard')}>
                  <div className="bg-center bg-no-repeat aspect-square bg-cover rounded-full size-9" style={{
                    backgroundImage: 'url("https://lh3.googleusercontent.com/aida-public/AB6AXuAoGb6izEyw_X-IY8P4G1a15e7o30ltLXJVnqKuWW_bw3qlnzlNNTYrEnkZXhnNLOZHJAuVURDsIy0yKJ7KWbV5ulHg8NFsUL2QIoXSgs3tLTs46S3zXpP3WpI1co60H8nXr7VC9fJbj0cdMT5dL9n4F2bRQo20AdUqCu9h7m8G7YlLEnUZVXjv39K5ticnvVqwC6wCVyIQxyYAJcZ9UhO93dRoTmg_8WKC7IOoAhK-PraBlN-2I9Qr5IK5rlI__qB-QTLv_Fmr4eNx")'
                  }} />
                  <h1 className="text-[#E0E0E0] text-base font-bold leading-normal">VulnScanner</h1>
                </div>
                
                {/* User status indicator */}
                {currentUser && (
                  <div className="flex items-center gap-2">
                    <div className="size-2 rounded-full bg-[#00C853]"></div>
                    <span className="text-xs text-[#888888] hidden sm:block">
                      Authenticated
                    </span>
                  </div>
                )}
              </div>
              {/* Navigation links and search */}
              <nav className="hidden md:flex items-center gap-4">
                <Link to="/dashboard" className="text-[#888888] hover:text-white text-sm font-medium">Dashboard</Link>
                <Link to="/projects" className="text-[#888888] hover:text-white text-sm font-medium">Projects</Link>
                <Link to="/scans" className="text-[#888888] hover:text-white text-sm font-medium">Scans</Link>
                <Link to="/reports" className="text-[#888888] hover:text-white text-sm font-medium">Reports</Link>
                <Link to="/settings" className="text-[#888888] hover:text-white text-sm font-medium">Settings</Link>
                <div className="relative">
                  <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-[#888888]">search</span>
                  <input
                    type="text"
                    placeholder="Search..."
                    className="h-10 w-56 pl-10 pr-3 rounded-lg bg-[#131523] border border-[#2E2E3F] text-sm text-[#E0E0E0] placeholder:text-[#888888] focus:outline-none focus:ring-2 focus:ring-[#00D9FF]/50"
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') {
                        const q = (e.target as HTMLInputElement).value.trim();
                        if (q) navigate(`/search?q=${encodeURIComponent(q)}`);
                      }
                    }}
                  />
                </div>
              </nav>

              <div className="flex items-center gap-4">
                <button className="relative flex cursor-pointer items-center justify-center overflow-hidden rounded-lg h-10 w-10 bg-[#131523]/80 text-[#E0E0E0] hover:text-[#4A90E2] transition-colors">
                  <span className="material-symbols-outlined">notifications</span>
                  <div className="absolute top-1.5 right-1.5 size-2.5 rounded-full bg-[#FF4C4C] border-2 border-[#131523]" />
                </button>
                
                <div ref={profileRef} className="relative flex items-center gap-3 cursor-pointer" onClick={() => setProfileOpen(!profileOpen)}>
                  <div className="bg-center bg-no-repeat aspect-square bg-cover rounded-full size-10" style={{
                    backgroundImage: 'url("https://lh3.googleusercontent.com/aida-public/AB6AXuCdOaINXzXPCl8Y-hFtI2ZnqmHTZKt2zgKT9uHSGm-z3XPbz2KkoxPACXtQpwqHMzoUnl9T4S74vWsmm4LS9qRskXRkAUylHMCkSvQWSQ9YfsHQ8R6H63cd688VgoEbPDvaosSdfujXd-sU7UXHqutC_Hs7Nj7E__VwTfRG7VliMn9e4zxPdndtPe_olK3eRVzUvpUQxPgE8Fvcv3IOoXWlvZAz_s_G3MlS9elim3BLzT-xI7wx_tZbYQT6hmkCvAi1ic918YIy--0Q")'
                  }} />
                  <div className="text-right hidden sm:block">
                    <p className="text-[#E0E0E0] text-sm font-medium">Alex Drake</p>
                    <p className="text-[#888888] text-xs">Admin</p>
                  </div>
                  
                  {profileOpen && (
                    <div className="absolute right-0 top-full mt-2 w-44 rounded-lg border border-[#2E2E3F]/60 bg-[#131523]/95 backdrop-blur-sm shadow-2xl shadow-black/50 p-1">
                      <button className="flex items-center gap-2 w-full px-3 py-2 text-sm text-[#E0E0E0] hover:bg-[#2E2E3F] rounded" onClick={() => { setProfileOpen(false); navigate('/profile'); }}>
                        <span className="material-symbols-outlined text-base">person</span>
                        Profile
                      </button>
                      <button className="flex items-center gap-2 w-full px-3 py-2 text-sm text-[#E0E0E0] hover:bg-[#2E2E3F] rounded" onClick={() => setProfileOpen(false)}>
                        <span className="material-symbols-outlined text-base">settings</span>
                        Settings
                      </button>
                      <button className="flex items-center gap-2 w-full px-3 py-2 text-sm text-[#FF4C4C] hover:bg-[#2E2E3F] rounded" onClick={() => setProfileOpen(false)}>
                        <span className="material-symbols-outlined text-base">logout</span>
                        Logout
                      </button>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </header>

          {/* Content */}
          <div className="flex-1 p-6 md:p-8 lg:p-10 space-y-8">
            {/* Title and actions */}
            <div className="flex flex-wrap justify-between items-start gap-4">
              <div className="flex flex-col gap-2">
                <h1 className="text-3xl font-bold leading-tight">Enhanced Dashboard</h1>
                <p className="text-[#888888] text-base">Real-time security monitoring and vulnerability tracking</p>
              </div>
              <div className="flex gap-3">
                <button 
                  onClick={() => navigate('/scans/new')} 
                  className="relative group flex min-w-[84px] cursor-pointer items-center justify-center overflow-hidden rounded-lg h-10 px-4 bg-[#4A90E2] text-white text-sm font-bold gap-2 transition-all duration-300 hover:shadow-[0_0_20px_0px_#4a90e280]"
                >
                  <span className="material-symbols-outlined transition-transform duration-300 group-hover:rotate-90">add</span>
                  <span className="truncate">New Scan</span>
                </button>
                <button 
                  onClick={() => navigate('/projects/new')} 
                  className="flex min-w-[84px] cursor-pointer items-center justify-center overflow-hidden rounded-lg h-10 px-4 bg-[#131523] text-[#E0E0E0] text-sm font-bold border border-[#2E2E3F] hover:bg-[#2E2E3F] hover:text-white transition-colors"
                >
                  <span className="truncate">New Project</span>
                </button>
              </div>
            </div>

            {/* Enhanced Metrics */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
              <MetricCard
                title="Total Projects"
                value={metrics?.total_projects || 0}
                icon="folder"
                color="info"
                isLoading={isLoading}
                animated
                onClick={() => navigate('/projects')}
              />
              <MetricCard
                title="Active Scans"
                value={metrics?.active_scans || 0}
                icon="radar"
                color="primary"
                isLoading={isLoading}
                animated
                trend={{ value: 12, isPositive: true }}
              />
              <MetricCard
                title="Vulnerabilities"
                value={metrics?.total_vulnerabilities || 0}
                icon="warning"
                color="error"
                isLoading={isLoading}
                animated
                trend={{ value: 5, isPositive: false }}
              />
              <MetricCard
                title="Success Rate"
                value={metrics ? `${metrics.scan_completion_rate.toFixed(1)}%` : '0%'}
                icon="check_circle"
                color="success"
                isLoading={isLoading}
                animated
                trend={{ value: 2, isPositive: true }}
              />
            </div>

            {/* Charts and Analytics */}
            <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-8">
              <ChartContainer
                title="Vulnerability Trends"
                subtitle="Last 7 days"
                isLoading={isLoading}
                height={300}
                actions={
                  <button className="text-[#4A90E2] text-sm font-medium hover:text-[#4A90E2]/80">
                    View Details
                  </button>
                }
              >
                <VulnerabilityTrendsChart
                  data={vulnerabilityTrends}
                  loading={isLoading}
                  height={260}
                />
              </ChartContainer>

              <ChartContainer
                title="Scan Metrics"
                subtitle="Completion status overview"
                isLoading={isLoading}
                height={300}
              >
                <ScanMetricsChart
                  data={scanMetrics}
                  loading={isLoading}
                  height={260}
                />
              </ChartContainer>

              <ChartContainer
                title="Project Distribution"
                subtitle="Status breakdown"
                isLoading={isLoading}
                height={300}
              >
                <ProjectDistributionChart
                  data={projectDistribution}
                  loading={isLoading}
                  height={260}
                />
              </ChartContainer>
            </div>

            {/* Projects and Activity */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              {/* Enhanced Projects list */}
              <div className="lg:col-span-2 space-y-6">
                <div className="flex justify-between items-center">
                  <h2 className="text-xl font-bold">Active Projects</h2>
                  <button 
                    onClick={() => navigate('/projects')}
                    className="text-[#4A90E2] text-sm font-medium hover:text-[#4A90E2]/80"
                  >
                    View All
                  </button>
                </div>
                
                <div className="space-y-4">
                  {isLoading ? (
                    [...Array(3)].map((_, index) => (
                      <div key={index} className="animate-pulse p-4 rounded-lg bg-[#131523]/80 border border-[#2E2E3F]/60">
                        <div className="flex justify-between items-start">
                          <div className="space-y-2 flex-1">
                            <div className="h-4 bg-[#2E2E3F] rounded w-1/3"></div>
                            <div className="h-3 bg-[#2E2E3F] rounded w-1/2"></div>
                          </div>
                          <div className="h-6 w-20 bg-[#2E2E3F] rounded"></div>
                        </div>
                      </div>
                    ))
                  ) : projects.length > 0 ? (
                    projects.map((project) => (
                      <div 
                        key={project.id}
                        onClick={() => navigate(`/projects/${project.id}`)}
                        className="group flex flex-col sm:flex-row sm:items-center gap-4 p-4 rounded-lg bg-[#131523]/80 border border-[#2E2E3F]/60 backdrop-blur-sm hover:border-[#4A90E2] transition-all cursor-pointer"
                      >
                        <div className="flex-1">
                          <p className="font-semibold">{project.name}</p>
                          <p className="text-[#888888] text-sm">{project.target_domain}</p>
                        </div>
                        
                        <div className="flex-1 flex flex-col sm:items-center">
                          <p className="text-[#888888] text-sm">Last Scan</p>
                          <p className="font-medium">
                            {project.last_scan_date ? formatTimeAgo(project.last_scan_date) : 'Never'}
                          </p>
                        </div>
                        
                        <div className="flex-1 flex flex-col sm:items-center">
                          <p className="text-[#888888] text-sm">Vulnerabilities</p>
                          <div className="flex items-center gap-3">
                            <div className="flex items-center gap-1.5">
                              <span className="size-2 rounded-full bg-[#FF4C4C]"></span>
                              <span className="text-[#FF4C4C] font-bold text-sm">{project.vulnerability_count.critical}</span>
                            </div>
                            <div className="flex items-center gap-1.5">
                              <span className="size-2 rounded-full bg-[#FFB833]"></span>
                              <span className="text-[#FFB833] font-bold text-sm">{project.vulnerability_count.high}</span>
                            </div>
                            <div className="flex items-center gap-1.5">
                              <span className="size-2 rounded-full bg-[#888888]"></span>
                              <span className="text-[#888888] font-bold text-sm">{project.vulnerability_count.medium}</span>
                            </div>
                          </div>
                        </div>
                        
                        <div className="flex-1 flex sm:justify-end">
                          <div className="flex items-center gap-2">
                            <div className={`size-2 rounded-full ${
                              project.scan_status === 'completed' ? 'bg-[#00C853]' :
                              project.scan_status === 'running' ? 'bg-[#FFB833]' :
                              project.scan_status === 'failed' ? 'bg-[#FF4C4C]' :
                              'bg-[#888888]'
                            }`}></div>
                            <span className="text-xs font-medium capitalize">
                              {project.scan_status}
                            </span>
                            {project.progress && (
                              <span className="text-xs text-[#888888]">
                                ({project.progress}%)
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                    ))
                  ) : (
                    // Empty state for projects
                    <div className="text-center py-12 px-6 rounded-lg bg-[#131523]/80 border border-[#2E2E3F]/60 backdrop-blur-sm">
                      <span className="material-symbols-outlined text-6xl text-[#888888] mb-4 block">folder_open</span>
                      <h3 className="text-lg font-semibold mb-2">No Projects Yet</h3>
                      <p className="text-[#888888] mb-6">Create your first project to start scanning for vulnerabilities</p>
                      <button 
                        onClick={() => navigate('/projects/new')}
                        className="inline-flex items-center gap-2 px-6 py-3 bg-[#4A90E2] text-white rounded-lg font-medium hover:bg-[#4A90E2]/80 transition-colors"
                      >
                        <span className="material-symbols-outlined">add</span>
                        Create Project
                      </button>
                    </div>
                  )}
                </div>
              </div>

              {/* Enhanced Activity Feed */}
              <div className="space-y-6">
                <div className="flex justify-between items-center">
                  <h2 className="text-xl font-bold">Live Activity</h2>
                  <button className="text-[#4A90E2] text-sm font-medium hover:text-[#4A90E2]/80">
                    View All
                  </button>
                </div>
                
                {isLoading ? (
                  <div className="space-y-3">
                    {[...Array(5)].map((_, index) => (
                      <div key={index} className="animate-pulse p-3 rounded-lg bg-[#131523]/80 border border-[#2E2E3F]/60">
                        <div className="flex items-center gap-3">
                          <div className="size-8 bg-[#2E2E3F] rounded-full"></div>
                          <div className="flex-1 space-y-1">
                            <div className="h-3 bg-[#2E2E3F] rounded w-3/4"></div>
                            <div className="h-2 bg-[#2E2E3F] rounded w-1/2"></div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : activities.length > 0 ? (
                  <ActivityFeed
                    activities={activities}
                    maxItems={8}
                    isLoading={false}
                    onItemClick={(activity) => {
                      // Check if activity has project_id (from backend) or metadata with project_id
                      const projectId = (activity as any).project_id || activity.metadata?.project_id;
                      if (projectId) {
                        // Navigate to project details page
                        navigate(`/projects/${projectId}`);
                      } else if (activity.projectName || (activity as any).project_name) {
                        // Fallback: navigate to projects list if no specific project ID
                        navigate('/projects');
                      }
                    }}
                  />
                ) : (
                  // Empty state for activity
                  <div className="text-center py-12 px-6 rounded-lg bg-[#131523]/80 border border-[#2E2E3F]/60 backdrop-blur-sm">
                    <span className="material-symbols-outlined text-6xl text-[#888888] mb-4 block">timeline</span>
                    <h3 className="text-lg font-semibold mb-2">No Activity Yet</h3>
                    <p className="text-[#888888] mb-6">Activity will appear here when you start scanning projects</p>
                    <button 
                      onClick={() => navigate('/scans/new')}
                      className="inline-flex items-center gap-2 px-6 py-3 bg-[#4A90E2] text-white rounded-lg font-medium hover:bg-[#4A90E2]/80 transition-colors"
                    >
                      <span className="material-symbols-outlined">radar</span>
                      Start Scan
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default EnhancedDashboardPage;
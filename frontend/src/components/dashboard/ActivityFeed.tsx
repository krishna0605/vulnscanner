import React from 'react';


export interface ActivityItem {
  id: string;
  type: 'scan_completed' | 'scan_started' | 'vulnerability_found' | 'project_created' | 'scan_failed';
  title: string;
  description?: string;
  timestamp: Date;
  projectName?: string;
  severity?: 'critical' | 'high' | 'medium' | 'low';
  metadata?: Record<string, any>;
}

interface ActivityFeedProps {
  activities: ActivityItem[];
  maxItems?: number;
  showTimestamps?: boolean;
  isLoading?: boolean;
  onItemClick?: (activity: ActivityItem) => void;
  className?: string;
}

const ActivityFeed: React.FC<ActivityFeedProps> = ({
  activities,
  maxItems = 10,
  showTimestamps = true,
  isLoading = false,
  onItemClick,
  className = ''
}) => {
  const getActivityIcon = (type: ActivityItem['type']) => {
    switch (type) {
      case 'scan_completed':
        return { icon: 'check_circle', color: 'success' as const };
      case 'scan_started':
        return { icon: 'radar', color: 'primary' as const };
      case 'vulnerability_found':
        return { icon: 'warning', color: 'error' as const };
      case 'project_created':
        return { icon: 'folder_open', color: 'info' as const };
      case 'scan_failed':
        return { icon: 'error', color: 'error' as const };
      default:
        return { icon: 'info', color: 'info' as const };
    }
  };

  const getSeverityColor = (severity?: string) => {
    switch (severity) {
      case 'critical':
        return 'text-[#FF4C4C] font-bold';
      case 'high':
        return 'text-[#FFB833] font-bold';
      case 'medium':
        return 'text-[#4A90E2] font-bold';
      case 'low':
        return 'text-[#888888] font-bold';
      default:
        return 'text-[#4A90E2] font-bold';
    }
  };

  const formatTimeAgo = (date: Date) => {
    const now = new Date();
    const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);
    
    if (diffInSeconds < 60) return 'Just now';
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
    return `${Math.floor(diffInSeconds / 86400)}d ago`;
  };

  const displayedActivities = activities.slice(0, maxItems);

  if (isLoading) {
    return (
      <div className={`space-y-4 ${className}`}>
        {[...Array(5)].map((_, index) => (
          <div key={index} className="flex items-start gap-4 animate-pulse">
            <div className="flex-shrink-0 mt-1 size-9 rounded-full bg-[#2E2E3F]"></div>
            <div className="flex-1 space-y-2">
              <div className="h-4 bg-[#2E2E3F] rounded w-3/4"></div>
              <div className="h-3 bg-[#2E2E3F] rounded w-1/2"></div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (displayedActivities.length === 0) {
    return (
      <div className={`text-center py-8 ${className}`}>
        <span className="material-symbols-outlined text-4xl text-[#888888] mb-2 block">
          history
        </span>
        <p className="text-[#888888] text-sm">No recent activity</p>
      </div>
    );
  }

  return (
    <ul className={`relative space-y-6 activity-timeline ${className}`}>
      {displayedActivities.map((activity, index) => {
        const { color } = getActivityIcon(activity.type);
        
        return (
          <li 
            key={activity.id}
            className={`
              flex items-start gap-4 activity-item transition-all duration-200
              ${onItemClick ? 'cursor-pointer hover:bg-[#131523]/50 hover:rounded-lg hover:p-2 hover:-m-2' : ''}
            `}
            onClick={() => onItemClick?.(activity)}
          >
            {/* Timeline dot */}
            <div className={`
              activity-dot flex-shrink-0 mt-1 flex items-center justify-center 
              size-9 rounded-full bg-[#131523] border relative
              ${color === 'success' ? 'border-[#00C853]/50' : ''}
              ${color === 'primary' ? 'border-[#4A90E2]/50' : ''}
              ${color === 'error' ? 'border-[#FF4C4C]/50' : ''}
              ${color === 'info' ? 'border-[#888888]/50' : ''}
            `}>
              <span className={`
                size-2 rounded-full
                ${color === 'success' ? 'bg-[#00C853] animate-pulseGlow' : ''}
                ${color === 'primary' ? 'bg-[#4A90E2]' : ''}
                ${color === 'error' ? 'bg-[#FF4C4C]' : ''}
                ${color === 'info' ? 'bg-[#888888]' : ''}
              `}></span>
            </div>
            
            {/* Content */}
            <div className="flex-1 min-w-0">
              <div className="flex items-start justify-between gap-2">
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-[#E0E0E0] leading-relaxed">
                    {activity.title}
                    {activity.projectName && (
                      <span className="font-bold text-[#4A90E2]/90 ml-1">
                        {activity.projectName}
                      </span>
                    )}
                    {activity.severity && (
                      <span className={`ml-1 ${getSeverityColor(activity.severity)}`}>
                        {activity.severity.charAt(0).toUpperCase() + activity.severity.slice(1)}
                      </span>
                    )}
                  </p>
                  {activity.description && (
                    <p className="text-xs text-[#888888] mt-1 leading-relaxed">
                      {activity.description}
                    </p>
                  )}
                </div>
                
                {showTimestamps && (
                  <span className="text-[#888888] text-xs whitespace-nowrap">
                    {formatTimeAgo(activity.timestamp)}
                  </span>
                )}
              </div>
            </div>
          </li>
        );
      })}
      
      {activities.length > maxItems && (
        <li className="flex items-center justify-center pt-4">
          <button className="text-[#4A90E2] text-sm font-medium hover:text-[#4A90E2]/80 transition-colors">
            View all activity ({activities.length - maxItems} more)
          </button>
        </li>
      )}
    </ul>
  );
};

export default ActivityFeed;
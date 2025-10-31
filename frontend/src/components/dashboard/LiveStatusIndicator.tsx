import React from 'react';

export type ScanStatus = 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';

interface LiveStatusIndicatorProps {
  status: ScanStatus;
  label?: string;
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
  animated?: boolean;
  progress?: number; // 0-100 for running scans
}

const LiveStatusIndicator: React.FC<LiveStatusIndicatorProps> = ({
  status,
  label,
  size = 'md',
  showLabel = true,
  animated = true,
  progress
}) => {
  const statusConfig = {
    pending: {
      color: 'bg-[#888888]',
      textColor: 'text-[#888888]',
      ringColor: 'ring-[#888888]/30',
      bgColor: 'bg-[#888888]/10',
      icon: 'schedule',
      label: 'Pending',
      animation: ''
    },
    running: {
      color: 'bg-[#4A90E2]',
      textColor: 'text-[#4A90E2]',
      ringColor: 'ring-[#4A90E2]/30',
      bgColor: 'bg-[#4A90E2]/10',
      icon: 'radar',
      label: 'Running',
      animation: animated ? 'animate-pulse' : ''
    },
    completed: {
      color: 'bg-[#00C853]',
      textColor: 'text-[#00C853]',
      ringColor: 'ring-[#00C853]/30',
      bgColor: 'bg-[#00C853]/10',
      icon: 'check_circle',
      label: 'Completed',
      animation: ''
    },
    failed: {
      color: 'bg-[#FF4C4C]',
      textColor: 'text-[#FF4C4C]',
      ringColor: 'ring-[#FF4C4C]/30',
      bgColor: 'bg-[#FF4C4C]/10',
      icon: 'error',
      label: 'Failed',
      animation: ''
    },
    cancelled: {
      color: 'bg-[#FFB833]',
      textColor: 'text-[#FFB833]',
      ringColor: 'ring-[#FFB833]/30',
      bgColor: 'bg-[#FFB833]/10',
      icon: 'cancel',
      label: 'Cancelled',
      animation: ''
    }
  };

  const sizeConfig = {
    sm: {
      dot: 'size-2',
      container: 'size-6',
      text: 'text-xs',
      icon: 'text-sm'
    },
    md: {
      dot: 'size-2',
      container: 'size-9',
      text: 'text-sm',
      icon: 'text-base'
    },
    lg: {
      dot: 'size-3',
      container: 'size-12',
      text: 'text-base',
      icon: 'text-lg'
    }
  };

  const config = statusConfig[status];
  const sizeClass = sizeConfig[size];
  const displayLabel = label || config.label;

  return (
    <div className="flex items-center gap-2">
      <div className={`
        flex-shrink-0 flex items-center justify-center 
        ${sizeClass.container} rounded-full 
        bg-[#131523] border ${config.ringColor} relative
      `}>
        {status === 'running' && progress !== undefined ? (
          <>
            {/* Progress ring */}
            <svg className="absolute inset-0 w-full h-full -rotate-90" viewBox="0 0 36 36">
              <path
                className="stroke-current text-[#2E2E3F]"
                strokeWidth="3"
                fill="none"
                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
              />
              <path
                className={`stroke-current ${config.textColor} transition-all duration-300`}
                strokeWidth="3"
                strokeLinecap="round"
                fill="none"
                strokeDasharray={`${progress}, 100`}
                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
              />
            </svg>
            <span className={`material-symbols-outlined ${sizeClass.icon} ${config.textColor} ${config.animation}`}>
              {config.icon}
            </span>
          </>
        ) : (
          <span className={`${sizeClass.dot} rounded-full ${config.color} ${config.animation}`}></span>
        )}
      </div>
      
      {showLabel && (
        <span className={`
          inline-flex items-center gap-2 px-3 py-1 
          ${sizeClass.text} font-medium rounded-full 
          ${config.bgColor} ${config.textColor} 
          ring-1 ring-inset ${config.ringColor}
        `}>
          {status === 'running' && progress !== undefined && (
            <span className="text-xs opacity-75">{progress}%</span>
          )}
          {displayLabel}
        </span>
      )}
    </div>
  );
};

export default LiveStatusIndicator;
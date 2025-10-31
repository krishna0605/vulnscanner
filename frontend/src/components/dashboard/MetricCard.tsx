import React from 'react';

interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: string;
  color?: 'primary' | 'success' | 'warning' | 'error' | 'info';
  isLoading?: boolean;
  trend?: {
    value: number;
    isPositive: boolean;
  };
  animated?: boolean;
  onClick?: () => void;
}

const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  subtitle,
  icon,
  color = 'primary',
  isLoading = false,
  trend,
  animated = false,
  onClick
}) => {
  const colorClasses = {
    primary: {
      text: 'text-[#4A90E2]',
      bg: 'bg-[#4A90E2]/20',
      border: 'border-[#4A90E2]/30',
      glow: 'shadow-[0_0_20px_0px_#4a90e280]'
    },
    success: {
      text: 'text-[#00C853]',
      bg: 'bg-[#00C853]/20',
      border: 'border-[#00C853]/30',
      glow: 'shadow-[0_0_20px_0px_#00c85380]'
    },
    warning: {
      text: 'text-[#FFB833]',
      bg: 'bg-[#FFB833]/20',
      border: 'border-[#FFB833]/30',
      glow: 'shadow-[0_0_20px_0px_#ffb83380]'
    },
    error: {
      text: 'text-[#FF4C4C]',
      bg: 'bg-[#FF4C4C]/20',
      border: 'border-[#FF4C4C]/30',
      glow: 'shadow-[0_0_20px_0px_#ff4c4c80]'
    },
    info: {
      text: 'text-[#E0E0E0]',
      bg: 'bg-[#131523]/80',
      border: 'border-[#2E2E3F]/60',
      glow: 'shadow-[0_0_10px_0px_#2e2e3f40]'
    }
  };

  const currentColor = colorClasses[color];

  if (isLoading) {
    return (
      <div className={`flex flex-col gap-2 rounded-xl p-6 ${currentColor.bg} border ${currentColor.border} backdrop-blur-sm animate-pulse`}>
        <div className="h-4 bg-[#2E2E3F] rounded w-3/4"></div>
        <div className="h-8 bg-[#2E2E3F] rounded w-1/2"></div>
        {subtitle && <div className="h-3 bg-[#2E2E3F] rounded w-2/3"></div>}
      </div>
    );
  }

  return (
    <div 
      className={`
        flex flex-col gap-2 rounded-xl p-6 
        ${currentColor.bg} border ${currentColor.border} backdrop-blur-sm
        transition-all duration-300 hover:${currentColor.glow}
        ${onClick ? 'cursor-pointer hover:scale-105' : ''}
        ${animated ? 'animate-fadeInUp' : ''}
      `}
      onClick={onClick}
    >
      <div className="flex items-center justify-between">
        <p className="text-[#888888] text-sm font-medium">{title}</p>
        {icon && (
          <span className={`material-symbols-outlined text-lg ${currentColor.text}`}>
            {icon}
          </span>
        )}
      </div>
      
      <div className="flex items-baseline gap-2">
        <p className={`tracking-tight text-4xl font-bold ${currentColor.text}`}>
          {value}
        </p>
        {trend && (
          <div className={`flex items-center gap-1 text-sm font-medium ${
            trend.isPositive ? 'text-[#00C853]' : 'text-[#FF4C4C]'
          }`}>
            <span className="material-symbols-outlined text-sm">
              {trend.isPositive ? 'trending_up' : 'trending_down'}
            </span>
            <span>{Math.abs(trend.value)}%</span>
          </div>
        )}
      </div>
      
      {subtitle && (
        <p className="text-[#888888] text-xs">{subtitle}</p>
      )}
    </div>
  );
};

export default MetricCard;
import React from 'react';

interface ChartContainerProps {
  title: string;
  subtitle?: string;
  children: React.ReactNode;
  isLoading?: boolean;
  error?: string;
  height?: number;
  actions?: React.ReactNode;
  className?: string;
  fullWidth?: boolean;
}

const ChartContainer: React.FC<ChartContainerProps> = ({
  title,
  subtitle,
  children,
  isLoading = false,
  error,
  height = 300,
  actions,
  className = '',
  fullWidth = false
}) => {
  if (error) {
    return (
      <div className={`
        rounded-xl p-6 bg-[#131523]/80 border border-[#2E2E3F]/60 backdrop-blur-sm
        ${fullWidth ? 'w-full' : ''}
        ${className}
      `}>
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-lg font-semibold text-[#E0E0E0]">{title}</h3>
            {subtitle && <p className="text-sm text-[#888888] mt-1">{subtitle}</p>}
          </div>
          {actions}
        </div>
        
        <div className="flex flex-col items-center justify-center py-12 text-center">
          <span className="material-symbols-outlined text-4xl text-[#FF4C4C] mb-3">
            error
          </span>
          <p className="text-[#FF4C4C] font-medium mb-2">Failed to load chart</p>
          <p className="text-[#888888] text-sm">{error}</p>
          <button className="mt-4 px-4 py-2 bg-[#4A90E2] text-white rounded-lg text-sm font-medium hover:bg-[#4A90E2]/80 transition-colors">
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className={`
      rounded-xl p-6 bg-[#131523]/80 border border-[#2E2E3F]/60 backdrop-blur-sm
      ${fullWidth ? 'w-full' : ''}
      ${className}
    `}>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-[#E0E0E0]">{title}</h3>
          {subtitle && <p className="text-sm text-[#888888] mt-1">{subtitle}</p>}
        </div>
        {actions}
      </div>
      
      {/* Chart Content */}
      <div className="relative" style={{ height: `${height}px` }}>
        {isLoading ? (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="flex flex-col items-center gap-4">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#4A90E2]"></div>
              <p className="text-[#888888] text-sm">Loading chart data...</p>
            </div>
          </div>
        ) : (
          <div className="w-full h-full">
            {children}
          </div>
        )}
      </div>
    </div>
  );
};

export default ChartContainer;
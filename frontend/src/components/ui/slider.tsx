'use client';

import * as React from 'react';
import { cn } from '@/lib/utils';

const Slider = React.forwardRef<
  HTMLInputElement,
  Omit<React.InputHTMLAttributes<HTMLInputElement>, 'value' | 'defaultValue'> & {
    value?: number[];
    defaultValue?: number[];
    onValueChange?: (value: number[]) => void;
    max?: number;
    step?: number;
  }
>(({ className, value, defaultValue, onValueChange, max = 100, step = 1, ...props }, ref) => {
  // Initialize state from value (controlled) or defaultValue (uncontrolled) or default to 0
  const [localValue, setLocalValue] = React.useState(
    (value && value[0]) ?? (defaultValue && defaultValue[0]) ?? 0
  );

  // Sync state if controlled value changes
  React.useEffect(() => {
    if (value !== undefined) {
      setLocalValue(value[0]);
    }
  }, [value]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = parseFloat(e.target.value);
    setLocalValue(newValue);
    onValueChange?.([newValue]);
  };

  return (
    <div className="relative flex w-full touch-none select-none items-center">
      <input
        type="range"
        min={0}
        max={max}
        step={step}
        value={localValue}
        onChange={handleChange}
        ref={ref}
        className={cn(
          'h-2 w-full cursor-pointer appearance-none rounded-full bg-slate-700 accent-cyan-500',
          className
        )}
        {...props}
      />
    </div>
  );
});
Slider.displayName = 'Slider';

export { Slider };

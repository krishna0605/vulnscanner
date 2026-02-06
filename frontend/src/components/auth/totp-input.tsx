'use client';

import { useState, useRef, useEffect, KeyboardEvent, ClipboardEvent } from 'react';

interface TOTPInputProps {
  length?: number;
  onComplete: (code: string) => void;
  disabled?: boolean;
  error?: string | null;
  autoFocus?: boolean;
}

export function TOTPInput({ 
  length = 6, 
  onComplete, 
  disabled = false,
  error = null,
  autoFocus = true
}: TOTPInputProps) {
  const [values, setValues] = useState<string[]>(Array(length).fill(''));
  const inputRefs = useRef<(HTMLInputElement | null)[]>([]);

  useEffect(() => {
    if (autoFocus && inputRefs.current[0]) {
      inputRefs.current[0].focus();
    }
  }, [autoFocus]);

  // Check if all digits are filled and call onComplete
  useEffect(() => {
    const code = values.join('');
    if (code.length === length && values.every(v => v !== '')) {
      onComplete(code);
    }
  }, [values, length, onComplete]);

  const handleChange = (index: number, value: string) => {
    // Only allow digits
    if (value && !/^\d$/.test(value)) return;

    const newValues = [...values];
    newValues[index] = value;
    setValues(newValues);

    // Move to next input if value is entered
    if (value && index < length - 1) {
      inputRefs.current[index + 1]?.focus();
    }
  };

  const handleKeyDown = (index: number, e: KeyboardEvent<HTMLInputElement>) => {
    // Handle backspace
    if (e.key === 'Backspace') {
      if (values[index] === '' && index > 0) {
        // Move to previous input if current is empty
        inputRefs.current[index - 1]?.focus();
      } else {
        // Clear current input
        const newValues = [...values];
        newValues[index] = '';
        setValues(newValues);
      }
    }
    
    // Handle arrow keys
    if (e.key === 'ArrowLeft' && index > 0) {
      inputRefs.current[index - 1]?.focus();
    }
    if (e.key === 'ArrowRight' && index < length - 1) {
      inputRefs.current[index + 1]?.focus();
    }
  };

  const handlePaste = (e: ClipboardEvent<HTMLInputElement>) => {
    e.preventDefault();
    const pastedData = e.clipboardData.getData('text').replace(/\D/g, '').slice(0, length);
    
    if (pastedData) {
      const newValues = [...values];
      for (let i = 0; i < pastedData.length; i++) {
        newValues[i] = pastedData[i];
      }
      setValues(newValues);
      
      // Focus the next empty input or the last one
      const nextEmptyIndex = newValues.findIndex(v => v === '');
      if (nextEmptyIndex !== -1) {
        inputRefs.current[nextEmptyIndex]?.focus();
      } else {
        inputRefs.current[length - 1]?.focus();
      }
    }
  };

  const reset = () => {
    setValues(Array(length).fill(''));
    inputRefs.current[0]?.focus();
  };

  return (
    <div className="w-full">
      <div className="flex justify-center gap-2 sm:gap-3">
        {values.map((value, index) => (
          <input
            key={index}
            ref={(el) => { inputRefs.current[index] = el; }}
            type="text"
            inputMode="numeric"
            maxLength={1}
            value={value}
            onChange={(e) => handleChange(index, e.target.value)}
            onKeyDown={(e) => handleKeyDown(index, e)}
            onPaste={handlePaste}
            disabled={disabled}
            className={`
              w-10 h-12 sm:w-12 sm:h-14 
              text-center text-xl sm:text-2xl font-mono font-bold
              rounded-lg border-2 
              bg-white/5 text-white
              transition-all duration-200
              focus:outline-none focus:ring-2 focus:ring-white/50
              disabled:opacity-50 disabled:cursor-not-allowed
              ${error 
                ? 'border-red-500/50 focus:border-red-500' 
                : 'border-white/20 focus:border-white/50 hover:border-white/30'
              }
            `}
            aria-label={`Digit ${index + 1}`}
          />
        ))}
      </div>
      
      {error && (
        <p className="mt-3 text-center text-sm text-red-400">
          {error}
        </p>
      )}
      
      <button
        type="button"
        onClick={reset}
        className="mt-4 w-full text-center text-sm text-slate-500 hover:text-slate-300 transition-colors"
      >
        Clear and try again
      </button>
    </div>
  );
}

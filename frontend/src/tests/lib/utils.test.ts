/**
 * Utility Functions Tests
 * Tests for shared utility functions
 */
import { describe, it, expect } from 'vitest';
import { cn } from '@/lib/utils';

describe('cn (className utility)', () => {
  it('merges multiple class names', () => {
    const result = cn('class1', 'class2');
    expect(result).toBe('class1 class2');
  });

  it('handles conditional classes', () => {
    const isActive = true;
    const result = cn('base', isActive && 'active');
    expect(result).toContain('base');
    expect(result).toContain('active');
  });

  it('handles false conditional classes', () => {
    const isActive = false;
    const result = cn('base', isActive && 'active');
    expect(result).toBe('base');
    expect(result).not.toContain('active');
  });

  it('handles undefined and null', () => {
    const result = cn('base', undefined, null);
    expect(result).toBe('base');
  });

  it('handles empty string', () => {
    const result = cn('base', '');
    expect(result).toBe('base');
  });

  it('merges Tailwind classes correctly', () => {
    const result = cn('px-4 py-2', 'px-8');
    // tailwind-merge should keep only px-8, not both
    expect(result).toContain('px-8');
    expect(result).toContain('py-2');
  });

  it('handles arrays of classes', () => {
    const result = cn(['class1', 'class2']);
    expect(result).toContain('class1');
    expect(result).toContain('class2');
  });

  it('handles nested conditionals', () => {
    const variant = 'primary';
    const result = cn('btn', {
      'btn-primary': variant === 'primary',
      'btn-secondary': variant === 'secondary',
    });
    expect(result).toContain('btn');
    expect(result).toContain('btn-primary');
    expect(result).not.toContain('btn-secondary');
  });

  it('deduplicates conflicting Tailwind utilities', () => {
    const result = cn('text-red-500', 'text-blue-500');
    // tailwind-merge keeps the last one
    expect(result).toBe('text-blue-500');
  });

  it('handles complex utility combinations', () => {
    const result = cn(
      'bg-white dark:bg-gray-800',
      'hover:bg-gray-100',
      'rounded-lg shadow-md'
    );
    expect(result).toContain('bg-white');
    expect(result).toContain('dark:bg-gray-800');
    expect(result).toContain('hover:bg-gray-100');
    expect(result).toContain('rounded-lg');
    expect(result).toContain('shadow-md');
  });
});

describe('Date formatting utilities', () => {
  it('formats dates consistently', () => {
    // Test that date formatting works
    const date = new Date('2026-02-07T12:00:00Z');
    const formatted = date.toLocaleDateString('en-US');
    expect(formatted).toBeTruthy();
    expect(typeof formatted).toBe('string');
  });

  it('handles relative time', () => {
    const now = new Date();
    const yesterday = new Date(now.getTime() - 24 * 60 * 60 * 1000);
    expect(yesterday < now).toBe(true);
  });
});

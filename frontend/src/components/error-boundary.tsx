'use client';

import React, { Component, ErrorInfo, ReactNode } from 'react';
import { logger } from '../utils/logger';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  // ...

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    logger.error('Uncaught error caught by boundary', { error, errorInfo });
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div className="flex flex-col items-center justify-center min-h-[400px] p-6 text-center">
          <div className="bg-red-50 p-6 rounded-lg max-w-md w-full border border-red-100">
            <h2 className="text-xl font-bold text-red-800 mb-2">Something went wrong</h2>
            <p className="text-red-600 mb-4">
              We encountered an unexpected error. Please try refreshing the page.
            </p>
            {this.state.error && process.env.NODE_ENV === 'development' && (
              <pre className="text-xs text-left bg-white p-3 rounded border border-red-200 overflow-auto max-h-40 mb-4">
                {this.state.error.message}
              </pre>
            )}
            <button
              className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
              onClick={() => window.location.reload()}
            >
              Refresh Page
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

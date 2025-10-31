import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth.ts';
import { useSelector } from 'react-redux';
import { RootState } from '../store/index.ts';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const location = useLocation();
  const { user, loading } = useAuth();
  const { isAuthenticated, loading: reduxLoading } = useSelector((state: RootState) => state.auth);

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

  // Show loading spinner while checking authentication (but only briefly)
  const isLoading = loading || reduxLoading;
  if (isLoading && !hasStoredAuth) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background-dark">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  // Check authentication from multiple sources
  const isUserAuthenticated = user || isAuthenticated || hasStoredAuth;

  if (!isUserAuthenticated) {
    // Redirect to login page with return url
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return <>{children}</>;
};

export default ProtectedRoute;
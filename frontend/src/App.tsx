import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext.tsx';
import ProtectedRoute from './components/ProtectedRoute.tsx';
import LoginPage from './pages/LoginPage.tsx';
import CreateAccountPage from './pages/CreateAccountPage.tsx';
import ResetPasswordPage from './pages/ResetPasswordPage.tsx';
import PricingPage from './pages/PricingPage.tsx';
import LandingPage from './pages/LandingPage.tsx';
import StripeCheckoutPage from './pages/StripeCheckoutPage.tsx';

import EnhancedDashboardPage from './pages/EnhancedDashboardPage.tsx';
import UserProfilePage from './pages/UserProfilePage.tsx';
import CreateProjectPage from './pages/CreateProjectPage.tsx';
import ScanConfigPage from './pages/ScanConfigPage.tsx';
import ProjectListPage from './pages/ProjectListPage.tsx';
import ProjectDetailsPage from './pages/ProjectDetailsPage.tsx';
import ScanOverviewPage from './pages/ScanOverviewPage.tsx';
import ReportsLandingPage from './pages/ReportsLandingPage.tsx';
import ReportsContextPage from './pages/ReportsContextPage.tsx';
import FindingDetailPage from './pages/FindingDetailPage.tsx';
import SettingsPage from './pages/SettingsPage.tsx';
import ApiManagementPage from './pages/ApiManagementPage.tsx';
import NotificationSettingsPage from './pages/NotificationSettingsPage.tsx';
import SecuritySettingsPage from './pages/SecuritySettingsPage.tsx';

const App: React.FC = () => {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<CreateAccountPage />} />
        <Route path="/forgot-password" element={<ResetPasswordPage />} />
        <Route path="/pricing" element={<PricingPage />} />
        <Route path="/checkout" element={<StripeCheckoutPage />} />
        <Route path="/dashboard" element={<ProtectedRoute><EnhancedDashboardPage /></ProtectedRoute>} />
        <Route path="/profile" element={<ProtectedRoute><UserProfilePage /></ProtectedRoute>} />
        <Route path="/projects" element={<ProtectedRoute><ProjectListPage /></ProtectedRoute>} />
        <Route path="/projects/:projectId" element={<ProtectedRoute><ProjectDetailsPage /></ProtectedRoute>} />
        <Route path="/projects/new" element={<ProtectedRoute><CreateProjectPage /></ProtectedRoute>} />
        <Route path="/scans" element={<ProtectedRoute><ScanOverviewPage /></ProtectedRoute>} />
        <Route path="/scans/new" element={<ProtectedRoute><ScanConfigPage /></ProtectedRoute>} />
        {/* Reports flow */}
        <Route path="/reports" element={<ProtectedRoute><ReportsLandingPage /></ProtectedRoute>} />
        <Route path="/reports/project/:projectId" element={<ProtectedRoute><ReportsContextPage /></ProtectedRoute>} />
        <Route path="/reports/scan/:scanId" element={<ProtectedRoute><ReportsContextPage /></ProtectedRoute>} />
        <Route path="/reports/scan/:scanId/findings/:findingId" element={<ProtectedRoute><FindingDetailPage /></ProtectedRoute>} />
        {/* Settings */}
        <Route path="/settings" element={<ProtectedRoute><SettingsPage /></ProtectedRoute>} />
        <Route path="/settings/api" element={<ProtectedRoute><ApiManagementPage /></ProtectedRoute>} />
        <Route path="/settings/notifications" element={<ProtectedRoute><NotificationSettingsPage /></ProtectedRoute>} />
        <Route path="/settings/security" element={<ProtectedRoute><SecuritySettingsPage /></ProtectedRoute>} />
      </Routes>
    </AuthProvider>
  );
};

export default App;
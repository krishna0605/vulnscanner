import React from 'react';
import ReactDOM from 'react-dom/client';
import { Provider } from 'react-redux';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import './index.css';
import App from './App.tsx';
import { store } from './store/index.ts';
import { loginSuccess } from './store/slices/authSlice.ts';

const queryClient = new QueryClient();

// Initialize auth state from storage (session token or JWT)
try {
  const token = localStorage.getItem('authToken') || sessionStorage.getItem('authToken');
  const email = localStorage.getItem('authUserEmail') || sessionStorage.getItem('authUserEmail');
  if (token && email) {
    store.dispatch(loginSuccess({ email }));
  }
} catch {}

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

root.render(
  <React.StrictMode>
    <Provider store={store}>
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <App />
        </BrowserRouter>
      </QueryClientProvider>
    </Provider>
  </React.StrictMode>
);
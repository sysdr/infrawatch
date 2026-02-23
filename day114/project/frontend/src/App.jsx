import React, { Suspense, lazy } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import AppLayout from './components/common/AppLayout';
import PageSkeleton from './components/common/PageSkeleton';

// Code-split pages: each gets its own JS chunk
const Dashboard   = lazy(() => import('./pages/Dashboard'));
const VitalsPage  = lazy(() => import('./pages/VitalsPage'));
const BundlePage  = lazy(() => import('./pages/BundlePage'));
const SWPage      = lazy(() => import('./pages/SWPage'));

export default function App() {
  return (
    <AppLayout>
      <Suspense fallback={<PageSkeleton />}>
        <Routes>
          <Route path="/"          element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/vitals"    element={<VitalsPage />} />
          <Route path="/bundles"   element={<BundlePage />} />
          <Route path="/sw"        element={<SWPage />} />
        </Routes>
      </Suspense>
    </AppLayout>
  );
}

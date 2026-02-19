import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';

// Public pages
import HomePage from './pages/public/HomePage';
import MoviePage from './pages/public/MoviePage';
import HallPage from './pages/public/HallPage';
import PaymentPage from './pages/public/PaymentPage';
import TicketPage from './pages/public/TicketPage';
import LoginPage from './pages/public/LoginPage';
import RegisterPage from './pages/public/RegisterPage';

// Admin pages
import AdminLayout from './pages/admin/AdminLayout';
import AdminDashboard from './pages/admin/AdminDashboard';
import AdminHalls from './pages/admin/AdminHalls';
import AdminMovies from './pages/admin/AdminMovies';
import AdminScreenings from './pages/admin/AdminScreenings';

// Layout components
import Header from './components/layout/Header';

const PrivateRoute = ({ children, adminOnly = false }) => {
  const { isAuthenticated, isAdmin, loading } = useAuth();
  
  if (loading) {
    return <div className="flex justify-center items-center h-screen">
      <div className="text-2xl">Загрузка...</div>
    </div>;
  }
  
  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }
  
  if (adminOnly && !isAdmin) {
    return <Navigate to="/" />;
  }
  
  return children;
};

function AppRoutes() {
  return (
    <Routes>
      {/* Public routes */}
      <Route path="/" element={<><Header /><HomePage /></>} />
      <Route path="/movie/:id" element={<><Header /><MoviePage /></>} />
      <Route path="/hall/:screeningId" element={<><Header /><HallPage /></>} />
      <Route path="/payment" element={<><Header /><PaymentPage /></>} />
      <Route path="/ticket/:bookingId" element={<><Header /><TicketPage /></>} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      
      {/* Admin routes */}
      <Route path="/admin" element={
        <PrivateRoute adminOnly>
          <AdminLayout />
        </PrivateRoute>
      }>
        <Route index element={<AdminDashboard />} />
        <Route path="halls" element={<AdminHalls />} />
        <Route path="movies" element={<AdminMovies />} />
        <Route path="screenings" element={<AdminScreenings />} />
      </Route>
    </Routes>
  );
}

function App() {
  return (
    <Router>
      <AuthProvider>
        <div className="min-h-screen">
          <AppRoutes />
        </div>
      </AuthProvider>
    </Router>
  );
}

export default App;
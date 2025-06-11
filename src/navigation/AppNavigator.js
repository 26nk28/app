import React from 'react';
import { BrowserRouter as Router, Route, Routes, Link, Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext'; // Import useAuth

// Import actual screen components
import OriginalLoginScreen from '../screens/Auth/LoginScreen';
import SignUpScreen from '../screens/Auth/SignUpScreen';
import UserInfoScreen from '../screens/Auth/UserInfoScreen';
import OriginalDashboardScreen from '../screens/Dashboard/DashboardScreen';
import OriginalProfileScreen from '../screens/Profile/ProfileScreen';
import GroupsListScreen from '../screens/Groups/GroupsListScreen';
import OriginalSettingsScreen from '../screens/Settings/SettingsScreen';
import CreateGroupScreen from '../screens/Groups/CreateGroupScreen';
import GroupDetailScreen from '../screens/Groups/GroupDetailScreen';
import MealSuggestionsScreen from '../screens/Meals/MealSuggestionsScreen';
import MealDetailScreen from '../screens/Meals/MealDetailScreen';

// Placeholder Screen Component
const PlaceholderScreen = ({ title }) => (
  <div style={{ padding: '20px', border: '1px solid #ccc', margin: '20px' }}>
    <h2>{title}</h2> <p>Placeholder for {title}.</p>
  </div>
);
const HealthQuestionnaireScreen = () => <PlaceholderScreen title="Health Questionnaire" />;

// ProtectedRoute component using AuthContext
const ProtectedRoute = () => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return <div>Loading authentication status...</div>; // Or a spinner
  }

  return isAuthenticated() ? <Outlet /> : <Navigate to="/login" replace />;
};

// Layout component including Navbar
const Layout = () => {
  const { isAuthenticated, logout, user } = useAuth();

  return (
    <>
      <nav style={{ backgroundColor: '#f0f0f0', padding: '10px 20px', marginBottom: '20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Link to="/" style={{ textDecoration: 'none', color: 'var(--primary-color)', fontWeight: 'bold', fontSize: 'var(--font-size-large)' }}>
          HarmonyPlate
        </Link>
        <ul style={{ listStyleType: 'none', padding: 0, margin: 0, display: 'flex', gap: '15px', alignItems: 'center' }}>
          {isAuthenticated() ? (
            <>
              {user && <li style={{color: 'var(--text-color)'}}>Hi, {user.name || user.email}</li>}
              <li><Link to="/">Dashboard</Link></li>
              <li><Link to="/groups">Groups</Link></li>
              <li><Link to="/profile">Profile</Link></li>
              <li><Link to="/settings">Settings</Link></li>
              <li><button onClick={() => logout()} className="button-primary" style={{backgroundColor: 'var(--error-color)', padding: 'var(--spacing-small)'}}>Logout</button></li>
            </>
          ) : (
            <>
              <li><Link to="/login">Login</Link></li>
              <li><Link to="/signup">Sign Up</Link></li>
            </>
          )}
        </ul>
      </nav>
      <div style={{ padding: 'var(--spacing-medium)'}}>
        <Outlet /> {/* Child routes will render here */}
      </div>
    </>
  );
};

function AppNavigator() {
  return (
    <Router>
      <Routes>
        <Route element={<Layout />}> {/* All routes now use the Layout with Navbar */}
          {/* Public Routes */}
          <Route path="/login" element={<OriginalLoginScreen />} />
          <Route path="/signup" element={<SignUpScreen />} />
          <Route path="/user-info" element={<UserInfoScreen />} /> {/* This should ideally be protected or part of a specific flow */}

          {/* Protected Routes */}
          <Route element={<ProtectedRoute />}>
            <Route path="/" element={<OriginalDashboardScreen />} />
            <Route path="/profile" element={<OriginalProfileScreen />} />
            <Route path="/groups" element={<GroupsListScreen />} />
            <Route path="/settings" element={<OriginalSettingsScreen />} />
            <Route path="/health-questionnaire" element={<HealthQuestionnaireScreen />} />
            <Route path="/groups/create" element={<CreateGroupScreen />} />
            <Route path="/groups/:groupId" element={<GroupDetailScreen />} />
            <Route path="/groups/:groupId/meals" element={<MealSuggestionsScreen />} />
            <Route path="/meals/details/:mealId" element={<MealDetailScreen />} />
            {/* Add other protected routes here */}
          </Route>

          {/* Fallback for undefined routes */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default AppNavigator;

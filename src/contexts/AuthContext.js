import React, { createContext, useState, useEffect, useContext } from 'react';
// Import userOnboardingApi if login is ever actually implemented here
// import { userOnboardingApi } from '../services/api';
import { userOnboardingApi } from '../services/api';


export const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null); // Could store user details { id, name, email, agentId }
  const [token, setToken] = useState(localStorage.getItem('authToken'));
  const [isLoading, setIsLoading] = useState(true); // To check auth status on initial load

  useEffect(() => {
    // This effect runs on initial app load to check if a token exists
    // In a real app, you'd validate the token with the backend here
    const storedToken = localStorage.getItem('authToken');
    if (storedToken) {
      setToken(storedToken);
      // setUser({ name: 'Mock User' }); // TODO: Fetch user details if token is valid
      // For now, if token exists, assume user is "logged in" for mock purposes
      // If you had a /me endpoint:
      // apiService.get('/auth/me').then(userData => setUser(userData)).catch(() => logout());
    }
    setIsLoading(false);
  }, []);

  const login = async (email, password) => {
    // TODO: Replace with actual API call when backend login endpoint exists
    // const { token: apiToken, user: userData } = await userOnboardingApi.login({ email, password });
    console.log("AuthContext: Mock login attempt", { email, password });
    if (email === "user@example.com" && password === "password") {
      const dummyToken = 'dummyAuthToken';
      localStorage.setItem('authToken', dummyToken);
      setToken(dummyToken);
      setUser({ email, name: 'Mock User' }); // Set mock user data
      console.log("AuthContext: Mock login successful");
      return { success: true };
    } else {
      console.log("AuthContext: Mock login failed");
      return { success: false, message: "Invalid credentials" };
    }
  };

  const signupAndOnboard = async (onboardingData) => {
    // onboardingData: { name, email, phone, health_form }
    try {
      // The backend /onboard endpoint creates the user and returns session/user IDs
      const response = await userOnboardingApi.onboardUser(onboardingData);
      // response includes: message, onboarding_session_id, user_id, agent_id
      // For actual login, a separate login step or token return from onboard is needed.
      // For now, we are not logging the user in directly after onboarding via this context function.
      // The flow is: signup -> user_info -> (onboard API call) -> health_questionnaire -> login
      console.log('AuthContext: Onboarding API call successful', response);
      return { success: true, data: response };
    } catch (error) {
      console.error('AuthContext: Onboarding API call failed', error);
      return { success: false, message: error.message || "Onboarding failed" };
    }
  };


  const logout = () => {
    localStorage.removeItem('authToken');
    setUser(null);
    setToken(null);
    // In a real app, you might also want to call a backend /logout endpoint
  };

  const isAuthenticated = () => !!token;

  return (
    <AuthContext.Provider value={{ user, token, login, logout, signupAndOnboard, isAuthenticated, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

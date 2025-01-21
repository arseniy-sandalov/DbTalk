import React, { useState, useEffect } from 'react';
import './App.css';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import AuthPage from './pages/AuthPage';
import ChatComponent from './pages/ChatComponent';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [token, setToken] = useState(null);
  const [userId, setUserId] = useState(null); 
  const [loading, setLoading] = useState(true); // Add a loading state

  // On app load, check if a token and userId exist in localStorage
  useEffect(() => {
    const savedToken = localStorage.getItem('token');
    const savedUserId = localStorage.getItem('userId');
    if (savedToken && savedUserId) {
      verifyToken(savedToken);
      setUserId(savedUserId);  // Retrieve the userId from localStorage
    } else {
      setLoading(false); // If no token, stop loading
    }
  }, []);

  // Function to verify token validity
  const verifyToken = async (savedToken) => {
    try {
      const response = await fetch(`http://localhost:8000/verify-token/${savedToken}`);
      if (response.ok) {
        setIsAuthenticated(true);
        setToken(savedToken);
      } else {
        localStorage.removeItem('token'); // Token is invalid, clear it
        setIsAuthenticated(false);
      }
    } catch (error) {
      console.error('Token verification failed', error);
      localStorage.removeItem('token'); // Token is invalid, clear it
      setIsAuthenticated(false);
    } finally {
      setLoading(false); // Stop loading after verification
    }
  };

  // Handle successful login
  const handleLogin = (token, userId) => {
    setIsAuthenticated(true);
    setToken(token);
    setUserId(userId); // Store userId after login
    localStorage.setItem('token', token);
    localStorage.setItem('userId', userId); // Save userId in localStorage
  };

  if (loading) {
    // Optionally display a loading spinner here
    return <div>Loading...</div>;
  }

  return (
    <Router>
      <Routes>
        <Route path="/" element={<AuthPage onLogin={handleLogin} />} />
        <Route path="/chat" element={isAuthenticated ? <ChatComponent token={token} userId={userId} /> : <Navigate to="/" />} />
      </Routes>
    </Router>
  );
}

export default App;





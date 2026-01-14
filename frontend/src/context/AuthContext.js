import React, { createContext, useContext, useState, useEffect } from 'react';
import { auth, onAuthStateChanged, getIdToken } from '../lib/firebase';
import axios from 'axios';
import { setAuthToken } from '../lib/api';

const AuthContext = createContext(null);

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [dbUser, setDbUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState(null);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (firebaseUser) => {
      setLoading(true);
      if (firebaseUser) {
        setUser(firebaseUser);
        try {
          const idToken = await firebaseUser.getIdToken();
          setToken(idToken);
          
          // Save token to localStorage
          setAuthToken(idToken);
          
          // Verify with backend and get/create user
          const response = await axios.post(
            `${BACKEND_URL}/api/auth/verify`,
            {},
            { headers: { Authorization: `Bearer ${idToken}` } }
          );
          setDbUser(response.data.user);
        } catch (error) {
          console.error('Error verifying user:', error);
          setDbUser(null);
        }
      } else {
        setUser(null);
        setDbUser(null);
        setToken(null);
        setAuthToken(null);
      }
      setLoading(false);
    });

    return () => unsubscribe();
  }, []);

  const refreshToken = async () => {
    if (user) {
      const newToken = await getIdToken();
      setToken(newToken);
      return newToken;
    }
    return null;
  };

  return (
    <AuthContext.Provider value={{ user, dbUser, token, loading, refreshToken }}>
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

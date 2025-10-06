/**
 * Authentication Context
 *
 * Provides Firebase authentication state and methods for the application.
 * Supports optional auth mode - works with or without Firebase enabled.
 */

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import {
  User,
  signInWithPopup,
  signOut as firebaseSignOut,
  onAuthStateChanged,
} from 'firebase/auth';
import { auth, googleProvider, ENABLE_AUTH, isFirebaseReady } from '@/lib/firebase';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  signInWithGoogle: () => Promise<void>;
  signOut: () => Promise<void>;
  getIdToken: () => Promise<string | null>;
  isAuthEnabled: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    // If auth is disabled or Firebase not ready, set loading to false immediately
    if (!ENABLE_AUTH || !isFirebaseReady()) {
      setLoading(false);
      return;
    }

    // Subscribe to Firebase auth state changes
    const unsubscribe = onAuthStateChanged(auth!, (user) => {
      setUser(user);
      setLoading(false);

      if (user) {
        console.log('✅ User signed in:', user.email);

        // Check if user is @google.com
        if (!user.email?.endsWith('@google.com')) {
          console.warn('⚠️ User is not @google.com:', user.email);
          // Sign out non-Google users
          firebaseSignOut(auth!).catch(console.error);
        }
      } else {
        console.log('🔓 User signed out');
      }
    });

    // Cleanup subscription
    return () => unsubscribe();
  }, []);

  const signInWithGoogle = async (): Promise<void> => {
    if (!isFirebaseReady() || !auth || !googleProvider) {
      console.error('❌ Firebase not ready for sign in');
      throw new Error('Firebase authentication is not configured');
    }

    try {
      const result = await signInWithPopup(auth, googleProvider);

      // Check if user is @google.com
      if (!result.user.email?.endsWith('@google.com')) {
        console.error('❌ Access denied: Not a @google.com email');
        await firebaseSignOut(auth);
        throw new Error('Access restricted to @google.com email addresses only');
      }

      console.log('✅ Signed in successfully:', result.user.email);
    } catch (error: any) {
      console.error('❌ Sign in failed:', error);
      throw error;
    }
  };

  const signOut = async (): Promise<void> => {
    if (!isFirebaseReady() || !auth) {
      console.error('❌ Firebase not ready for sign out');
      return;
    }

    try {
      await firebaseSignOut(auth);
      console.log('✅ Signed out successfully');
    } catch (error) {
      console.error('❌ Sign out failed:', error);
      throw error;
    }
  };

  const getIdToken = async (): Promise<string | null> => {
    if (!ENABLE_AUTH || !user) {
      return null;
    }

    try {
      const token = await user.getIdToken();
      return token;
    } catch (error) {
      console.error('❌ Failed to get ID token:', error);
      return null;
    }
  };

  const value: AuthContextType = {
    user,
    loading,
    signInWithGoogle,
    signOut,
    getIdToken,
    isAuthEnabled: ENABLE_AUTH,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// Hook to use auth context
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

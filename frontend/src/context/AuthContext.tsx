'use client';

import { createContext, useContext, useState, ReactNode, useEffect, useCallback } from 'react';
import keycloak from '@/keycloak';
import { KeycloakProfile } from 'keycloak-js';

// Extend the KeycloakProfile with potential custom attributes if needed
type User = KeycloakProfile & {
  // e.g., department?: string;
};

interface AuthContextType {
  user: User | null;
  token: string | null;
  authenticated: boolean;
  loading: boolean;
  login: () => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [authenticated, setAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true); // Start with loading state
  const [isKeycloakInitialized, setIsKeycloakInitialized] = useState(false); // New state to prevent multiple initializations

  const login = useCallback(() => {
    keycloak.login();
  }, []);

  const logout = useCallback(() => {
    keycloak.logout();
  }, []);

  useEffect(() => {
    if (isKeycloakInitialized) {
      return; // Already initialized, do nothing
    }

    const initKeycloak = async () => {
      try {
        const auth = await keycloak.init({
          onLoad: 'check-sso',
          silentCheckSsoRedirectUri: window.location.origin + '/silent-check-sso.html',
        });

        setAuthenticated(auth);

        if (auth) {
          const userProfile = await keycloak.loadUserProfile();
          setUser(userProfile as User);
          setToken(keycloak.token || null);

          // Set up a timer to refresh the token before it expires
          keycloak.onTokenExpired = () => {
            keycloak.updateToken(30) // Refresh if token expires in 30 seconds or less
              .then((refreshed) => {
                if (refreshed) {
                  setToken(keycloak.token || null);
                  console.log('Token was successfully refreshed');
                } else {
                  console.warn('Token not refreshed, valid for ' + Math.round(keycloak.tokenParsed!.exp! + keycloak.timeSkew! - new Date().getTime() / 1000) + ' seconds');
                }
              })
              .catch(() => {
                console.error('Failed to refresh the token, or the session has expired');
                keycloak.logout(); // Log out if refresh fails
              });
          };
        }
      } catch (error) {
        console.error("Failed to initialize Keycloak:", error);
      } finally {
        setLoading(false); // Initialization finished, stop loading
        setIsKeycloakInitialized(true); // Mark as initialized
      }
    };

    initKeycloak();

    // Clean up event listeners
    return () => {
      keycloak.onTokenExpired = undefined;
    };
  }, [isKeycloakInitialized]); // Add isKeycloakInitialized to dependency array

  return (
    <AuthContext.Provider value={{ user, token, authenticated, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
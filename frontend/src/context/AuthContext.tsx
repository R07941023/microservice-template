import { createContext, useContext, useState, ReactNode, useEffect } from 'react';
import { jwtDecode } from 'jwt-decode';

interface User {
  sub: string; // Google user ID
  email: string;
  name: string;
  picture?: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (jwtToken: string) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);

  // Load token from localStorage on initial load
  useEffect(() => {
    const storedToken = localStorage.getItem('google_id_token');
    if (storedToken) {
      try {
        const decodedUser = jwtDecode<User>(storedToken);
        setUser(decodedUser);
        setToken(storedToken);
      } catch (error) {
        console.error("Failed to decode stored token:", error);
        localStorage.removeItem('google_id_token'); // Clear invalid token
      }
    }
  }, []);

  const login = (jwtToken: string) => {
    try {
      const decodedUser = jwtDecode<User>(jwtToken);
      setUser(decodedUser);
      setToken(jwtToken);
      localStorage.setItem('google_id_token', jwtToken);
      console.log("AuthContext: User logged in", decodedUser);
    } catch (error) {
      console.error("AuthContext: Failed to decode JWT on login:", error);
      setUser(null);
      setToken(null);
      localStorage.removeItem('google_id_token');
    }
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('google_id_token');
    console.log("AuthContext: User logged out");
  };

  return (
    <AuthContext.Provider value={{ user, token, login, logout }}>
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

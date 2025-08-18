'use client';

import { useAuth } from '../context/AuthContext'; // Use relative path

const LoginComponent = () => {
  const { authenticated, user, login, logout } = useAuth();

  if (authenticated) {
    return (
      <div className="flex items-center space-x-2">
        <span className="text-white text-sm hidden md:block">
          {user?.username || user?.email || "Logged In"}
        </span>
        <button
          onClick={logout}
          className="bg-red-500 hover:bg-red-700 text-white text-sm py-1 px-3 rounded"
        >
          Logout
        </button>
      </div>
    );
  }

  return (
    <button
      onClick={login}
      className="bg-blue-500 hover:bg-blue-700 text-white text-sm font-bold py-1 px-3 rounded"
    >
      Login
    </button>
  );
};

export default LoginComponent;
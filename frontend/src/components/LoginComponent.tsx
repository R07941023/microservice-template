'use client';

import { GoogleLogin } from '@react-oauth/google';
import { useAuth } from '@/context/AuthContext';
import Image from 'next/image';

const LoginComponent = () => {
  const { user, login, logout } = useAuth();

  if (user) {
    return (
      <div className="flex items-center space-x-2">
        {user.picture && (
          <Image
            src={user.picture}
            alt="User Avatar"
            width={32}      // 對應 w-8 = 2rem = 32px
            height={32}
            className="rounded-full"
          />
        )}
        <span className="text-white text-sm hidden md:block">{user.name || user.email}</span>
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
    <GoogleLogin
      text="signin_with"
      theme="filled_black"
      onSuccess={credentialResponse => {
        if (credentialResponse.credential) {
          login(credentialResponse.credential);
        }
      }}
      onError={() => {
        console.log('Login Failed');
      }}
    />
  );
};

export default LoginComponent;

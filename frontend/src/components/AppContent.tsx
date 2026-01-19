'use client';

import { ReactNode } from "react";
import { useAuth } from "@/context/AuthContext";
import LoginComponent from "@/components/LoginComponent";

const AppContent = ({ children }: { children: ReactNode }) => {
  const { loading } = useAuth();

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <p>Initializing Authentication...</p>
      </div>
    );
  }

  return (
    <div className="antialiased flex flex-col min-h-screen">
      <header className="bg-gray-800 text-white p-4 shadow-md">
        <div className="container mx-auto flex justify-between items-center">
          <div className="flex items-center">
            <img src="/maplestory-icon.png?v=2" alt="MapleStory Icon" className="h-8 w-8 mr-3" />
            <h1 className="text-2xl font-bold">MapleStory V113 Item Database</h1>
          </div>
          <LoginComponent />
        </div>
      </header>
      <main className="flex-grow container mx-auto p-4">{children}</main>
      <footer className="bg-gray-800 text-white p-4 text-center text-sm">
        <div className="container mx-auto"> MapleStory V113 Item Database. All rights reserved.
        </div>
      </footer>
    </div>
  );
};

export default AppContent;
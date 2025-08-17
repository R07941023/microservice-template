'use client';
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import LoginComponent from '@/components/LoginComponent';
import { AuthProvider, useAuth } from '@/context/AuthContext';
import { ReactNode } from "react";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

// Create a new component to handle the loading state UI
const AppContent = ({ children }: { children: ReactNode }) => {
  // No conditional rendering based on loading, initError, authenticated here
  // LoginComponent will handle authentication UI based on useAuth() internally

  return (
    <div className="antialiased flex flex-col min-h-screen">
      <header className="bg-gray-800 text-white p-4 shadow-md">
        <div className="container mx-auto flex justify-between items-center">
          <h1 className="text-2xl font-bold">MapleStory V113 Item Database</h1>
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

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${geistSans.variable} ${geistMono.variable}`}>
        <AuthProvider>
          <AppContent>{children}</AppContent>
        </AuthProvider>
      </body>
    </html>
  );
}
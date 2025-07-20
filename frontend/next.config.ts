import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  images: {
    domains: ['lh3.googleusercontent.com'],
  },
  webpack: (config, { isServer }) => {
    if (!isServer) {
      config.watchOptions = {
        poll: 1000, // Check for changes every 1000ms (1 second)
        aggregateTimeout: 1000, // Delay before rebuilding after a change
      };
    }
    return config;
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://ms-maple-drop-repo:8000/:path*',
      },
    ];
  },
  /* config options here */
};

export default nextConfig;

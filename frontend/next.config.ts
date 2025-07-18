import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  webpack: (config, { isServer }) => {
    if (!isServer) {
      config.watchOptions = {
        poll: 1000, // Check for changes every 1000ms (1 second)
        aggregateTimeout: 1000, // Delay before rebuilding after a change
      };
    }
    return config;
  },
  /* config options here */
};

export default nextConfig;

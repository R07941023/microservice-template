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
        source: '/api/images/:path*',
        destination: 'http://kong:8000/ms-image-retriever/images/:path*',
      },
      {
        source: '/api/get_drop/:path*',
        destination: 'http://kong:8000/ms-drop-repo/get_drop/:path*',
      },
      {
        source: '/api/add_drop',
        destination: 'http://kong:8000/ms-drop-repo/add_drop',
      },
      {
        source: '/api/delete_drop/:path*',
        destination: 'http://kong:8000/ms-drop-repo/delete_drop/:path*',
      },
      {
        source: '/api/names/all',
        destination: 'http://kong:8000/ms-name-resolver/api/names/all',
      },
      {
        source: '/api/name-to-ids/:path*',
        destination: 'http://kong:8000/ms-name-resolver/api/name-to-ids/:path*',
      },
      {
        source: '/api/existence-check/:path*',
        destination: 'http://kong:8000/ms-search-aggregator/api/existence-check/:path*',
      },
    ]
  },
  /* config options here */
};

export default nextConfig;

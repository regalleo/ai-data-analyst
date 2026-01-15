/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Rewrites are only needed for local development when using next.js proxy
  // For Vercel deployment, the frontend calls the backend directly via NEXT_PUBLIC_API_URL
  async rewrites() {
    // In production (Vercel), skip rewrites - API calls go directly to backend URL
    if (process.env.VERCEL_ENV === 'production') {
      return [];
    }
    // For local development, rewrite /api calls to local backend
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/api/:path*',
      },
    ];
  },
};

module.exports = nextConfig;


/** @type {import('next').NextConfig} */
const backend = process.env.BACKEND_URL || "http://localhost:8000";

const nextConfig = {
  async rewrites() {
    return [
      { source: "/api/:path*", destination: `${backend}/api/:path*` },
      { source: "/outputs/:path*", destination: `${backend}/outputs/:path*` },
    ];
  },
};

module.exports = nextConfig;

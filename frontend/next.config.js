/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  
  // Configuration pour SuperSmartMatch Unifié
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5050',
    NEXT_PUBLIC_SUPERSMARTMATCH_URL: process.env.NEXT_PUBLIC_SUPERSMARTMATCH_URL || 'http://localhost:5052',
    NEXT_PUBLIC_CV_PARSER_URL: process.env.NEXT_PUBLIC_CV_PARSER_URL || 'http://localhost:5051',
    NEXT_PUBLIC_JOB_PARSER_URL: process.env.NEXT_PUBLIC_JOB_PARSER_URL || 'http://localhost:5053',
  },

  // Configuration pour les images et assets
  images: {
    domains: ['localhost'],
    formats: ['image/avif', 'image/webp'],
  },

  // Configuration pour les redirections
  async redirects() {
    return [
      {
        source: '/matching',
        destination: '/supersmartmatch',
        permanent: true,
      },
      {
        source: '/smartmatch',
        destination: '/supersmartmatch',
        permanent: true,
      },
    ];
  },

  // Configuration pour les rewrites API
  async rewrites() {
    return [
      {
        source: '/api/matching/:path*',
        destination: `${process.env.NEXT_PUBLIC_SUPERSMARTMATCH_URL || 'http://localhost:5052'}/api/:path*`,
      },
    ];
  },

  // Headers de sécurité
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'Referrer-Policy',
            value: 'origin-when-cross-origin',
          },
        ],
      },
    ];
  },

  // Configuration Webpack pour optimisations
  webpack: (config, { buildId, dev, isServer, defaultLoaders, webpack }) => {
    // Optimisations pour la production
    if (!dev && !isServer) {
      config.resolve.alias = {
        ...config.resolve.alias,
        '@': './src',
      };
    }

    return config;
  },
};

module.exports = nextConfig;

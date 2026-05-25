import { defineConfig, type Plugin } from 'vitest/config';
import react from '@vitejs/plugin-react';
import path from 'path';

const mockCssPlugin: Plugin = {
  name: 'mock-css',
  enforce: 'pre',
  load(id) {
    if (id.endsWith('.css')) return '';
  },
};

export default defineConfig({
  plugins: [mockCssPlugin, react()],
  test: {
    globals: true,
    environment: 'happy-dom',
    css: false,
    setupFiles: ['./src/__tests__/setup.ts'],
    include: ['src/**/*.{test,spec}.{ts,tsx}'],
    exclude: ['node_modules', '.next'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html', 'lcov'],
      exclude: [
        'node_modules/**',
        '.next/**',
        'src/__tests__/**',
        '**/*.d.ts',
        'vitest.config.ts',
        'next.config.*',
        'postcss.config.*',
        'tailwind.config.*',
      ],
    },
    testTimeout: 10000,
    hookTimeout: 10000,
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
});

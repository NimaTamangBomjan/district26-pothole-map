import { defineConfig } from 'vite';
import { svelte } from '@sveltejs/vite-plugin-svelte';

// base: './' so the deployed app loads its data via relative paths
// (e.g. ./data/d26_zctas.pmtiles), matching the same-origin GitHub Pages.
// publicDir (default `public/`) is copied to the build
// root, including the symlinked `public/data` -> ../../data/processed.
export default defineConfig({
  base: './',
  plugins: [svelte()]
});

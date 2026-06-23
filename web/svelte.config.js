import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

export default {
  // Svelte 5. vitePreprocess enables <script lang="ts"> in components.
  preprocess: vitePreprocess()
};

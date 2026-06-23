<script lang="ts">
  import LayersIcon from './icons/LayersIcon.svelte';

  /** Mobile-only Layers button (Figma node 63:1269). Opens the layers modal.
   *  Figma: white circle, 0.5px secondary border, 50% opacity, no shadow. */
  let { onClick }: { onClick?: () => void } = $props();
</script>

<button type="button" class="fab" aria-label="Layers" aria-haspopup="dialog" onclick={onClick}>
  <LayersIcon />
</button>

<style>
  .fab {
    position: absolute;
    top: var(--space-400);
    right: var(--space-400);
    width: 50px;
    height: 50px;
    border-radius: 50%;
    background: var(--color-surface-base);
    border: 0.5px solid var(--color-on-surface-secondary);
    opacity: 0.5;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    color: var(--color-on-surface-primary);
  }
  /* Inferred: brighten on interaction (design specifies only the 50% resting state). */
  .fab:hover,
  .fab:focus-visible {
    opacity: 1;
  }
  @media (min-width: 768px) {
    .fab { display: none; }
  }
</style>

<script lang="ts">
  /** Loading placeholder rows shown while the attribute parquet parses. */
  let { rows = 6 }: { rows?: number } = $props();
</script>

<div class="skeleton" aria-hidden="true">
  {#each Array(rows) as _, i (i)}
    <div class="bar"></div>
  {/each}
</div>

<style>
  .skeleton {
    display: flex;
    flex-direction: column;
    gap: var(--space-200);
    padding-block: var(--space-100);
  }
  .bar {
    height: 14px;
    border-radius: 3px;
    background: var(--color-rank-empty);
    animation: pulse 1.4s ease-in-out infinite;
  }
  .bar:nth-child(odd) {
    animation-delay: 0.2s;
  }
  @keyframes pulse {
    0%,
    100% {
      opacity: 0.45;
    }
    50% {
      opacity: 0.9;
    }
  }
  @media (prefers-reduced-motion: reduce) {
    .bar {
      animation: none;
      opacity: 0.6;
    }
  }
</style>

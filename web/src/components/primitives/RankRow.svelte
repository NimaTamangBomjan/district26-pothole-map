<script lang="ts">
  import RankWidget from './RankWidget.svelte';

  /** Indicator label (fills) + Rank Widget (hugs). Used in the zip-code detail view. */
  let { label, value = null }: { label: string; value?: number | null } = $props();
</script>

<div class="rank-row">
  <span class="label">{label}</span>
  <RankWidget {value} />
</div>

<style>
  .rank-row {
    display: flex;
    align-items: center;
    /* 10px is a raw Figma value on this row (not a spacing token). */
    gap: 10px;
    padding-block: var(--space-100);
  }
  .label {
    flex: 1 0 0;
    min-width: 0;
    font-size: var(--type-small-size);
    font-weight: var(--type-small-weight);
    color: var(--color-on-surface-primary);
  }
</style>

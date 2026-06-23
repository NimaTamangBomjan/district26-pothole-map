<script lang="ts">
  /**
   * Label (fills) + value (hugs, tabular figures). Used in the district summary
   * view. `value` is a preformatted string — per-indicator formatting is
   * the caller's job, since district stats mix percents,
   * counts, densities, and means.
   */
  let { label, value }: { label: string; value: string } = $props();
</script>

<div class="stat-row">
  <span class="label">{label}</span>
  <span class="value">{value}</span>
</div>

<style>
  .stat-row {
    display: flex;
    align-items: center;
    gap: 10px;
    padding-block: var(--space-100);
    font-size: var(--type-small-size);
    color: var(--color-on-surface-primary);
  }
  .label {
    flex: 1 0 0;
    min-width: 0;
  }
  .value {
    flex-shrink: 0;
    text-align: right;
    font-variant-numeric: tabular-nums;
  }
</style>

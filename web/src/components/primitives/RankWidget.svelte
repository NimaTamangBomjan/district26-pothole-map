<script lang="ts">
  /**
   * Five-box within-district rank indicator.
   *
   * **no inversion** — `filledCount = value` (rank 5 → 5 filled = most of the
   * measured thing, rank 1 → 1 filled). "Good vs. bad" is conveyed by the
   * legend/context, NOT by fill direction. 
   *
   * `value = null` is the no-data / non-residential edge case: all boxes
   * empty and dimmed, layout preserved (never hidden).
   */
  let { value = null }: { value?: number | null } = $props();

  const BOXES = [1, 2, 3, 4, 5] as const;
</script>

<div
  class="rank-widget"
  class:is-empty={value == null}
  role="img"
  aria-label={value == null ? 'No data' : `Rank ${value} of 5`}
>
  {#each BOXES as i (i)}
    <span class="box" class:filled={value != null && i <= value} aria-hidden="true"></span>
  {/each}
</div>

<style>
  .rank-widget {
    display: inline-flex;
    gap: var(--space-25);
    align-items: flex-start;
  }
  .box {
    width: 10px;
    height: 10px;
    border-radius: 2px;
    background: var(--color-rank-empty);
  }
  .box.filled {
    background: var(--color-rank-filled);
  }
  /* No-data state: dim the whole widget (~30% opacity), no box filled. */
  .is-empty {
    opacity: 0.3;
  }
</style>

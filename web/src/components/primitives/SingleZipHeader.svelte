<script lang="ts">
  import ChevronRightIcon from '../icons/ChevronRightIcon.svelte';

  /**
   * Zip-detail header (Figma node 63:1318): back chevron + zip code (body/small-bold),
   * 0.5px bottom border. The chevron is the shared right-chevron flipped to point
   * left. The back control is a real button returning to the zip list.
   */
  let { zip, onBack }: { zip: string; onBack?: () => void } = $props();
</script>

<div class="single-zip-header">
  <button type="button" class="back" aria-label="Back to zip code list" onclick={onBack}>
    <span class="chevron-left"><ChevronRightIcon /></span>
  </button>
  <span class="zip">{zip}</span>
</div>

<style>
  .single-zip-header {
    display: flex;
    align-items: center;
    gap: var(--space-200);
    padding-top: 3.5px;
    padding-bottom: var(--space-200);
    border-bottom: 0.5px solid var(--color-on-surface-secondary);
  }
  .back {
    flex-shrink: 0;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: var(--space-100);
    margin: calc(-1 * var(--space-100));
    background: none;
    border: none;
    color: var(--color-on-surface-primary);
  }
  .chevron-left {
    display: inline-flex;
    transform: scaleX(-1); /* right chevron → left (back) */
  }
  .zip {
    flex: 1 0 0;
    min-width: 0;
    font-size: var(--type-small-size);
    font-weight: var(--type-small-bold-weight);
    color: var(--color-on-surface-primary);
  }
  @media (pointer: coarse) {
    .back {
      padding: 10px;
      margin: -10px;
    }
  }
</style>

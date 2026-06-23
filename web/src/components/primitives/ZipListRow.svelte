<script lang="ts">
  import ChevronRightIcon from '../icons/ChevronRightIcon.svelte';

  /**
   * Selectable zip-code row: a real <button>, keyboard-focusable, with
   * a selected state exposed via aria-current. Selecting drills into zip-detail.
   */
  let {
    zip,
    selected = false,
    onSelect,
    onHover,
    onHoverEnd
  }: {
    zip: string;
    selected?: boolean;
    onSelect?: () => void;
    onHover?: () => void;
    onHoverEnd?: () => void;
  } = $props();
</script>

<button
  type="button"
  class="zip-row"
  class:is-selected={selected}
  aria-current={selected ? 'true' : undefined}
  onclick={onSelect}
  onmouseenter={onHover}
  onmouseleave={onHoverEnd}
  onfocus={onHover}
  onblur={onHoverEnd}
>
  <span class="zip">{zip}</span>
  <span class="chevron"><ChevronRightIcon /></span>
</button>

<style>
  .zip-row {
    display: flex;
    align-items: center;
    gap: 10px;
    width: 100%;
    padding-block: 3.5px;
    background: var(--color-surface-base);
    border: none;
    text-align: left;
    color: var(--color-on-surface-primary);
  }
  .zip {
    flex: 1 0 0;
    min-width: 0;
    font-size: var(--type-small-size);
  }
  .chevron {
    flex-shrink: 0;
    display: inline-flex;
    color: var(--color-on-surface-secondary);
  }
  .zip-row:hover {
    background: color-mix(in srgb, var(--color-on-surface-primary) 5%, var(--color-surface-base));
  }
  .is-selected .zip {
    font-weight: var(--type-small-bold-weight);
  }
  .is-selected .chevron {
    color: var(--color-on-surface-primary);
  }
  @media (pointer: coarse) {
    .zip-row {
      min-height: 44px;
    }
  }
</style>

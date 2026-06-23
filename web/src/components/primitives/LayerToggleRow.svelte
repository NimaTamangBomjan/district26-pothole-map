<script lang="ts">
  /**
   * A layer on/off control. Real <button> with aria-pressed.
   *
   * Indicator: polygon/raster layers show a color *swatch* (the layer's
   * accent token, shared with the MapLibre paint); point layers show a 2-char
   * *icon* code in the mono icon font.
   */
  type Indicator =
    | { type: 'swatch'; color: string }
    | { type: 'icon'; code: string };

  let {
    label,
    indicator,
    on = false,
    onToggle
  }: {
    label: string;
    indicator: Indicator;
    on?: boolean;
    onToggle?: () => void;
  } = $props();
</script>

<button
  type="button"
  class="layer-toggle"
  class:is-on={on}
  aria-pressed={on}
  onclick={onToggle}
>
  {#if indicator.type === 'swatch'}
    <span class="indicator swatch" style="background: {indicator.color};" aria-hidden="true"></span>
  {:else}
    <span class="indicator icon" aria-hidden="true">{indicator.code}</span>
  {/if}
  <span class="label">{label}</span>
</button>

<style>
  .layer-toggle {
    display: flex;
    align-items: center;
    gap: var(--space-100);
    width: 100%;
    padding: var(--space-50) var(--space-100) var(--space-100) 0;
    background: var(--color-surface-base);
    border: none;
    border-bottom: 0.5px solid var(--color-on-surface-primary);
    text-align: left;
  }
  .indicator {
    flex-shrink: 0;
    width: 16px;
    height: 16px;
    opacity: 0.35;
  }
  .swatch {
    border-radius: 2px;
  }
  .icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border: 0.5px solid var(--color-on-surface-primary);
    border-radius: 1px;
    font-family: var(--font-family-icon);
    font-style: italic;
    font-size: 8.5px;
    line-height: 0;
    color: var(--color-on-surface-primary);
  }
  .label {
    font-size: var(--type-small-size);
    font-weight: var(--type-small-weight);
    color: var(--color-on-surface-primary);
    white-space: nowrap;
  }

  .is-on .indicator {
    opacity: 1;
  }
  .is-on .label {
    font-weight: var(--type-small-bold-weight);
  }
  /* ≥44px touch target on coarse pointers (mobile layer rows). */
  @media (pointer: coarse) {
    .layer-toggle {
      min-height: 44px;
    }
  }
</style>

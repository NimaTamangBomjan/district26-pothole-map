<script lang="ts">
  /** Point-feature attribute popup (Figma 106:2117): translucent bordered box,
   *  one row per attribute = bold 150px label + value. */
  let { rows }: { rows: { label: string; value: string }[] } = $props();
</script>

<div class="popup">
  {#each rows as r, i (i)}
    <div class="row">
      <span class="label">{r.label}</span>
      <span class="value">{r.value}</span>
    </div>
  {/each}
</div>

<style>
  .popup {
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    gap: var(--space-100);
    padding: 6px var(--space-300);
    background: rgb(255 255 255 / 0.95);
    border: 0.4px solid var(--color-on-surface-primary);
    border-radius: 1px;
    overflow: clip;
    /* Pin font + line-height: MapLibre's base style sets the map container to
       `font: 12px/20px Helvetica Neue`, which the popup would otherwise inherit —
       the 20px line-height was the extra inter-row gap, and the family was wrong. */
    font-family: var(--font-family-base);
    font-size: var(--type-small-size);
    line-height: var(--type-line-height);
    color: var(--color-on-surface-primary);
  }
  .row {
    display: flex;
    gap: 0;
    align-items: center;
    width: 100%;
    padding-block: var(--space-100);
    /* Transparent so the translucent popup background shows through (rows had a
       solid white fill from Figma that conflicted with the 80%-white box). */
    background: transparent;
  }
  .label {
    flex-shrink: 0;
    width: 150px;
    font-weight: var(--type-small-bold-weight);
  }
  .value {
    white-space: nowrap;
  }
</style>

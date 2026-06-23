<script lang="ts">
  /**
   * Bordered text button.
   */
  let {
    label,
    onclick,
    type = 'button'
  }: {
    label: string;
    onclick?: () => void;
    type?: 'button' | 'submit';
  } = $props();
</script>

<button {type} class="border-button" {onclick}>{label}</button>

<style>
  .border-button {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 8px 6px;
    border: 0.75px solid var(--color-on-surface-primary);
    border-radius: 3px;
    background: var(--color-surface-base);
    font-size: var(--type-body-size);
    color: var(--color-on-surface-primary);
    white-space: nowrap;
  }
  /* Inferred states (not in Figma). */
  .border-button:hover {
    background: color-mix(in srgb, var(--color-on-surface-primary) 6%, var(--color-surface-base));
  }
  .border-button:active {
    background: color-mix(in srgb, var(--color-on-surface-primary) 12%, var(--color-surface-base));
  }
</style>

<script lang="ts">
  /**
   * Descriptive context copy. Two independent instances exist (per design): one
   * inside the sidebar (view description) and one in the desktop bottom band
   * (layer/legend description) — distinct paragraphs, not duplicates. 
   */
  let { text, size = 'caption' }: { text?: string; size?: 'caption' | 'small' } = $props();

  const placeholder =
    'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed consequat turpis libero, in tempor ante tristique vitae. Aenean tincidunt felis et neque condimentum placerat.';
</script>

<!-- {@html} so the copy can use inline markup (<strong>, <br>, etc.). Safe here:
     the text is author-controlled copy from lib/copy.ts, never user input. -->
<p class="context-text" class:is-caption={size === 'caption'} class:is-small={size === 'small'}>
  {@html text ?? placeholder}
</p>

<style>
  .context-text {
    margin: 0;
    color: var(--color-on-surface-primary);
    line-height: 1.35;
    white-space: pre-wrap;
  }
  .is-caption { font-size: var(--type-caption-size); }
  .is-small { font-size: var(--type-small-size); }
</style>

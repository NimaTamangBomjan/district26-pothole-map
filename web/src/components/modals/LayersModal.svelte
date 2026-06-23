<script lang="ts">
  import Modal from '../primitives/Modal.svelte';
  import LayerToggleRow from '../primitives/LayerToggleRow.svelte';
  import ContextText from '../ContextText.svelte';
  import { LAYERS } from '../../lib/layers';
  import { LAYERS_CONTEXT } from '../../lib/copy';
  import { visibleLayers, toggleLayer, closeModal } from '../../stores';

  // Mobile Layers modal (Figma 66:1716): the 11 toggle rows + context, in the
  // bottom-sheet placement. Same registry/store as the desktop bottom band.
</script>

<Modal title="Layers" placement="sheet" onClose={closeModal}>
  <div class="rows">
    {#each LAYERS as l (l.id)}
      <LayerToggleRow
        label={l.label}
        indicator={l.indicator.type === 'swatch'
          ? { type: 'swatch', color: `var(${l.indicator.colorVar})` }
          : l.indicator}
        on={$visibleLayers.has(l.id)}
        onToggle={() => toggleLayer(l.id)}
      />
    {/each}
  </div>
  <div class="context">
    <ContextText text={LAYERS_CONTEXT} size="caption" />
  </div>
</Modal>

<style>
  .rows {
    display: flex;
    flex-direction: column;
  }
  .context {
    margin-top: var(--space-200);
  }
</style>

<script lang="ts">
  import ZipListRow from '../primitives/ZipListRow.svelte';
  import { ZCTAS } from '../../lib/indicators';
  import { selectedZip, selectZip, hoveredZip } from '../../stores';
</script>

<div class="rows">
  {#each ZCTAS as zip (zip)}
    <ZipListRow
      {zip}
      selected={$selectedZip === zip}
      onSelect={() => selectZip(zip)}
      onHover={() => hoveredZip.set(zip)}
      onHoverEnd={() => hoveredZip.set(null)}
    />
  {/each}
</div>

<style>
  .rows {
    display: flex;
    flex-direction: column;
  }
</style>

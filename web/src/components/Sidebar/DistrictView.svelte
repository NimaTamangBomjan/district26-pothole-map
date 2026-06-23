<script lang="ts">
  import StatRow from '../primitives/StatRow.svelte';
  import ContextText from '../ContextText.svelte';
  import Skeleton from '../Skeleton.svelte';
  import { INDICATORS } from '../../lib/indicators';
  import { formatStat } from '../../lib/format';
  import { DISTRICT_CONTEXT } from '../../lib/copy';
  import { districtAttrs, attrsLoading } from '../../stores';

</script>

{#if $attrsLoading}
  <Skeleton rows={INDICATORS.length} />
{:else}
  <div class="rows">
    {#each INDICATORS as ind (ind.key)}
      <StatRow
        label={ind.label}
        value={$districtAttrs ? formatStat($districtAttrs[ind.statColumn], ind.format) : '—'}
      />
    {/each}
  </div>
  <div class="context">
    <ContextText text={DISTRICT_CONTEXT} size="caption" />
  </div>
{/if}

<style>
  .rows {
    display: flex;
    flex-direction: column;
  }
  .context {
    margin-top: var(--space-100);
    padding-top: 6px;
    border-top: 0.5px solid var(--color-on-surface-secondary);
  }
</style>

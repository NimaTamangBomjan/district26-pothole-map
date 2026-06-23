<script lang="ts">
  import SingleZipHeader from '../primitives/SingleZipHeader.svelte';
  import RankRow from '../primitives/RankRow.svelte';
  import ContextText from '../ContextText.svelte';
  import Skeleton from '../Skeleton.svelte';
  import { INDICATORS } from '../../lib/indicators';
  import { ZIP_CONTEXT } from '../../lib/copy';
  import { selectedZip, backToList, zctaAttrs, attrsLoading } from '../../stores';

  // The selected ZCTA's ranks from d26_zctas_attrs.parquet. 
  // Skeleton while loading; null rank → empty widget.
  let row = $derived($zctaAttrs && $selectedZip ? ($zctaAttrs.get($selectedZip) ?? null) : null);
</script>

<SingleZipHeader zip={$selectedZip ?? ''} onBack={backToList} />
{#if $attrsLoading}
  <Skeleton rows={INDICATORS.length} />
{:else}
  <div class="rows">
    {#each INDICATORS as ind (ind.key)}
      <RankRow
        label={ind.label}
        value={row && typeof row[ind.rankColumn] === 'number' ? (row[ind.rankColumn] as number) : null}
      />
    {/each}
  </div>
  <div class="context">
    <ContextText text={ZIP_CONTEXT} size="caption" />
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

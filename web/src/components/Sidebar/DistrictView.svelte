<script lang="ts">
  import { onMount } from 'svelte';
  import StatRow from '../primitives/StatRow.svelte';
  import ContextText from '../ContextText.svelte';
  import Skeleton from '../Skeleton.svelte';
  import { INDICATORS } from '../../lib/indicators';
  import { formatStat } from '../../lib/format';
  import { DISTRICT_CONTEXT } from '../../lib/copy';
  import { districtAttrs, attrsLoading } from '../../stores';

  type PotholeStats = {
    total: number;
    open: number;
    inProgress: number;
    closed: number;
    highPriority: number;
    mediumPriority: number;
    lowPriority: number;
  };

  let potholeStats: PotholeStats | null = null;
  let trackerExpanded = false;

  function normalizeStatus(value: unknown) {
    return String(value ?? '').trim().toLowerCase();
  }

  function normalizePriority(value: unknown) {
    return String(value ?? '').trim().toLowerCase();
  }

  onMount(async () => {
    try {
      const res = await fetch('data/potholes.geojson');
      if (!res.ok) return;

      const data = await res.json();
      const features = Array.isArray(data.features) ? data.features : [];

      const stats: PotholeStats = {
        total: features.length,
        open: 0,
        inProgress: 0,
        closed: 0,
        highPriority: 0,
        mediumPriority: 0,
        lowPriority: 0
      };

      for (const feature of features) {
        const props = feature?.properties ?? {};
        const status = normalizeStatus(props.status);
        const priority = normalizePriority(props.priority);

        if (status === 'open' || status === 'reported') {
          stats.open += 1;
        } else if (status === 'in progress' || status === 'in-progress') {
          stats.inProgress += 1;
        } else if (status === 'closed' || status === 'completed' || status === 'repaired') {
          stats.closed += 1;
        }

        if (priority === 'high') {
          stats.highPriority += 1;
        } else if (priority === 'medium') {
          stats.mediumPriority += 1;
        } else if (priority === 'low') {
          stats.lowPriority += 1;
        }
      }

      potholeStats = stats;
    } catch {
      potholeStats = null;
    }
  });
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

    <button
      type="button"
      class="tracker-row"
      aria-expanded={trackerExpanded}
      onclick={() => (trackerExpanded = !trackerExpanded)}
    >
      <span class="label">
        <span class="chevron" class:is-open={trackerExpanded}>›</span>
        Pothole Repair Tracker
      </span>
      <span class="value">{potholeStats ? String(potholeStats.total) : '—'}</span>
    </button>

    {#if trackerExpanded}
      <div class="tracker-details">
        <StatRow label="Open" value={potholeStats ? String(potholeStats.open) : '—'} />
        <StatRow label="In Progress" value={potholeStats ? String(potholeStats.inProgress) : '—'} />
        <StatRow label="Closed" value={potholeStats ? String(potholeStats.closed) : '—'} />
        <StatRow label="High Priority" value={potholeStats ? String(potholeStats.highPriority) : '—'} />
        <StatRow label="Medium Priority" value={potholeStats ? String(potholeStats.mediumPriority) : '—'} />
        <StatRow label="Low Priority" value={potholeStats ? String(potholeStats.lowPriority) : '—'} />
      </div>
    {/if}
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

  .tracker-row {
    display: flex;
    align-items: center;
    gap: 10px;
    padding-block: var(--space-100);
    padding-inline: 0;
    border: 0;
    background: transparent;
    font: inherit;
    font-size: var(--type-small-size);
    color: var(--color-on-surface-primary);
    text-align: left;
    cursor: pointer;
  }

  .label {
    flex: 1 0 0;
    min-width: 0;
    display: flex;
    align-items: center;
    gap: 4px;
  }

  .value {
    flex-shrink: 0;
    text-align: right;
    font-variant-numeric: tabular-nums;
  }

  .chevron {
    display: inline-block;
    color: var(--color-on-surface-secondary);
    transform: rotate(0deg);
    transition: transform 0.15s ease;
  }

  .chevron.is-open {
    transform: rotate(90deg);
  }

  .tracker-details {
    padding-left: 16px;
    border-left: 0.5px solid var(--color-on-surface-secondary);
  }

  .context {
    margin-top: var(--space-100);
    padding-top: 6px;
    border-top: 0.5px solid var(--color-on-surface-secondary);
  }
</style>

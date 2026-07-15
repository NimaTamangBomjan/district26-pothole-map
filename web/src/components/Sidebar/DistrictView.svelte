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
    averageDaysOpen: number | null;
    oldestOpenDays: number | null;
    officeTracked: number;
    dateStart: string;
    dateEnd: string;
  };

  let potholeStats: PotholeStats | null = null;
  let trackerExpanded = false;

  function normalizeStatus(value: unknown) {
    return String(value ?? '').trim().toLowerCase();
  }

  function formatDate(value: string) {
    if (!value) return '—';

    const [year, month, day] = value.split('-');

    if (!year || !month || !day) return value;

    return `${Number(month)}/${Number(day)}/${year}`;
  }

  function formatDateRange(stats: PotholeStats) {
    if (!stats.dateStart || !stats.dateEnd) return 'Last 30 days';

    return `${formatDate(stats.dateStart)} – ${formatDate(stats.dateEnd)}`;
  }

  function formatNumber(value: number | null) {
    return value === null ? '—' : String(value);
  }

  onMount(async () => {
    try {
      const res = await fetch('data/potholes.geojson');
      if (!res.ok) return;

      const data = await res.json();
      const features = Array.isArray(data.features) ? data.features : [];

      const dates: string[] = [];
      const openDays: number[] = [];

      const stats: PotholeStats = {
        total: features.length,
        open: 0,
        inProgress: 0,
        closed: 0,
        averageDaysOpen: null,
        oldestOpenDays: null,
        officeTracked: 0,
        dateStart: '',
        dateEnd: ''
      };

      for (const feature of features) {
        const props = feature?.properties ?? {};
        const status = normalizeStatus(props.status);
        const dateValue = String(props.city_created_date ?? props.reported_date ?? '').trim();
        const daysOpen = Number(props.days_open ?? 0);

        if (dateValue) {
          dates.push(dateValue);
        }

        if (props.office_tracked === true || props.office_tracked === 'true') {
          stats.officeTracked += 1;
        }

        if (status === 'open' || status === 'reported') {
          stats.open += 1;

          if (Number.isFinite(daysOpen)) {
            openDays.push(daysOpen);
          }
        } else if (status === 'in progress' || status === 'in-progress') {
          stats.inProgress += 1;

          if (Number.isFinite(daysOpen)) {
            openDays.push(daysOpen);
          }
        } else if (status === 'closed' || status === 'completed' || status === 'repaired') {
          stats.closed += 1;
        }
      }

      dates.sort((a, b) => a.localeCompare(b));

      stats.dateStart = dates[0] ?? '';
      stats.dateEnd = dates[dates.length - 1] ?? '';

      if (openDays.length > 0) {
        stats.averageDaysOpen = Math.round((openDays.reduce((sum, value) => sum + value, 0) / openDays.length) * 10) / 10;
        stats.oldestOpenDays = Math.max(...openDays);
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
        311 Potholes - Last 30 Days
      </span>
      <span class="value">{potholeStats ? String(potholeStats.total) : '—'}</span>
    </button>

    {#if trackerExpanded}
      <div class="tracker-details">
        <StatRow label="Open" value={potholeStats ? String(potholeStats.open) : '—'} />
        {#if potholeStats && potholeStats.inProgress > 0}
          <StatRow label="In Progress" value={String(potholeStats.inProgress)} />
        {/if}
        <StatRow label="Closed" value={potholeStats ? String(potholeStats.closed) : '—'} />
        <StatRow label="Average Days Open" value={potholeStats ? formatNumber(potholeStats.averageDaysOpen) : '—'} />
        <StatRow label="Oldest Open Request" value={potholeStats && potholeStats.oldestOpenDays !== null ? `${potholeStats.oldestOpenDays} days` : '—'} />
        {#if potholeStats && potholeStats.officeTracked > 0}
          <StatRow label="Office Tracked" value={String(potholeStats.officeTracked)} />
        {/if}
        <StatRow label="Date Range" value={potholeStats ? formatDateRange(potholeStats) : '—'} />
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

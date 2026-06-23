export type StatFormat = 'percent' | 'count' | 'density' | 'decimal';

/**
 * Format a district raw stat value for display. 
 * Non-numbers (missing data) render as an em dash.
 */
export function formatStat(value: unknown, kind: StatFormat): string {
  if (typeof value !== 'number' || Number.isNaN(value)) return '—';
  switch (kind) {
    case 'percent':
      return `${value.toFixed(1)}%`;
    case 'count':
      return Math.round(value).toLocaleString('en-US');
    case 'density':
    case 'decimal':
      return value.toFixed(1);
  }
}

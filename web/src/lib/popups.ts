export interface PopupField {
  key: string;
  label: string;
  format?: (value: unknown) => string;
  hideWhenEmpty?: boolean;
}

export function formatIsoDate(value: unknown): string {
  return typeof value === 'string' && value.length >= 10 ? value.slice(0, 10) : '—';
}

const EASTERN_FMT = new Intl.DateTimeFormat('en-CA', {
  timeZone: 'America/New_York',
  year: 'numeric',
  month: '2-digit',
  day: '2-digit',
  hour: '2-digit',
  minute: '2-digit',
  hourCycle: 'h23',
  timeZoneName: 'short'
});

export function formatEastern(value: unknown): string {
  if (typeof value !== 'string' || value.length < 10) return '—';

  const d = new Date(value);

  if (Number.isNaN(d.getTime())) return '—';

  const parts = EASTERN_FMT.formatToParts(d);
  const get = (t: string) => parts.find((p) => p.type === t)?.value ?? '';

  return `${get('year')}-${get('month')}-${get('day')} ${get('hour')}:${get('minute')} ${get('timeZoneName')}`;
}

export const POPUP_FIELDS: Record<string, PopupField[]> = {
  gi: [
    { key: 'asset_type', label: 'Asset Type' },
    { key: 'constructed_date', label: 'Constructed Date', format: formatIsoDate }
  ],
  catch_basins: [
    { key: 'unitid', label: 'Unit ID' }
  ],
  flooding_311: [
    { key: 'descriptor', label: 'Descriptor' },
    { key: 'agency', label: 'Agency' },
    { key: 'created_date', label: 'Opened', format: formatEastern },
    { key: 'closed_date', label: 'Closed', format: formatEastern }
  ],
  potholes: [
    { key: 'address', label: 'Location', hideWhenEmpty: true },
    { key: 'status', label: 'Status' },
    { key: 'sr_number', label: '311 SR Number' },
    { key: 'reported_date', label: '311 Created Date' },
    { key: 'closed_date', label: 'Closed Date', hideWhenEmpty: true },
    { key: 'source', label: 'Source' },
    { key: 'office_source', label: 'Office Tracked By', hideWhenEmpty: true },
    { key: 'office_role', label: 'Office Role', hideWhenEmpty: true },
    { key: 'office_added_date', label: 'Office Added Date', hideWhenEmpty: true },
    { key: 'notes_public', label: 'Notes', hideWhenEmpty: true }
  ],
  cso: [
    { key: 'Waterbody', label: 'Waterbody' },
    { key: 'Waterbod_1', label: 'Waterbody (Secondary)' }
  ]
};

export function buildPopupRows(
  layerId: string,
  props: Record<string, unknown>
): { label: string; value: string }[] {
  const fields = POPUP_FIELDS[layerId] ?? [];

  return fields.flatMap((f) => {
    const raw = props[f.key];
    const isEmpty = raw == null || raw === '';

    if (f.hideWhenEmpty && isEmpty) {
      return [];
    }

    const value = f.format ? f.format(raw) : isEmpty ? '—' : String(raw);

    return [{ label: f.label, value }];
  });
}

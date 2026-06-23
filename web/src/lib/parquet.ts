import { asyncBufferFromUrl, parquetReadObjects } from 'hyparquet';
import { freshDataUrl } from './config';

/** One parsed parquet row. ZCTA5 is a string; numeric columns are numbers. */
export type AttrRow = Record<string, number | string | null>;

/** Per-ZCTA attributes + ranks, keyed by ZCTA5 string (6 rows). */
export async function loadZctaAttrs(): Promise<Map<string, AttrRow>> {
  const file = await asyncBufferFromUrl({ url: freshDataUrl('d26_zctas_attrs.parquet') });
  const rows = (await parquetReadObjects({ file })) as AttrRow[];
  return new Map(rows.map((r) => [String(r.ZCTA5), r]));
}

/** District-level aggregates (1 row, no ranks). */
export async function loadDistrictAttrs(): Promise<AttrRow> {
  const file = await asyncBufferFromUrl({ url: freshDataUrl('d26_attrs.parquet') });
  const rows = (await parquetReadObjects({ file })) as AttrRow[];
  return rows[0];
}

import { parquetReadObjects } from 'hyparquet';
import { freshDataUrl } from './config';

/** One parsed parquet row. ZCTA5 is a string; numeric columns are numbers. */
export type AttrRow = Record<string, number | string | null>;

/**
 * Fetch a (small) parquet fully and parse it from an in-memory buffer.
 *
 * We deliberately do NOT use hyparquet's asyncBufferFromUrl (HTTP range requests):
 * GitHub Pages gzip-compresses these files and computes ranges against the
 * *compressed* bytes, so range reads return the wrong length/offset (the footer
 * read fails with "footer != PAR1"). A plain full GET lets the browser
 * transparently decompress gzip and yields the correct bytes. These attribute
 * parquets are only a few KB, so downloading the whole file is ideal anyway.
 */
async function readParquet(file: string): Promise<AttrRow[]> {
  const res = await fetch(freshDataUrl(file));
  if (!res.ok) throw new Error(`fetch ${file} failed: ${res.status}`);
  const ab = await res.arrayBuffer();
  return parquetReadObjects({
    file: { byteLength: ab.byteLength, slice: (start, end) => ab.slice(start, end) }
  }) as Promise<AttrRow[]>;
}

/** Per-ZCTA attributes + ranks, keyed by ZCTA5 string (6 rows). */
export async function loadZctaAttrs(): Promise<Map<string, AttrRow>> {
  const rows = await readParquet('d26_zctas_attrs.parquet');
  return new Map(rows.map((r) => [String(r.ZCTA5), r]));
}

/** District-level aggregates (1 row, no ranks). */
export async function loadDistrictAttrs(): Promise<AttrRow> {
  const rows = await readParquet('d26_attrs.parquet');
  return rows[0];
}

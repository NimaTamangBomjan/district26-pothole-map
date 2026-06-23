/**
 * Single source of truth for where the pipeline's data artifacts are served.
 * In dev and in the Vite build, `public/data` is a symlink to the pipeline's
 * `data/processed/` output dir, so all artifacts resolve under `<base>data/`.
 * `import.meta.env.BASE_URL` is Vite's configured `base` ('./' here), which
 * keeps paths relative for GitHub Pages. To relocate the data, change this one
 * constant.
 */
export const DATA_BASE = `${import.meta.env.BASE_URL}data/`;

/** Build an absolute-from-base URL for a named artifact, e.g. dataUrl('d26_zctas.pmtiles'). */
export function dataUrl(file: string): string {
  return `${DATA_BASE}${file}`;
}

/**
 * Build identifier for cache-busting the most update-prone artifacts — the
 * Parquet and the 311 GeoJSON. Set VITE_BUILD_VERSION=<sha> in CI; falls
 * back to 'dev' locally. PMTiles/COG are left to range-request + ETag caching.
 */
export const BUILD_VERSION = import.meta.env.VITE_BUILD_VERSION ?? 'dev';

/** dataUrl with a `?v=<build>` cache-buster, for files that change each pipeline run. */
export function freshDataUrl(file: string): string {
  return `${dataUrl(file)}?v=${BUILD_VERSION}`;
}

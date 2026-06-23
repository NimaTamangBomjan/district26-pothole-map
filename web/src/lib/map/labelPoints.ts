import type { FeatureCollection, Point } from 'geojson';

/**
 * Label anchor points — one per feature — so the map shows exactly ONE label per
 * feature. (MapLibre places a label per tile a polygon spans; labeling a points
 * source instead avoids the duplicates, the same idea as the boundaries map's
 * centerpoints source.) Points are `st_centroid` of each geometry (EPSG:4326),
 * computed from the pipeline's d26_zctas / d26 geometry.
 *
 * NOTE: baked in for now (Option C). The D26 boundaries are a static Tier-2
 * snapshot, so this is safe, but it must be regenerated if the boundaries change
 * — ideally promoted to a pipeline-emitted GeoJSON later.
 */
export const ZCTA_LABEL_POINTS: FeatureCollection<Point, { ZCTA5: string }> = {
  type: 'FeatureCollection',
  features: (
    [
      ['11101', -73.93915, 40.74672],
      ['11109', -73.957, 40.74628],
      ['11377', -73.90516, 40.74477],
      ['11106', -73.9317, 40.76193],
      ['11104', -73.92047, 40.74484],
      ['11378', -73.91025, 40.7249]
    ] as [string, number, number][]
  ).map(([ZCTA5, lon, lat]) => ({
    type: 'Feature',
    properties: { ZCTA5 },
    geometry: { type: 'Point', coordinates: [lon, lat] }
  }))
};

export const DISTRICT_LABEL_POINT: FeatureCollection<Point, { CounDist: string }> = {
  type: 'FeatureCollection',
  features: [
    {
      type: 'Feature',
      properties: { CounDist: '26' },
      geometry: { type: 'Point', coordinates: [-73.92487, 40.74284] }
    }
  ]
};

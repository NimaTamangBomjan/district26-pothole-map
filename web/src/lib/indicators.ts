export interface Indicator {
  key: string;
  label: string;
  /** rank_* column in d26_zctas_attrs.parquet (zip-detail Rank Rows). */
  rankColumn: string;
  /** raw value column in d26_attrs.parquet (district Stat Rows). */
  statColumn: string;
  /** display format for the district raw value. */
  format: 'percent' | 'count' | 'density' | 'decimal';
}

export const INDICATORS: Indicator[] = [
  { key: 'gi', label: 'Green Infrastructure', rankColumn: 'rank_n_gi_sqmi', statColumn: 'n_gi_sqmi', format: 'density' },
  { key: 'flooding_311', label: '311 Service Requests (Flooding-Related)', rankColumn: 'rank_n_flooding_311_p10k', statColumn: 'n_flooding_311_p10k', format: 'density' },
  { key: 'catch_basins', label: 'Catch Basins', rankColumn: 'rank_n_cb_sqmi', statColumn: 'n_cb_sqmi', format: 'density' },
  { key: 'fvi', label: 'Mean Flood Vulnerability Index', rankColumn: 'rank_mean_fshri', statColumn: 'mean_fshri', format: 'decimal' },
  { key: 'fema_100', label: '100-Year Flood Plane', rankColumn: 'rank_pct_100_year', statColumn: 'pct_100_year', format: 'percent' },
  { key: 'fema_500', label: '500-Year Flood Plane', rankColumn: 'rank_pct_500_year', statColumn: 'pct_500_year', format: 'percent' },
  { key: 'swf_limited', label: 'Stormwater Flooding (Limited)', rankColumn: 'rank_limited_swf_pct', statColumn: 'limited_swf_pct', format: 'percent' },
  { key: 'swf_moderate', label: 'Stormwater Flooding (Moderate)', rankColumn: 'rank_moderate_swf_pct', statColumn: 'moderate_swf_pct', format: 'percent' },
  { key: 'permeable', label: 'Permeable Surface', rankColumn: 'rank_pct_permeable_surface', statColumn: 'pct_permeable_surface', format: 'percent' },
  { key: 'tree_canopy', label: 'Tree Canopy', rankColumn: 'rank_pct_tree_canopy', statColumn: 'pct_tree_canopy', format: 'percent' }
];

/**
 * The 6 D26 ZCTAs (join key ZCTA5, string).
 */
export const ZCTAS = ['11101', '11104', '11106', '11109', '11377', '11378'];

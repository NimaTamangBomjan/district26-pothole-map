/**
 * Basemap style.
 *
 * CARTO Positron — a MapLibre-native GL style, no API key, light-gray streets
 * look. (The nyc-boundaries reference uses a Mapbox-hosted "Boundaries Map"
 * style — a light monochrome, hue 185°, gray water — that needs mapbox-gl + a
 * token and isn't usable under MapLibre. See the reference_basemap_style memory
 * for the palette to reproduce.)
 *
 * Centralized so the planned swap to a self-hosted Protomaps basemap is a
 * one-line change.
 */
export const BASEMAP_STYLE = 'https://basemaps.cartocdn.com/gl/positron-gl-style/style.json';

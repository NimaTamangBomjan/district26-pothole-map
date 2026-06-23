/**
 * Read a CSS custom property (design token) off :root so it can be used in a
 * MapLibre paint expression. This keeps the token the single source of truth for
 * a layer's color in BOTH the UI swatch (var(--…)) and the map symbology.
 */
export function cssVar(name: string): string {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
}

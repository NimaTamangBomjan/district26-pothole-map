/**
 * Generate a point-marker image matching the Figma layer icon: a 16px white,
 * 0.5px-bordered, 1px-radius box with the 2–3 char code in the mono icon font.
 * Rendered on a canvas at 2× and registered via map.addImage(id, img, {pixelRatio:2}),
 * which reuses the already-loaded NewComputerModernMono10 web font (symbol layers
 * can't, since the basemap glyphs don't include it).
 */
/** Device-pixel-ratio for the marker image; addImage must be told via { pixelRatio }. */
export const ICON_PIXEL_RATIO = 2;

/** Rendered native marker size in px. The Figma icon is a 16px box; we render it
 *  larger (20px → a 40px canvas at 2×) and let the icon-size ramp scale it with zoom. */
export const ICON_NATIVE_PX = 20;
const LOGICAL_SIZE = ICON_NATIVE_PX;

/** The icon-size zoom ramp — shared by the layer paint (dataLayers) AND the popup
 *  offset (popups) so the two never drift. Native size at zoom ≤ zMin, ×sMax at zMax. */
export const ICON_SIZE_RAMP = { zMin: 15, sMin: 1, zMax: 20, sMax: 1.75 };

/** Rendered icon size in CSS px at a given zoom (mirrors the icon-size ramp). */
export function iconSizePx(zoom: number): number {
  const { zMin, sMin, zMax, sMax } = ICON_SIZE_RAMP;
  const f =
    zoom <= zMin ? sMin : zoom >= zMax ? sMax : sMin + ((sMax - sMin) * (zoom - zMin)) / (zMax - zMin);
  return ICON_NATIVE_PX * f;
}

export function makeIconMarker(
  code: string,
  colors: { fill: string; border: string; text: string }
): ImageData {
  // Figma metrics (16px box, 0.5px border, 1px radius, 8.5px code) scaled to the
  // LOGICAL_SIZE footprint and the pixel ratio — i.e. the 16px design, bigger.
  const k = (LOGICAL_SIZE / 16) * ICON_PIXEL_RATIO;
  const size = 16 * k; // = LOGICAL_SIZE * ICON_PIXEL_RATIO = 40
  const canvas = document.createElement('canvas');
  canvas.width = size;
  canvas.height = size;
  const ctx = canvas.getContext('2d')!;

  const inset = 0.5 * k;
  roundRect(ctx, inset, inset, size - 2 * inset, size - 2 * inset, 1 * k);
  ctx.fillStyle = colors.fill;
  ctx.fill();
  ctx.lineWidth = 0.5 * k;
  ctx.strokeStyle = colors.border;
  ctx.stroke();

  ctx.fillStyle = colors.text;
  ctx.font = `italic ${8.5 * k}px "NewComputerModernMono10", monospace`;
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText(code, size / 2, size / 2 + 0.5 * k);

  return ctx.getImageData(0, 0, size, size);
}

function roundRect(ctx: CanvasRenderingContext2D, x: number, y: number, w: number, h: number, r: number) {
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.arcTo(x + w, y, x + w, y + h, r);
  ctx.arcTo(x + w, y + h, x, y + h, r);
  ctx.arcTo(x, y + h, x, y, r);
  ctx.arcTo(x, y, x + w, y, r);
  ctx.closePath();
}

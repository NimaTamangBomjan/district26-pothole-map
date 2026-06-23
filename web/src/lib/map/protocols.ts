import maplibregl from 'maplibre-gl';
import { Protocol } from 'pmtiles';
import { cogProtocol } from '@geomatico/maplibre-cog-protocol';

let registered = false;

/**
 * Register the `pmtiles://` and `cog://` protocols once, globally. Idempotent so
 * it's safe to call on every map mount.
 */
export function registerMapProtocols(): void {
  if (registered) return;
  const protocol = new Protocol();
  maplibregl.addProtocol('pmtiles', protocol.tile);
  maplibregl.addProtocol('cog', cogProtocol);
  registered = true;
}

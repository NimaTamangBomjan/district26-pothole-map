<script lang="ts">
  import Header from './components/Header.svelte';
  import Footer from './components/Footer.svelte';
  import Map from './components/Map.svelte';
  import Sidebar from './components/Sidebar/Sidebar.svelte';
  import LayerToolbar from './components/LayerToolbar.svelte';
  import LayersFab from './components/LayersFab.svelte';
  import LayersModal from './components/modals/LayersModal.svelte';
  import AboutModal from './components/modals/AboutModal.svelte';
  import { onMount } from 'svelte';
  import { view, selectedZip, attrsLoading, zctaAttrs, districtAttrs, activeModal, openModal } from './stores';
  import { loadZctaAttrs, loadDistrictAttrs } from './lib/parquet';

  // Load the attribute parquets once at startup (hyparquet). The sidebar
  // shows a loading skeleton until these resolve; Map.svelte joins the ranks to
  // the ZCTA features via setFeatureState when zctaAttrs lands.
  onMount(async () => {
    try {
      const [zctas, district] = await Promise.all([loadZctaAttrs(), loadDistrictAttrs()]);
      zctaAttrs.set(zctas);
      districtAttrs.set(district);
    } catch (e) {
      console.error('Failed to load attribute parquet:', e);
    } finally {
      attrsLoading.set(false);
    }
  });

  // Mirror view state into the URL query string (?view=…&zip=…) so deep
  // links and back/forward reflect the current view.
  $effect(() => {
    const params = new URLSearchParams(window.location.search);
    if ($view === 'district') params.delete('view');
    else params.set('view', $view);
    if ($selectedZip) params.set('zip', $selectedZip);
    else params.delete('zip');
    const qs = params.toString();
    history.replaceState({}, '', qs ? `${location.pathname}?${qs}` : location.pathname);
  });
</script>

<!-- inert while a modal is open: the background is non-interactive and removed
     from the a11y tree, reinforcing the dialog's focus containment. -->
<div class="app" inert={$activeModal !== null}>
  <Header onAbout={() => openModal('about')} />

  <div class="body">
    <div class="stage">
      <Map />
      <Sidebar />
      <LayersFab onClick={() => openModal('layers')} />
    </div>
    <div class="bottom-band-wrap">
      <LayerToolbar />
    </div>
  </div>

  <Footer />
</div>

{#if $activeModal === 'layers'}
  <LayersModal />
{:else if $activeModal === 'about'}
  <AboutModal />
{/if}

<style>
  .app {
    display: flex;
    flex-direction: column;
    height: 100%;
  }
  .body {
    flex: 1;
    min-height: 0;
    display: flex;
    flex-direction: column;
  }
  /* The map area: a relative positioning stage; map + overlays sit inside it. */
  .stage {
    position: relative;
    flex: 1;
    min-height: 0;
  }
  /* Mobile: edge-to-edge map, no bottom band (FAB + modal instead). */
  .bottom-band-wrap {
    display: none;
  }

  @media (min-width: 768px) {
    /* Desktop gutters around the map + bottom band. */
    .body {
      padding: 0 var(--space-400);
    }
    .bottom-band-wrap {
      display: block;
      padding: var(--space-300) 0;
    }
  }
</style>

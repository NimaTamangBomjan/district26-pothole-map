<script lang="ts">
  import Modal from '../primitives/Modal.svelte';
  import { closeModal } from '../../stores';

  // About modal (Figma 73:2003 desktop / 73:2099 mobile): centered on both
  // breakpoints. Copy is placeholder until the real About text is provided.
</script>

<Modal title="About" placement="centered" onClose={closeModal}>
  <div class="about">
    <p>
      The District 26 Green Infrastructure map shows where green infrastructure investment, 
      flood risk, and flood-mitigating assets overlap in and around the district.
      Until now, these disparate pieces of information have made it challenging for the Office of Council Member Julie Won,
      her constituents, and representatives from city agencies to be on the same page during discussions on vitally important flood-related concerns.
    </p>
    <p>
      Full documentation of this map's data sources and methodology can be found <a href="https://github.com/BetaNYC/d26-gi-web-map" target="_blank" rel="noopener noreferrer">here</a>, published alongside its fully open source code. 
    </p>
  </div>
</Modal>

<style>
  .about {
    display: flex;
    flex-direction: column;
    gap: var(--space-300);
    font-size: var(--type-body-size);
    line-height: 1.45;
    color: var(--color-on-surface-primary);
  }
  .about p {
    margin: 0;
  }
  .about a {
    color: var(--color-on-surface-beta-blue);
  }
</style>

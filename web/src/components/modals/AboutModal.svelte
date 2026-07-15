<script lang="ts">
  import Modal from '../primitives/Modal.svelte';
  import { closeModal } from '../../stores';

  // About modal (Figma 73:2003 desktop / 73:2099 mobile): centered on both
  // breakpoints. Copy is placeholder until the real About text is provided.
</script>

<Modal title="About" placement="centered" onClose={closeModal}>
  <div class="about">
    <p>
      The District 26 Pothole Tracker is an independent civic data project by <strong>Nima Tamang Bomjan</strong>.
      It uses NYC 311 Open Data to map recent pothole service requests in the District 26 area and adds an office-tracking workflow for matching selected 311 service request numbers from a public-safe CSV.
    </p>
    <p>
      This project is not an official NYC Council, NYC agency, or BetaNYC website.
      It is a student-built civic technology project created for public data exploration, transparency, and workflow demonstration.
    </p>
    <p>
      The map is adapted from the <strong>BetaNYC District 26 green infrastructure web map template</strong>.
      NYC 311 remains the source for pothole request data, while the office-tracked status comes only from the local CSV workflow added to this project.
    </p>
    <p>
      Project code and documentation are available
      <a href="https://github.com/NimaTamangBomjan/district26-pothole-map" target="_blank" rel="noopener noreferrer">on GitHub</a>.
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
  .about strong {
    font-weight: 600;
    color: var(--color-on-surface-primary);
  }
  .about a {
    color: var(--color-on-surface-beta-blue);
  }
</style>

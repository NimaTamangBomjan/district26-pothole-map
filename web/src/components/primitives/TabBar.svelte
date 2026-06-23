<script lang="ts">
  /**
   * Segmented underline tabs. role="tablist" with roving tabindex and
   * arrow-key navigation. `panelId` links the tabs to the tabpanel the
   * sidebar renders: each tab gets a stable id and aria-controls={panelId}, and
   * the panel sets aria-labelledby to the active tab's id (`tabId(panelId, sel)`).
   *
   * Note: inactive label uses on-surface-secondary (#707070, WCAG AA-passing)
   * rather than the Figma `rank/empty` #e2e2e2, which fails contrast.
   */
  type Tab = { id: string; label: string };

  let {
    tabs,
    selected,
    panelId,
    onChange
  }: {
    tabs: Tab[];
    selected: string;
    panelId: string;
    onChange?: (id: string) => void;
  } = $props();

  /** Stable element id for a tab (shared with the panel's aria-labelledby). */
  const tabElId = (id: string) => `${panelId}-tab-${id}`;

  let tabEls = $state<HTMLButtonElement[]>([]);

  function select(id: string) {
    if (id !== selected) onChange?.(id);
  }

  function onKeydown(e: KeyboardEvent, index: number) {
    let next = index;
    if (e.key === 'ArrowRight' || e.key === 'ArrowDown') next = (index + 1) % tabs.length;
    else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') next = (index - 1 + tabs.length) % tabs.length;
    else if (e.key === 'Home') next = 0;
    else if (e.key === 'End') next = tabs.length - 1;
    else return;
    e.preventDefault();
    select(tabs[next].id);
    tabEls[next]?.focus();
  }
</script>

<div class="tab-bar" role="tablist">
  {#each tabs as tab, i (tab.id)}
    <button
      bind:this={tabEls[i]}
      type="button"
      role="tab"
      id={tabElId(tab.id)}
      aria-controls={panelId}
      class="tab"
      class:is-active={tab.id === selected}
      aria-selected={tab.id === selected}
      tabindex={tab.id === selected ? 0 : -1}
      onclick={() => select(tab.id)}
      onkeydown={(e) => onKeydown(e, i)}
    >
      <span class="tab-label">{tab.label}</span>
      <span class="underline" aria-hidden="true"></span>
    </button>
  {/each}
</div>

<style>
  .tab-bar {
    display: flex;
    gap: var(--space-1200);
    align-items: flex-end;
    justify-content: center;
    padding-bottom: 6px;
    border-bottom: 0.5px solid var(--color-on-surface-secondary);
  }
  .tab {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: flex-end;
    gap: var(--space-50);
    padding: 1px 0;
    background: none;
    border: none;
  }
  @media (pointer: coarse) {
    .tab {
      min-height: 44px;
    }
  }
  .tab-label {
    font-size: var(--type-small-size);
    font-weight: var(--type-small-weight);
    color: var(--color-on-surface-secondary);
    white-space: nowrap;
  }
  .underline {
    width: 100%;
    height: 2px;
    background: transparent;
  }
  .is-active .tab-label {
    font-weight: var(--type-small-bold-weight);
    color: var(--color-on-surface-primary);
  }
  .is-active .underline {
    background: var(--color-on-surface-primary);
  }
</style>

<script lang="ts">
  import type { Snippet } from 'svelte';
  import { onMount, onDestroy } from 'svelte';
  import ModalHeader from './ModalHeader.svelte';

  /**
   * One responsive dialog primitive. `placement` decides positioning:
   * 'sheet' = bottom-anchored (mobile Layers), 'centered' = centered card (About,
   * both breakpoints — per the Figma). Accessibility contract: role=dialog +
   * aria-modal, focus moves in on open and returns to the trigger on close, focus
   * is trapped, Escape closes, scrim-click closes, and the ✕ is a real close button.
   */
  let {
    title,
    placement = 'centered',
    onClose,
    children
  }: {
    title: string;
    placement?: 'sheet' | 'centered';
    onClose?: () => void;
    children?: Snippet;
  } = $props();

  let dialogEl = $state<HTMLDivElement>();
  let trigger: HTMLElement | null = null;
  const titleId = `modal-title-${Math.random().toString(36).slice(2, 8)}`;

  function close() {
    onClose?.();
  }

  function focusable(): HTMLElement[] {
    if (!dialogEl) return [];
    return Array.from(
      dialogEl.querySelectorAll<HTMLElement>(
        'a[href], button:not([disabled]), input, select, textarea, [tabindex]:not([tabindex="-1"])'
      )
    );
  }

  function onKeydown(e: KeyboardEvent) {
    if (e.key === 'Escape') {
      e.preventDefault();
      close();
    } else if (e.key === 'Tab') {
      const els = focusable();
      if (els.length === 0) {
        e.preventDefault();
        return;
      }
      const first = els[0];
      const last = els[els.length - 1];
      const active = document.activeElement;
      if (e.shiftKey && active === first) {
        e.preventDefault();
        last.focus();
      } else if (!e.shiftKey && active === last) {
        e.preventDefault();
        first.focus();
      }
    }
  }

  onMount(() => {
    trigger = document.activeElement as HTMLElement;
    // Move focus into the dialog (announces the title via aria-labelledby).
    queueMicrotask(() => dialogEl?.focus());
  });
  onDestroy(() => {
    // Defer so focus returns AFTER the flush clears `inert` on the app background
    // (the trigger lives there); focusing a still-inert subtree would no-op.
    const t = trigger;
    queueMicrotask(() => t?.focus?.());
  });
</script>

<svelte:window onkeydown={onKeydown} />

<!-- svelte-ignore a11y_click_events_have_key_events a11y_no_static_element_interactions -->
<div class="scrim {placement}" onclick={close} role="presentation">
  <div
    class="dialog {placement}"
    bind:this={dialogEl}
    role="dialog"
    aria-modal="true"
    aria-labelledby={titleId}
    tabindex="-1"
    onclick={(e) => e.stopPropagation()}
  >
    <div class="head">
      <ModalHeader {title} {titleId} onClose={close} />
    </div>
    <div class="content">
      {@render children?.()}
    </div>
  </div>
</div>

<style>
  .scrim {
    position: fixed;
    inset: 0;
    z-index: 100;
    display: flex;
    background: rgb(0 0 0 / 0.4);
  }
  .scrim.centered {
    align-items: center;
    justify-content: center;
    padding: var(--space-400);
  }
  .scrim.sheet {
    align-items: flex-end;
  }

  .dialog {
    display: flex;
    flex-direction: column;
    background: var(--color-surface-base);
    box-sizing: border-box;
    --modal-pad: var(--space-400);
  }
  .dialog.centered {
    width: min(520px, 100%);
    max-height: 80vh;
    border-radius: 8px;
    --modal-pad: 20px;
  }
  .dialog.sheet {
    width: 100%;
    max-height: 85%;
    border-radius: 12px 12px 0 0;
  }

  .head {
    flex-shrink: 0;
    padding: var(--space-400) var(--modal-pad) 0;
  }
  .content {
    overflow-y: auto;
    scrollbar-gutter: stable;
    padding: var(--space-200) var(--modal-pad) var(--space-400);
  }
</style>

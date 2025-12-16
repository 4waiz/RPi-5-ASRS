<script>
  import { fly } from "svelte/transition";
  import { cubicOut, cubicInOut } from "svelte/easing";
  // Component state passed in from parent.
  let { open = false, unit = null, onClose = () => {} } = $props();

  // Distinguish numeric-looking statuses to style them differently.
  const isNumeric = (value) => {
    if (value === null || value === undefined) return false;
    const trimmed = String(value).trim();
    return trimmed !== "" && !Number.isNaN(Number(trimmed));
  };
</script>

{#if open && unit}
  <!-- Drawer slides in/out using Svelte transitions provided by the parent. -->
  <aside
    class="drawer"
    aria-label="Unit details drawer"
    in:fly={{ x: 88, duration: 320, easing: cubicOut, opacity: 0.08 }}
    out:fly={{ x: 120, duration: 360, easing: cubicInOut, opacity: 0.02 }}
  >
    <header class="hdr">
      <div class="head">
        {#if unit?.image}<img src={unit.image} alt="" />{/if}
        <div>
          <div class="title">{unit?.name ?? ""}</div>
          <div class="subtitle">{unit ? `( ID: ${unit.id} )` : ""}</div>
        </div>
      </div>
      <button class="icon-btn" onclick={() => onClose()} aria-label="Close">
        <svg width="22" height="22" viewBox="0 0 24 24">
          <path d="M6 6l12 12M18 6L6 18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
        </svg>
      </button>
    </header>

    <section class="list">
      {#each unit.subcomponents ?? [] as component (component.id)}
        <div class="row">
          {#if component.image}<img src={component.image} alt="" />{/if}
          <div class="meta">
            <div class="name">{component.name}</div>
            <div class="id">{component.id}</div>
          </div>
          <div class="status {component.status} {isNumeric(component.status) ? "numeric" : ""}">
            {component.status ?? "Unknown"}
          </div>
        </div>
      {/each}
    </section>
  </aside>
{/if}

<style>
  .drawer {
    flex: 1 1 min(480px, 90vw);
    align-self: stretch;
    max-width: 640px;
    max-height: calc(100vh - 160px);
    background: #fff;
    box-shadow: -8px 0 18px rgba(0, 0, 0, 0.12);
    display: grid;
    grid-template-rows: auto 1fr;
    border: 1px solid #eee;
    border-radius: 16px;
    overflow: hidden;
  }

  .hdr {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 16px 18px;
    border-bottom: 1px solid #eee;
  }
  .head {
    display: flex;
    align-items: center;
    gap: 12px;
  }
  .head img {
    width: 52px;
    height: 52px;
    object-fit: contain;
    background: #f4f4f4;
    border-radius: 12px;
  }
  .title {
    font-weight: 700;
    font-size: 1.05rem;
    color: #222;
  }
  .subtitle {
    color: #7b7b7b;
    font-size: 0.9rem;
  }
  .icon-btn {
    border: none;
    background: transparent;
    padding: 8px;
    border-radius: 10px;
    cursor: pointer;
  }
  .icon-btn:hover {
    background: #f4f4f4;
  }

  .list {
    padding: 12px 16px 28px;
    overflow: auto;
    scroll-behavior: smooth;
    -webkit-overflow-scrolling: touch;
    overscroll-behavior: contain;
  }
  .row {
    display: grid;
    grid-template-columns: 64px 1fr auto;
    align-items: center;
    gap: 16px;
    padding: 18px 14px;
    border-bottom: 1px solid #f2f2f2;
    border-radius: 16px;
    transition: background 140ms ease, box-shadow 160ms ease, transform 120ms ease;
  }
  .row img {
    width: 60px;
    height: 60px;
    object-fit: contain;
  }
  .meta {
    display: grid;
  }
  .name {
    font-weight: 600;
    color: #2b2b2b;
  }
  .id {
    color: #8a8a8a;
    font-size: 0.9rem;
  }
  .status {
    font-weight: 600;
    font-size: 0.92rem;
  }
  .status.Running,
  .status.Live {
    color: #1e7d34;
  }
  .status.Off {
    color: #a33;
  }
  .status.numeric {
    color: #2a6bf3;
  }

  @media (max-width: 960px) {
    .drawer {
      flex: 1 1 100%;
      width: 100%;
      max-height: none;
      border-radius: 16px;
    }
  }
</style>
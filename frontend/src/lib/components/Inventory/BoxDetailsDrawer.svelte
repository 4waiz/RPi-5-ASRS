<script>
  import { afterUpdate, createEventDispatcher } from "svelte";
  import { clearSelection } from "../../stores/inventory.js";

  /** @typedef {import("../../stores/inventory.js").InventoryBox} InventoryBox */
  /** @typedef {import("../../stores/inventory.js").LiveEvent} LiveEvent */
  /** @typedef {{ box: InventoryBox, events: LiveEvent[], mode: "LIVE"|"SIM" }} Props */

  export let box;
  export let events = [];
  export let mode = "SIM";

  const dispatch = createEventDispatcher();

  const isLiveMode = mode === "LIVE";

  let drawerEl;
  let lastBoxId;

  afterUpdate(() => {
    if (box && box.id !== lastBoxId) {
      drawerEl?.focus();
      lastBoxId = box.id;
    }
  });

  function close() {
    clearSelection();
    dispatch("close");
  }

  function formatDate(timestamp) {
    if (!timestamp) return "";
    try {
      return new Date(timestamp).toLocaleString([], {
        hour: "2-digit",
        minute: "2-digit",
        month: "short",
        day: "numeric",
      });
    } catch {
      return "";
    }
  }
</script>

{#if box}
  <div class="overlay" on:click|self={close} aria-hidden="true" />
  <aside
    class="drawer"
    bind:this={drawerEl}
    tabindex="-1"
    role="dialog"
    aria-label={`Details for box ${box.id}`}
    aria-modal="true"
  >
    <header>
      <div>
        <h2>Box {box.id}</h2>
        <p>{box.sku ?? "Unassigned SKU"}</p>
      </div>
      <button class="close" on:click={close} aria-label="Close box details">×</button>
    </header>

    <section class="stats">
      <div>
        <span class="label">Quantity</span>
        <strong>{box.qty} / {box.capacity}</strong>
      </div>
      <div>
        <span class="label">Reserved</span>
        <strong>{box.reservedQty}</strong>
      </div>
      <div>
        <span class="label">Status</span>
        <strong class={`status ${box.status}`}>{box.status}</strong>
      </div>
      <div>
        <span class="label">Last operation</span>
        <strong>{formatDate(box.lastOpAt)}</strong>
      </div>
    </section>

    <section class="actions">
      <button
        type="button"
        class="action primary"
        disabled={isLiveMode}
        aria-disabled={isLiveMode}
        title={isLiveMode ? "Disabled in LIVE mode" : "Reserve stock"}
      >
        Reserve
      </button>
      <button
        type="button"
        class="action"
        disabled={isLiveMode}
        aria-disabled={isLiveMode}
        title={isLiveMode ? "Disabled in LIVE mode" : "Release held stock"}
      >
        Release
      </button>
      {#if isLiveMode}
        <span class="mode-lock" aria-hidden="true">LIVE mode – actions locked</span>
      {/if}
    </section>

    <section class="history">
      <h3>Recent activity</h3>
      {#if events.length === 0}
        <p class="empty">No recent events for this box.</p>
      {:else}
        <ul>
          {#each events as event (event.id)}
            <li>
              <span class="event-type {event.type}">{event.type}</span>
              <p>{event.message}</p>
              <time datetime={event.at}>{formatDate(event.at)}</time>
            </li>
          {/each}
        </ul>
      {/if}
    </section>
  </aside>
{/if}

<style>
  .overlay {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.35);
    z-index: 20;
  }

  .drawer {
    position: fixed;
    top: 0;
    right: 0;
    width: min(360px, 90vw);
    height: 100%;
    background: #fff;
    box-shadow: -12px 0 24px rgba(0, 0, 0, 0.15);
    padding: 24px;
    display: flex;
    flex-direction: column;
    gap: 24px;
    z-index: 30;
    outline: none;
  }

  header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
  }

  header h2 {
    margin: 0;
    font-size: 1.4rem;
  }

  header p {
    margin: 4px 0 0;
    color: rgba(0, 0, 0, 0.6);
  }

  .close {
    border: none;
    background: transparent;
    font-size: 1.5rem;
    cursor: pointer;
    line-height: 1;
    color: rgba(0, 0, 0, 0.4);
  }

  .close:hover,
  .close:focus-visible {
    color: rgba(0, 0, 0, 0.7);
    outline: none;
  }

  .stats {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 16px;
  }

  .label {
    display: block;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: rgba(0, 0, 0, 0.45);
  }

  .status.full {
    color: #067a58;
  }

  .status.partial {
    color: #f2994a;
  }

  .status.empty {
    color: #b00020;
  }

  .actions {
    display: flex;
    align-items: center;
    gap: 12px;
    flex-wrap: wrap;
  }

  .action {
    padding: 10px 18px;
    border-radius: 10px;
    border: 1px solid rgba(0, 0, 0, 0.1);
    background: #fff;
    font-weight: 600;
    cursor: pointer;
  }

  .action.primary {
    background: #0052cc;
    color: #fff;
    border-color: #0052cc;
  }

  .action:disabled {
    cursor: not-allowed;
    opacity: 0.6;
  }

  .mode-lock {
    font-size: 0.8rem;
    color: rgba(0, 0, 0, 0.5);
  }

  .history h3 {
    margin: 0;
    font-size: 1rem;
  }

  .history ul {
    margin: 12px 0 0;
    padding: 0;
    list-style: none;
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .history li {
    display: grid;
    grid-template-columns: auto 1fr;
    gap: 8px 12px;
    padding: 8px 0;
    border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  }

  .event-type {
    text-transform: uppercase;
    font-size: 0.7rem;
    font-weight: 700;
    padding: 2px 6px;
    border-radius: 6px;
    background: rgba(0, 0, 0, 0.08);
  }

  .event-type.retrieve {
    background: rgba(0, 82, 204, 0.12);
    color: #0052cc;
  }

  .event-type.store {
    background: rgba(0, 184, 148, 0.16);
    color: #067a58;
  }

  .event-type.reject,
  .event-type.alert {
    background: rgba(204, 0, 0, 0.12);
    color: #b00020;
  }

  .history p {
    margin: 0;
    grid-column: 1 / -1;
    color: rgba(0, 0, 0, 0.8);
  }

  .history time {
    grid-column: 2 / 3;
    font-size: 0.8rem;
    color: rgba(0, 0, 0, 0.45);
  }

  .empty {
    margin: 0;
    color: rgba(0, 0, 0, 0.5);
    font-style: italic;
  }
</style>

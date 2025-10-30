<script>
  import { inventoryStore, selectBox } from "../../stores/inventory.js";

  /** @typedef {import("../../stores/inventory.js").InventoryBox} InventoryBox */
  /** @typedef {{ items?: InventoryBox[] }} Props */

  export let items = [];

  const GRID_COLUMNS = 5;
  const GRID_ROWS = 4;

  $: selectedId = $inventoryStore.selectedBoxId;

  function formatStatus(status) {
    if (status === "full") return "Full";
    if (status === "partial") return "Partially full";
    return "Empty";
  }
</script>

<section
  class="bins-grid"
  style={`--grid-columns:${GRID_COLUMNS}; --grid-rows:${GRID_ROWS};`}
  aria-label="Inventory bins"
>
  {#each items as item (item.id)}
    <button
      type="button"
      class="bin-card"
      class:selected={item.id === selectedId}
      on:click={() => selectBox(item.id)}
      aria-pressed={item.id === selectedId}
      aria-label={`Select box ${item.id}, ${formatStatus(item.status)}, ${item.qty} of ${item.capacity} units`}
    >
      <header>
        <span class="box-id">Box {item.id}</span>
        {#if item.hasAlert}
          <span class="alert-badge" aria-label="Alert active">!</span>
        {/if}
      </header>
      <div class="status-row">
        <span class="status-indicator {item.status}"></span>
        <span class="status-label">{formatStatus(item.status)}</span>
      </div>
      <div class="meta">
        <span class="sku">{item.sku ?? "Empty slot"}</span>
        <span class="qty">{item.qty}/{item.capacity}</span>
        {#if item.reservedQty}
          <span class="reserved">Reserved: {item.reservedQty}</span>
        {/if}
      </div>
    </button>
  {/each}
</section>

<style>
  .bins-grid {
    display: grid;
    grid-template-columns: repeat(var(--grid-columns), minmax(0, 1fr));
    grid-auto-rows: minmax(120px, auto);
    gap: 16px;
  }

  .bin-card {
    display: flex;
    flex-direction: column;
    gap: 8px;
    padding: 14px;
    border-radius: 14px;
    border: 1px solid rgba(0, 0, 0, 0.1);
    background: #fff;
    text-align: left;
    cursor: pointer;
    transition: transform 0.15s ease, border-color 0.15s ease, box-shadow 0.15s ease;
  }

  .bin-card:hover,
  .bin-card:focus-visible {
    border-color: rgba(0, 82, 204, 0.45);
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
    outline: none;
  }

  .bin-card.selected {
    border-color: #0052cc;
    box-shadow: 0 0 0 2px rgba(0, 82, 204, 0.3);
  }

  header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 600;
    color: rgba(0, 0, 0, 0.87);
  }

  .alert-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background: #d93025;
    color: #fff;
    border-radius: 999px;
    font-size: 0.7rem;
    padding: 2px 6px;
    font-weight: 700;
  }

  .status-row {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .status-indicator {
    display: inline-block;
    width: 10px;
    height: 10px;
    border-radius: 999px;
    border: 3px solid transparent;
  }

  .status-indicator.full {
    border-color: #067a58;
  }

  .status-indicator.partial {
    border-color: #f2994a;
  }

  .status-indicator.empty {
    border-color: #b00020;
  }

  .status-label {
    font-size: 0.85rem;
    color: rgba(0, 0, 0, 0.6);
  }

  .meta {
    display: grid;
    gap: 4px;
    font-size: 0.85rem;
    color: rgba(0, 0, 0, 0.7);
  }

  .sku {
    font-weight: 500;
    color: rgba(0, 0, 0, 0.75);
  }

  .qty {
    font-feature-settings: "tnum";
  }

  .reserved {
    color: rgba(0, 0, 0, 0.5);
  }

  @media (max-width: 1100px) {
    .bins-grid {
      grid-template-columns: repeat(4, minmax(0, 1fr));
    }
  }

  @media (max-width: 900px) {
    .bins-grid {
      grid-template-columns: repeat(3, minmax(0, 1fr));
    }
  }

  @media (max-width: 640px) {
    .bins-grid {
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }
  }
</style>

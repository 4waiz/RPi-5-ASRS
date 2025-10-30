<script>
  import { createEventDispatcher } from "svelte";
  import { inventoryStore, setStatus } from "../../stores/inventory.js";
  import { loadInventory } from "../../services/inventoryService.js";
  import inventoryImage from "../../../assets/inverntory/inventory storage.png";

  const REFRESH_LABEL = "Refresh inventory data";
  const dispatch = createEventDispatcher();

  $: state = $inventoryStore;
  $: updatedText = formatUpdatedText(state.updatedAt);

  async function handleRefresh() {
    setStatus("loading", null);
    await loadInventory();
    dispatch("refreshed");
  }

  function formatUpdatedText(timestamp) {
    if (!timestamp) return "Never updated";
    try {
      const date = new Date(timestamp);
      return `Updated ${date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}`;
    } catch {
      return "Updated recently";
    }
  }
</script>

<header class="inventory-header" data-state={state.status}>
  <div class="header-info">
    <div>
      <h1>Inventory</h1>
      <p class="updated-at">{updatedText}</p>
    </div>
    <button
      class="refresh-button"
      aria-label={REFRESH_LABEL}
      on:click={handleRefresh}
      disabled={state.status === "loading"}
    >
      {state.status === "loading" ? "Refreshing..." : "Refresh"}
    </button>
  </div>
  <img class="header-image" src={inventoryImage} alt="Inventory storage" />
</header>

<style>
  .inventory-header {
    display: grid;
    grid-template-columns: 1fr auto;
    align-items: center;
    gap: 24px;
    padding: 16px 20px;
    background: #f9fafb;
    border-radius: 16px;
    border: 1px solid rgba(0, 0, 0, 0.05);
  }

  .header-info {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
  }

  h1 {
    margin: 0;
    font-size: 1.5rem;
    font-weight: 600;
    color: rgba(0, 0, 0, 0.87);
  }

  .updated-at {
    margin: 6px 0 0;
    color: rgba(0, 0, 0, 0.6);
    font-size: 0.875rem;
  }

  .refresh-button {
    padding: 8px 16px;
    border-radius: 8px;
    background: #0052cc;
    color: #fff;
    font-weight: 600;
    border: none;
    cursor: pointer;
    transition: background 0.2s ease;
  }

  .refresh-button:disabled {
    background: rgba(0, 0, 0, 0.12);
    cursor: wait;
  }

  .refresh-button:not(:disabled):hover,
  .refresh-button:not(:disabled):focus-visible {
    background: #003f99;
    outline: none;
  }

  .header-image {
    width: 220px;
    max-width: 100%;
    border-radius: 12px;
    object-fit: cover;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
  }

  @media (max-width: 900px) {
    .inventory-header {
      grid-template-columns: 1fr;
      text-align: center;
    }

    .header-info {
      flex-direction: column;
    }

    .header-image {
      width: 100%;
    }
  }
</style>

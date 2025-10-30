<script>
  import { BOX_STATUSES, inventoryStore, kpiCounts, setFilter } from "../../stores/inventory.js";

  const LABELS = {
    full: "Full",
    partial: "Partially full",
    empty: "Empty",
  };

  $: currentStatus = $inventoryStore.filter.status;
  $: counts = $kpiCounts;

  function handleClick(statusKey) {
    const nextStatus = currentStatus === statusKey ? "all" : statusKey;
    setFilter({ status: nextStatus });
  }
</script>

<section class="kpi-bar" aria-label="Inventory status KPIs">
  {#each BOX_STATUSES as status}
    <button
      type="button"
      class:active={currentStatus === status}
      class="kpi-chip"
      on:click={() => handleClick(status)}
      aria-pressed={currentStatus === status}
      aria-label={`Filter ${LABELS[status]} bins`}
    >
      <span>{LABELS[status]}</span>
      <strong>{counts[status] ?? 0}</strong>
    </button>
  {/each}
</section>

<style>
  .kpi-bar {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
  }

  .kpi-chip {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 10px 16px;
    border-radius: 999px;
    border: 1px solid rgba(0, 0, 0, 0.08);
    background: #fff;
    font-size: 0.95rem;
    font-weight: 500;
    color: rgba(0, 0, 0, 0.74);
    cursor: pointer;
    transition: background 0.2s ease, border-color 0.2s ease;
  }

  .kpi-chip:hover,
  .kpi-chip:focus-visible {
    border-color: rgba(0, 82, 204, 0.4);
    outline: none;
  }

  .kpi-chip.active {
    background: rgba(0, 82, 204, 0.12);
    border-color: #0052cc;
    color: #003f99;
  }

  .kpi-chip strong {
    font-size: 1rem;
    color: rgba(0, 0, 0, 0.87);
  }
</style>

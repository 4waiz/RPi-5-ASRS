<script>
  import { onMount } from "svelte";
  import {
    BOX_STATUSES,
    inventoryStore,
    setFilter,
  } from "../../stores/inventory.js";

  const STATUS_OPTIONS = [{ value: "all", label: "All statuses" }].concat(
    BOX_STATUSES.map((key) => ({
      value: key,
      label: key === "partial" ? "Partially full" : key.charAt(0).toUpperCase() + key.slice(1),
    })),
  );

  const SORT_OPTIONS = [
    { value: "box-asc", label: "Box ID (Asc)" },
    { value: "box-desc", label: "Box ID (Desc)" },
    { value: "qty-asc", label: "Quantity (Low→High)" },
    { value: "qty-desc", label: "Quantity (High→Low)" },
  ];

  let searchInput;

  $: filter = $inventoryStore.filter;

  function handleSearchInput(event) {
    setFilter({ query: event.currentTarget.value });
  }

  function handleStatusChange(event) {
    setFilter({ status: event.currentTarget.value });
  }

  function handleSortChange(event) {
    setFilter({ sort: event.currentTarget.value });
  }

  onMount(() => {
    const handler = (event) => {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        searchInput?.focus();
      }
    };

    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  });
</script>

<section class="toolbar" aria-label="Inventory filters">
  <div class="search-group">
    <label class="sr-only" for="inventory-search">Search inventory</label>
    <input
      id="inventory-search"
      bind:this={searchInput}
      type="search"
      placeholder="Search by SKU or box…"
      value={filter.query}
      on:input={handleSearchInput}
      aria-label="Search inventory boxes"
    />
    <span class="hint">⌘/Ctrl + K</span>
  </div>

  <div class="controls">
    <label class="sr-only" for="inventory-status-filter">Filter by fill status</label>
    <select
      id="inventory-status-filter"
      value={filter.status}
      on:change={handleStatusChange}
      aria-label="Filter by inventory status"
    >
      {#each STATUS_OPTIONS as option}
        <option value={option.value}>{option.label}</option>
      {/each}
    </select>

    <label class="sr-only" for="inventory-sort">Sort bins</label>
    <select
      id="inventory-sort"
      value={filter.sort}
      on:change={handleSortChange}
      aria-label="Sort inventory bins"
    >
      {#each SORT_OPTIONS as option}
        <option value={option.value}>{option.label}</option>
      {/each}
    </select>
  </div>
</section>

<style>
  .toolbar {
    display: flex;
    flex-wrap: wrap;
    gap: 16px;
    align-items: center;
    justify-content: space-between;
  }

  .search-group {
    position: relative;
    flex: 1 1 260px;
  }

  input[type="search"] {
    width: 100%;
    padding: 10px 40px 10px 14px;
    border-radius: 10px;
    border: 1px solid rgba(0, 0, 0, 0.12);
    font-size: 0.95rem;
  }

  input[type="search"]:focus-visible {
    outline: 2px solid rgba(0, 82, 204, 0.4);
    outline-offset: 1px;
  }

  .hint {
    position: absolute;
    right: 12px;
    top: 50%;
    transform: translateY(-50%);
    font-size: 0.75rem;
    color: rgba(0, 0, 0, 0.4);
  }

  .controls {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
    align-items: center;
  }

  select {
    padding: 10px 14px;
    border-radius: 10px;
    border: 1px solid rgba(0, 0, 0, 0.12);
    font-size: 0.95rem;
    background-color: #fff;
  }

  .sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    border: 0;
  }
</style>

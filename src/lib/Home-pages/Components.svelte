<script>
import UnitCard from "./UnitCard.svelte";
  import RightDrawer from "./RightDrawer.svelte";
  import { units } from "../catalog.js";
  import { writable } from "svelte/store";

const DEFAULT_STATUSES = {
  SM1: "Running",
  SM2: "Running",
  SM3: "Off",
  PS1: "Live",
  PS2: "Live",
  PS3: "Live",
  PS4: "Idle",
  JO1: "Online",
  GD1: "Idle",
};

const INITIAL_STATE = {
  online: true,
  statuses: DEFAULT_STATUSES,
};

// Simplified store without the performance-killing interval
const createStatusStore = () => {
  const store = writable(INITIAL_STATE);

  return {
    subscribe: store.subscribe,
    setOnline(value) {
      store.update((state) => ({
        ...state,
        online: value ?? !state.online,
      }));
    },
    setStatus(id, status) {
      store.update((state) => ({
        ...state,
        statuses: {
          ...state.statuses,
          [id]: status,
        },
      }));
    },
    reset() {
      store.set(INITIAL_STATE);
    },
  };
};

const statusStore = createStatusStore();


  const catalog = units;
  let open = false;
  let selectedUnitId = null;

  $: backendOnline = $statusStore.online;

  // Memoized: Only recalculate when statusStore changes
  $: unitsWithStatus = catalog.map((unit) => ({
    ...unit,
    subcomponents: unit.subcomponents.map((component) => ({
      ...component,
      status: backendOnline
        ? $statusStore.statuses[component.id] ?? component.defaultStatus ?? "Unknown"
        : "Unknown",
    })),
  }));

  $: selectedUnit = selectedUnitId ? unitsWithStatus.find((unit) => unit.id === selectedUnitId) : null;

  const closeDrawer = () => {
    open = false;
    selectedUnitId = null;
  };

  const openDrawer = (unitId) => {
    if (open && selectedUnitId === unitId) {
      closeDrawer();
      return;
    }
    selectedUnitId = unitId;
    open = true;
  };
</script>

<div class="components-page" class:with-drawer={open}>
  <div class="units-column">
    {#each unitsWithStatus as unit (unit.id)}
      <UnitCard
        {unit}
        active={open && selectedUnit?.id === unit.id}
        hideCount={open}
        hideArrow={open}
        on:open={() => openDrawer(unit.id)}
      />
    {/each}
  </div>

  <RightDrawer
    {open}
    onClose={closeDrawer}
    unit={selectedUnit}
  />
</div>

<style>
  /* Layout container combining the unit list and the detail drawer. */
  .components-page {
    position: relative;
    display: flex;
    gap: 28px;
    align-items: stretch;
    padding: 20px 24px 32px;
    min-height: calc(100vh - 120px);
    box-sizing: border-box;
    transition: all 200ms ease;
    user-select: none;
    caret-color: transparent;
  }

  :global(.components-page *) {
    user-select: none;
    caret-color: transparent;
  }

  .units-column {
    flex: 1 1 100%;
    display: flex;
    flex-direction: column;
    gap: 16px;
    max-width: 960px;
    transition: all 200ms ease;
  }

  .components-page.with-drawer {
    align-items: flex-start;
    column-gap: 44px;
  }

  .components-page.with-drawer .units-column {
    flex: 0 0 340px;
    max-width: 340px;
  }

  .components-page:not(.with-drawer) {
    justify-content: center;
  }

  .components-page:not(.with-drawer) :global(.unit-card) {
    min-height: 140px;
  }

  @media (max-width: 960px) {
    .components-page {
      flex-direction: column;
      gap: 20px;
    }

    .units-column {
      flex: 1 1 auto;
      max-width: none;
    }

    .components-page.with-drawer .units-column {
      flex: 1 1 auto;
    }
  }
</style>

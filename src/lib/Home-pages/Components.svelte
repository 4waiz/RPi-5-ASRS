<script>
import UnitCard from "./UnitCard.svelte";
  import RightDrawer from "./RightDrawer.svelte";
  import { units } from "../catalog.js";
  import { writable } from "svelte/store";
  import { onMount, onDestroy } from "svelte";

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
  GD2: "Running",
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

// Define possible statuses for each component type
const STATUS_OPTIONS = {
  // Stepper Motors
  SM1: ["Running", "Off", "Idle"],
  SM2: ["Running", "Off", "Idle"],
  SM3: ["Running", "Off", "Idle"],

  // Proximity Sensors
  PS1: ["Live", "Idle", "Detecting"],
  PS2: ["Live", "Idle", "Detecting"],
  PS3: ["Live", "Idle", "Detecting"],
  PS4: ["Live", "Idle", "Detecting"],

  // Jetson Orin
  JO1: ["Online", "Processing", "Idle", "Busy"],

  // DC Motors
  GD1: ["Running", "Off", "Idle"],
  GD2: ["Running", "Off", "Idle"],
};

let statusInterval;
let isVisible = $state(true);

// Randomly change component statuses to simulate live system
function updateStatuses() {
  // Randomly pick 2-5 components to update for more visible changes
  const numChanges = Math.floor(Math.random() * 4) + 2;
  const componentIds = Object.keys(STATUS_OPTIONS);

  for (let i = 0; i < numChanges; i++) {
    const randomId = componentIds[Math.floor(Math.random() * componentIds.length)];
    const possibleStatuses = STATUS_OPTIONS[randomId];
    const randomStatus = possibleStatuses[Math.floor(Math.random() * possibleStatuses.length)];

    statusStore.setStatus(randomId, randomStatus);
  }
}

onMount(() => {
  // Start interval only when visible
  if (isVisible) {
    statusInterval = setInterval(updateStatuses, 2000);
  }

  // Pause/resume based on page visibility
  const handleVisibilityChange = () => {
    if (document.hidden) {
      if (statusInterval) {
        clearInterval(statusInterval);
        statusInterval = null;
      }
      isVisible = false;
    } else {
      isVisible = true;
      if (!statusInterval) {
        statusInterval = setInterval(updateStatuses, 2000);
      }
    }
  };

  document.addEventListener('visibilitychange', handleVisibilityChange);

  return () => {
    document.removeEventListener('visibilitychange', handleVisibilityChange);
    if (statusInterval) {
      clearInterval(statusInterval);
    }
  };
});

onDestroy(() => {
  if (statusInterval) {
    clearInterval(statusInterval);
  }
});


  const catalog = units;
  let open = $state(false);
  let selectedUnitId = $state(null);
  let cachedUnits = $state([]);

  // Derived reactive values using Svelte 5 runes
  let backendOnline = $derived($statusStore.online);

  let unitsWithStatus = $derived(
    catalog.map((unit) => ({
      ...unit,
      subcomponents: unit.subcomponents.map((component) => ({
        ...component,
        status: backendOnline
          ? $statusStore.statuses[component.id] ?? component.defaultStatus ?? "Unknown"
          : "Unknown",
      })),
    }))
  );

  let selectedUnit = $derived(
    selectedUnitId ? unitsWithStatus.find((unit) => unit.id === selectedUnitId) : null
  );

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

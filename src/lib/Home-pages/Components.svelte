<script>
import UnitCard from "./UnitCard.svelte";
  import RightDrawer from "./RightDrawer.svelte";
  import { units } from "../catalog.js";
  import { writable } from "svelte/store";

const STATUS_SEQUENCE = ["Running", "Live", "Online", "Idle", "Off"];

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
  lastUpdated: new Date().toISOString(),
  statuses: DEFAULT_STATUSES,
};

const clone = (value) => JSON.parse(JSON.stringify(value));

const createStatusStore = () => {
  const store = writable(clone(INITIAL_STATE));

  if (typeof window !== "undefined") {
    const interval = setInterval(() => {
      store.update((state) => {
        const nextStatuses = Object.fromEntries(
          Object.entries(state.statuses).map(([id, status]) => [
            id,
            getNextStatus(status),
          ])
        );

        return {
          ...state,
          lastUpdated: new Date().toISOString(),
          statuses: nextStatuses,
        };
      });
    }, 3000);

    const unsubscribe = store.subscribe(() => {});

    if (import.meta?.hot) {
      import.meta.hot.dispose(() => {
        clearInterval(interval);
        unsubscribe();
      });
    }
  }

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
      store.set(clone(INITIAL_STATE));
    },
  };
};

const getNextStatus = (current) => {
  const index = STATUS_SEQUENCE.indexOf(current);
  if (index === -1) {
    return STATUS_SEQUENCE[0];
  }
  return STATUS_SEQUENCE[(index + 1) % STATUS_SEQUENCE.length];
};

const statusStore = createStatusStore();


  const catalog = units;
  let open = false;
  let selectedUnitId = null;

  $: statusState = $statusStore;
  $: backendOnline = statusState?.online ?? false;
  $: unitsWithStatus = catalog.map((unit) => ({
    ...unit,
    subcomponents: unit.subcomponents.map((component) => ({
      ...component,
      status: backendOnline
        ? statusState?.statuses?.[component.id] ?? component.defaultStatus ?? "Unknown"
        : "Unknown",
    })),
  }));

  $: selectedUnit = unitsWithStatus.find((unit) => unit.id === selectedUnitId) ?? null;

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
    background: #f3f3f3;
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

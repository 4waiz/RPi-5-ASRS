<script>
import UnitCard from "./UnitCard.svelte";
  import RightDrawer from "./RightDrawer.svelte";
  import { units } from "../../lib/catalog.js";
  import { writable } from "svelte/store";
  import { t } from "../../lib/i18n";

// Map English component names to translation keys
const componentNameMap = {
  "Stepper Motor 57x56mm": "components.stepperMotor",
  "Proximity Sensor": "components.proximitySensor",
  "Jetson Orin Nano": "components.jetsonOrinNano",
  "Greartisan DC 24V": "components.greartisanDC"
};

// Map unit names to translation keys
const getUnitNameKey = (name) => {
  if (name.includes("Conveyor_Unit _1")) return "components.conveyorUnit";
  if (name.includes("Conveyor_Unit _2")) return "components.conveyorUnit";
  return null;
};

const getUnitNumber = (name) => {
  if (name.includes("_1")) return "1";
  if (name.includes("_2")) return "2";
  return "";
};

// Map status values to translation keys (case-insensitive)
const statusMap = {
  "running": "components.status.running",
  "live": "components.status.live",
  "online": "components.status.online",
  "idle": "components.status.idle",
  "off": "components.status.off",
  "unknown": "components.status.unknown"
};

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
  let open = $state(false);
  let selectedUnitId = $state(null);

  let statusState = $derived($statusStore);
  let backendOnline = $derived(statusState?.online ?? false);
  let unitsWithStatus = $derived(catalog.map((unit) => {
    // Translate unit name
    const unitNameKey = getUnitNameKey(unit.name);
    const unitNumber = getUnitNumber(unit.name);
    const translatedUnitName = unitNameKey
      ? $t(unitNameKey).replace('{number}', unitNumber)
      : unit.name;

    return {
      ...unit,
      translatedName: translatedUnitName,
      subcomponents: unit.subcomponents.map((component) => {
        const status = backendOnline
          ? statusState?.statuses?.[component.id] ?? component.defaultStatus ?? "Unknown"
          : "Unknown";

        // Translate component name
        const componentNameKey = componentNameMap[component.name];
        const translatedComponentName = componentNameKey ? $t(componentNameKey) : component.name;

        // Translate status
        const statusKey = statusMap[status.toLowerCase()];
        const translatedStatus = statusKey ? $t(statusKey) : status;

        return {
          ...component,
          translatedName: translatedComponentName,
          status: status,
          translatedStatus: translatedStatus,
        };
      }),
    };
  }));

  let selectedUnit = $derived(unitsWithStatus.find((unit) => unit.id === selectedUnitId) ?? null);

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
        onOpen={() => openDrawer(unit.id)}
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
    transition: all 0.3s ease;
    background: var(--bg-page);
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
    transition: all 0.3s ease;
    background: var(--bg-page);
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
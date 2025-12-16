<script>
import UnitCard from "./UnitCard.svelte";
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

  {#if open && selectedUnit}
    <div class="components-column">
      {#each selectedUnit.subcomponents as component (component.id)}
        <div class="component-card">
          <div class="component-thumb">
            {#if component.image}<img src={component.image} alt="" />{/if}
          </div>
          <div class="component-info">
            <div class="component-name">{component.translatedName || component.name}</div>
            <div class="component-id">{component.id}</div>
            <div class="component-status {component.status}">
              {component.translatedStatus || component.status || $t('components.status.unknown')}
            </div>
          </div>
        </div>
      {/each}
    </div>
  {/if}
</div>

<style>
  /* Layout container combining the unit list and the components. */
  .components-page {
    position: relative;
    display: flex;
    flex-direction: row;
    flex-wrap: nowrap;
    gap: 20px;
    align-items: stretch;
    padding: 12px 16px 16px;
    height: 100%;
    box-sizing: border-box;
    transition: all 0.3s ease;
    background: transparent;
    user-select: none;
    caret-color: transparent;
    overflow: hidden;
  }

  :global(.components-page *) {
    user-select: none;
    caret-color: transparent;
  }

  /* Custom scrollbar styling */
  .units-column::-webkit-scrollbar,
  .components-column::-webkit-scrollbar {
    width: 6px;
  }

  .units-column::-webkit-scrollbar-track,
  .components-column::-webkit-scrollbar-track {
    background: transparent;
  }

  .units-column::-webkit-scrollbar-thumb,
  .components-column::-webkit-scrollbar-thumb {
    background: var(--border, rgba(0, 0, 0, 0.15));
    border-radius: 3px;
  }

  .units-column::-webkit-scrollbar-thumb:hover,
  .components-column::-webkit-scrollbar-thumb:hover {
    background: var(--secondary, rgba(0, 0, 0, 0.25));
  }

  .units-column {
    display: flex;
    flex-direction: column;
    gap: 20px;
    max-width: 600px;
    transition: all 0.3s ease;
    background: transparent;
    flex-shrink: 0;
    overflow: hidden;
  }

  .components-page:not(.with-drawer) {
    justify-content: flex-start;
  }

  .components-page:not(.with-drawer) .units-column {
    flex: 1 1 auto;
    max-width: 700px;
  }

  .components-page:not(.with-drawer) :global(.unit-card) {
    min-height: 108px;
  }

  .components-page.with-drawer {
    align-items: stretch;
    column-gap: 24px;
    justify-content: flex-start;
  }

  .components-page.with-drawer .units-column {
    flex: 0 0 320px;
    width: 320px;
    max-width: 320px;
  }

  /* Remove card styling when drawer is open */
  .components-page.with-drawer :global(.unit-card) {
    background: none;
    box-shadow: none;
    border: none;
    border-radius: 0;
    padding: 25px 16px 12px 12px;
    border-bottom: 1px solid var(--border, rgba(0, 0, 0, 0.1));
  }

  .components-page.with-drawer :global(.unit-card:last-child) {
    border-bottom: none;
  }

  .components-page.with-drawer :global(.unit-card.active) {
    background: var(--bg-card, #ffffff);
    border: 2px solid var(--brand, #ff5622);
    border-radius: 17px;
    padding: 25px 16px 12px 12px;
  }

  /* Components column on the right */
  .components-column {
    display: flex;
    flex-direction: column;
    gap: 0;
    flex: 1 1 0;
    min-width: 280px;
    background: transparent;
    overflow-y: auto;
    overflow-x: hidden;
    height: 100%;
    max-height: 100%;
    padding-right: 8px;
  }

  .component-card {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 20px 12px;
    border: none;
    border-bottom: 1px solid var(--border, rgba(0, 0, 0, 0.12));
    min-width: 200px;
    background: none;
  }

  .component-card:last-child {
    border-bottom: none;
  }

  .component-thumb {
    width: 64px;
    height: 64px;
    display: grid;
    place-items: center;
    overflow: hidden;
    flex-shrink: 0;
  }

  .component-thumb img {
    max-width: 56px;
    max-height: 56px;
    object-fit: contain;
  }

  .component-info {
    display: flex;
    flex-direction: column;
    gap: 2px;
  }

  .component-name {
    font-size: 0.9rem;
    font-weight: 600;
    color: var(--primary, #222);
  }

  .component-id {
    font-size: 0.8rem;
    color: var(--secondary, #717171);
  }

  .component-status {
    font-size: 0.8rem;
    font-weight: 600;
    margin-top: 2px;
  }

  .component-status.Running {
    color: var(--info, #3b82f6);
  }

  .component-status.Live {
    color: var(--success, #22c55e);
  }

  .component-status.Online {
    color: var(--success, #22c55e);
  }

  .component-status.Idle {
    color: var(--secondary, #717171);
  }

  .component-status.Off {
    color: var(--danger, #ef4444);
  }

  /* Numeric values like 0, 1 for sensors */
  .component-status[class~="0"] {
    color: var(--secondary, #717171);
  }

  .component-status:is(
      [class~="1"],
      [class~="2"],
      [class~="3"],
      [class~="4"],
      [class~="5"],
      [class~="6"],
      [class~="7"],
      [class~="8"],
      [class~="9"]
    ) {
    color: var(--info, #3b82f6);
  }

  @media (max-width: 768px) {
    .components-page {
      flex-direction: column;
      gap: 20px;
    }

    .components-page.with-drawer {
      flex-direction: column;
      gap: 24px;
    }

    .units-column {
      flex: 1 1 auto;
      max-width: none;
      width: 100%;
    }

    .components-page.with-drawer .units-column {
      flex: 1 1 auto;
      max-width: none;
      width: 100%;
    }

    .components-column {
      width: 100%;
      min-width: auto;
    }

    .component-card {
      min-width: auto;
    }
  }
</style>
<script>
  import { onMount } from "svelte";
  import UnitCard from "../components/UnitCard.svelte";
  import RightDrawer from "../components/RightDrawer.svelte";

  import full from "../../assets/inverntory/Full.svg?url";
  import partial from "../../assets/inverntory/Partial.svg?url";
  import empty from "../../assets/inverntory/Empty.svg?url";
  import conveyorReal from "../../assets/inverntory/Conveyor_Unit _1.png?url";
  import stepperImg from "../../assets/inverntory/Stepper Motor 57x56mm.png?url";
  import proximityImg from "../../assets/inverntory/Proximity Sensor.png?url";
  import jetsonImg from "../../assets/inverntory/Jetson Orin Nano.png?url";
  import dcImg from "../../assets/inverntory/Greartisan DC 24V.png?url";

  // Ordered list of statuses we rotate through to simulate live updates.
  const STATUS_SEQUENCE = ["Running", "Live", "Online", "Idle", "Off"];

  // Return the next status in the sequence, wrapping back to the start.
  const nextStatus = (value) => {
    const index = STATUS_SEQUENCE.indexOf(value);
    if (index === -1) {
      return STATUS_SEQUENCE[0];
    }
    return STATUS_SEQUENCE[(index + 1) % STATUS_SEQUENCE.length];
  };

  // Base inventory definition. We clone this structure so the interval-driven
  // animation never mutates the source data.
  const baseUnits = [
    {
      id: "CV1",
      name: "Conveyor_Unit _1",
      image: conveyorReal,
      subcomponents: [
        {
          id: "SM1",
          name: "Stepper Motor 57x56mm",
          status: "Running",
          image: stepperImg,
        },
        {
          id: "PS1",
          name: "Proximity Sensor",
          status: "Live",
          image: proximityImg,
        },
        {
          id: "PS2",
          name: "Proximity Sensor",
          status: "Live",
          image: proximityImg,
        },
        {
          id: "JO1",
          name: "Jetson Orin Nano",
          status: "Online",
          image: jetsonImg,
        },
        {
          id: "GD1",
          name: "Greartisan DC 24V",
          status: "Idle",
          image: dcImg,
        },
      ],
    },
    {
      id: "CV1B",
      name: "Conveyor_Unit _1",
      image: partial,
      subcomponents: [
        {
          id: "SM2",
          name: "Stepper Motor 57x56mm",
          status: "Running",
          image: full,
        },
        {
          id: "GD1",
          name: "Greatisan DC 24V",
          status: "Idle",
          image: partial,
        },
        {
          id: "PS3",
          name: "Proximity Sensor",
          status: "Live",
          image: partial,
        },
      ],
    },
    {
      id: "CV2",
      name: "Conveyor_Unit _2",
      image: empty,
      subcomponents: [
        {
          id: "SM3",
          name: "Stepper Motor 57x56mm",
          status: "Off",
          image: full,
        },
        {
          id: "PS4",
          name: "Proximity Sensor",
          status: "Idle",
          image: partial,
        },
      ],
    },
  ];

  // Live copy used by the UI; each interval tick creates new objects so Svelte
  // reactivity picks up the changes without mutating the originals.
  let units = baseUnits.map((unit) => ({
    ...unit,
    subcomponents: unit.subcomponents.map((subcomponent) => ({
      ...subcomponent,
    })),
  }));

  let open = false;
  let selectedUnit = null;

  // Drawer controls keep the experience view-only while allowing toggling.
  const closeDrawer = () => {
    open = false;
    selectedUnit = null;
  };

  const openDrawer = (unit) => {
    if (open && selectedUnit?.id === unit.id) {
      closeDrawer();
      return;
    }
    selectedUnit = unit;
    open = true;
  };

  // Rotate subcomponent statuses every two seconds to mimic live telemetry.
  onMount(() => {
    const interval = setInterval(() => {
      const nextUnits = units.map((unit) => ({
        ...unit,
        subcomponents: unit.subcomponents.map((subcomponent) => ({
          ...subcomponent,
          status: nextStatus(subcomponent.status),
        })),
      }));

      units = nextUnits;

      if (selectedUnit) {
        const refreshed = nextUnits.find((unit) => unit.id === selectedUnit.id);
        if (refreshed) {
          selectedUnit = refreshed;
        } else {
          selectedUnit = null;
          open = false;
        }
      }
    }, 2000);

    return () => {
      clearInterval(interval);
    };
  });
</script>

<div class="components-page" class:with-drawer={open}>
  <div class="units-column">
    {#each units as unit (unit.id)}
      <UnitCard
        {unit}
        active={open && selectedUnit?.id === unit.id}
        hideCount={open}
        hideArrow={open}
        on:open={() => openDrawer(unit)}
      />
    {/each}
  </div>

  <RightDrawer
    {open}
    onClose={closeDrawer}
    title={selectedUnit?.name ?? ""}
    subtitle={selectedUnit ? `( ID: ${selectedUnit.id} )` : ""}
    image={selectedUnit?.image ?? ""}
    items={selectedUnit?.subcomponents ?? []}
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

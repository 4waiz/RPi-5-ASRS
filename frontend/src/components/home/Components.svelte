<script>
  import UnitCard from "./UnitCard.svelte";
  import RightDrawer from "./RightDrawer.svelte";
  import { onMount, onDestroy } from "svelte";
  import { writable } from "svelte/store";
  import { t } from "../../lib/i18n";

  // --- CONFIGURATION ---
  //const API_URL = "http://127.0.0.1:8007/system-status"; 
  const API_URL = "http://192.168.208.146:8007/system-status";
  const POLL_INTERVAL = 3000; // Update every 3 seconds

  // --- STORE DEFINITION ---
  const createSystemStore = () => {
    const { subscribe, set } = writable({ 
      units: [], 
      online: false, 
      lastUpdated: null 
    });

    let interval;

    const fetchData = async () => {
      try {
        const res = await fetch(API_URL);
        if (res.ok) {
          const data = await res.json();
          set({ 
            units: data, 
            online: true, 
            lastUpdated: new Date().toISOString() 
          });
        } else {
          // Keep old data but mark offline
          set(state => ({ ...state, online: false }));
        }
      } catch (err) {
        console.error("API Error:", err);
        set(state => ({ ...state, online: false }));
      }
    };

    const start = () => {
      fetchData(); // Initial fetch
      interval = setInterval(fetchData, POLL_INTERVAL);
    };

    const stop = () => clearInterval(interval);

    return { subscribe, start, stop };
  };

  const systemStore = createSystemStore();

  // --- LIFECYCLE ---
  onMount(() => systemStore.start());
  onDestroy(() => systemStore.stop());

  // --- REACTIVE STATE (Svelte 5 Runes) ---
  let systemState = $derived($systemStore);
  let backendOnline = $derived(systemState.online);
  
  // Translation & Mapping Logic
  // We process the API data to add translations and UI helpers
  let unitsWithStatus = $derived(systemState.units.map((unit) => {
    return {
      ...unit,
      translatedName: $t(unit.name) || unit.name, // Try translating subsystem name
      subcomponents: unit.subcomponents.map((comp) => {
        // Map Status to Translation Key
        // e.g. "idle" -> "components.status.idle"
        const statusKey = `components.status.${comp.status.toLowerCase()}`;
        const translatedStatus = $t(statusKey) !== statusKey ? $t(statusKey) : comp.status;

        return {
          ...comp,
          // If translation exists for component name, use it; otherwise use DB name
          translatedName: $t(`components.${comp.id}`) !== `components.${comp.id}` 
            ? $t(`components.${comp.id}`) 
            : comp.name,
          
          status: backendOnline ? comp.status : "Offline",
          translatedStatus: backendOnline ? translatedStatus : $t("components.status.offline"),
          
          // CRITICAL: The API sends 'image_path', we map it to 'image' for your UI
          image: comp.image ? `/${comp.image.split('\\').join('/').replace(/ /g, '%20')}` : null
        };
      }),
    };
  }));

  // Drawer Logic
  let open = $state(false);
  let selectedUnitId = $state(null);
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
/* ... Keep your existing styles ... */
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
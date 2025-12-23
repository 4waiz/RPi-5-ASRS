<script>
  import { onMount } from "svelte";
  import CircularProgressBar from "../charts/Circular-Progress-Bar.svelte";
  import Tem from "../charts/Tem.svelte";
  import NumericData from "../charts/numeric-data.svelte";
  import NumericalGraph from "../charts/numerical-graph.svelte";
  import AbstractInventory from "../shared/abstract-inventory.svelte";
  import { t } from "../../lib/i18n";

  let Cl = [80, 20];
  // Overview metrics variables
  let PickingAccuracy = $state(0);
  let InventoryAccuracy = $state(0);
  let temperature = $state(0);
  let Availability = $state(0);
  let throughputValue = $state(0);
  let cycleTime = $state(0);
  let energyConsumed = $state(0);
  let cpuLoad = $state(0);

  // Initialize slot status variables
  let full = $state(0);
  let pariallyFull = $state(0);
  let empty = $state(0);

  // Fetch dashboard stats from API
  async function fetchDashboardStats() {
    try {
      const response = await fetch("/api/dashboard/stats");
      if (!response.ok) throw new Error("Failed to fetch dashboard stats");
      const data = await response.json();

      // Update metrics (convert decimals to percentages where needed)
      PickingAccuracy = Math.round(data.picking_accuracy * 100);
      InventoryAccuracy = Math.round(data.inventory_accuracy * 100);
      temperature = data.temperature;
      Availability = Math.round(data.availability * 100);
      throughputValue = data.throughput;
      cycleTime = data.cycle_time;
      energyConsumed = data.energy_per_cycle;
      cpuLoad = data.cpu_load;
    } catch (error) {
      console.error("Error fetching dashboard stats:", error);
    }
  }

  // Fetch inventory data from API
  async function fetchInventorySlots() {
    try {
      const response = await fetch("/api/inventory");
      if (!response.ok) throw new Error("Failed to fetch inventory slots");
      const data = await response.json();

      // Count slots by status
      full = data.filter(slot => slot.status === "Full").length;
      pariallyFull = data.filter(slot => slot.status === "Partially full").length;
      empty = data.filter(slot => slot.status === "Empty").length;
    } catch (error) {
      console.error("Error fetching inventory slots:", error);
    }
  }

  // On mount, fetch data and refresh every 1 second
  onMount(() => {
    fetchDashboardStats();
    fetchInventorySlots();
    const interval = setInterval(() => {
      fetchDashboardStats();
      fetchInventorySlots();
    }, 1000);
    return () => clearInterval(interval);
  });
</script>

<div class="row">
  <div class="column1">
    <CircularProgressBar Name={$t('overview.pickingAccuracy')} Present={PickingAccuracy} />
    <div class="hd"></div>
    <CircularProgressBar
      Name={$t('overview.inventoryAccuracy')}
      Present={InventoryAccuracy}
    />
  </div>

  <div class="vd"></div>

  <div class="column1">
    <Tem value={temperature} />
    <div class="hd"></div>
    <CircularProgressBar Name={$t('overview.availability')} Present={Availability} />
  </div>

  <div class="vd"></div>

  <div class="column2">
    <NumericData value={throughputValue} unit="Ops/h" label={$t('overview.throughput')} />
    <div class="hd"></div>
    <NumericData value={cycleTime} unit="min/cycle" label={$t('overview.cycleTime')} />
    <div class="hd"></div>
    <NumericData value={energyConsumed} unit="w/Cycle" label={$t('overview.energyCycle')} />
  </div>
  <div class="column3">
    <AbstractInventory {full} {pariallyFull} {empty} />
    <NumericalGraph value={cpuLoad} unit="Milliseconds" label={$t('overview.cpuOverload')} />
  </div>
</div>

<style>
  .column1 {
    display: flex;
    width: 112.78px;
    flex-direction: column;
    align-items: flex-end;
    gap: 16px;
  }
  .hd {
    height: 1.5px;
    width: 100%;
    background-color: rgba(0, 0, 0, 0.08);
  }
  .column2 {
    display: flex;
    width: 112.78px;
    flex-direction: column;
    align-items: flex-start;
    gap: 40px;
  }
  .column3 {
    display: flex;
    width: 249.6px;
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  .row {
    display: flex;
    align-items: flex-start;
    gap: 32px;
  }
  .vd {
    flex: 0 0 1.5px; /* fixed 2px width, no growth */
    background-color: #000000; /* your color */
    opacity: 0.08; /* optional: softer line */
    align-self: stretch; /* if you keep flex-start on the row, add this */
    /* no height needed */
  }
</style>

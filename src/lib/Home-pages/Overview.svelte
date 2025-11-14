<script>
  import { onMount, onDestroy } from "svelte";
  import CircularProgressBar from "../Statistical charts/Circular-Progress-Bar.svelte";
  import Temperature from "../Statistical charts/Temperature.svelte";
  import NumericData from "../Statistical charts/numeric-data.svelte";

  /* inventory icons (paths match your repo) */
  import Empty   from "../../assets/inventory/Empty.svg";
  import Full    from "../../assets/inventory/Full.svg";
  import Partial from "../../assets/inventory/Partial.svg";

  const icons = { full: Full, empty: Empty, partial: Partial };

  // Live reactive data
  let carStock = $state(100);
  let helicopterStock = $state(10);
  let processorTemp = $state(45);
  let ambientTemp = $state(23);
  let energyConsumption = $state(120);
  let humidity = $state(65);
  let asrsUtilization = $state(25);

  /* demo slot states - 7 in storage, 8 out storage, 1 out of stock */
  let slots = $state([
    "full","full","full","full","full","full","full",  // 7 in storage
    "partial","partial","partial","partial","partial","partial","partial","partial",  // 8 out storage
    "empty"  // 1 out of stock
  ]);

  let counts = $derived({
    full: slots.filter((s) => s === "full").length,
    partial: slots.filter((s) => s === "partial").length,
    empty: slots.filter((s) => s === "empty").length,
  });

  let interval;

  // Utility function to generate realistic fluctuations
  function fluctuate(current, min, max, change = 3) {
    const delta = (Math.random() - 0.5) * change;
    let newValue = current + delta;
    return Math.min(Math.max(newValue, min), max);
  }

  // Simulate live data updates
  function updateData() {
    // Stock levels change occasionally (0-100%)
    if (Math.random() > 0.7) {
      carStock = Math.round(fluctuate(carStock, 0, 100, 5));
    }
    if (Math.random() > 0.7) {
      helicopterStock = Math.round(fluctuate(helicopterStock, 0, 100, 8));
    }

    // Temperatures fluctuate with wider range for more visible changes
    processorTemp = Math.round(fluctuate(processorTemp, 20, 140, 8));
    ambientTemp = Math.round(fluctuate(ambientTemp, 10, 80, 6));

    // Energy consumption varies
    energyConsumption = Math.round(fluctuate(energyConsumption, 80, 180, 5));

    // Humidity changes slowly
    humidity = Math.round(fluctuate(humidity, 40, 80, 2));

    // ASRS utilization varies based on activity
    asrsUtilization = Math.round(fluctuate(asrsUtilization, 10, 95, 6));

    // Occasionally change inventory slots
    if (Math.random() > 0.85) {
      const randomIndex = Math.floor(Math.random() * slots.length);
      const states = ["full", "partial", "empty"];
      slots[randomIndex] = states[Math.floor(Math.random() * states.length)];
    }
  }

  let isVisible = $state(true);

  onMount(() => {
    // Start interval only when visible
    if (isVisible) {
      interval = setInterval(updateData, 2000);
    }

    // Pause/resume based on page visibility
    const handleVisibilityChange = () => {
      if (document.hidden) {
        // Page is hidden, stop the interval
        if (interval) {
          clearInterval(interval);
          interval = null;
        }
        isVisible = false;
      } else {
        // Page is visible again, restart the interval
        isVisible = true;
        if (!interval) {
          interval = setInterval(updateData, 2000);
        }
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);

    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      if (interval) {
        clearInterval(interval);
      }
    };
  });

  onDestroy(() => {
    if (interval) {
      clearInterval(interval);
    }
  });
</script>

<div class="main-container">
  <div class="row">
    <!-- Column 1 -->
    <div class="column1">
      <CircularProgressBar Name="Car Stock" Present={carStock} />
      <div class="hd"></div>
      <Temperature Temperature={processorTemp} max={160} label="Processor Temperature" />
    </div>

    <div class="vd"></div>

    <!-- Column 2 -->
    <div class="column1">
      <CircularProgressBar Name="Helicopter Stock" Present={helicopterStock} />
      <div class="hd"></div>
      <Temperature Temperature={ambientTemp} max={160} label="Ambient Temperature" />
    </div>

    <div class="vd"></div>

    <!-- Column 3 -->
    <div class="column2">
      <NumericData value={energyConsumption} unit="kWh" label="Energy Consumption" />
      <div class="hd"></div>
      <NumericData value={humidity} unit="%" label="Humidity" />
      <div class="hd"></div>
      <NumericData value={asrsUtilization} unit="%" label="ASRS Utilization" />
    </div>

    <div style="flex:0 0 0px;"></div>


    <!-- Inventory status on the RIGHT -->
    <div class="inventory-status-container">
      <div class="container">
        <h3>Inventory status</h3>

        <div class="grid">
          {#each slots as state, i}
            <img
              class="cell"
              src={icons[state]}
              alt={`slot-${i}-${state}`}
              width="27"
              height="18"
            />
          {/each}
        </div>

        <div class="legend">
          <div class="legend-item">
            <img class="legend-icon" src={icons.full} alt="In Storage" />
            <span><strong>{counts.full}</strong> : In Storage</span>
          </div>

          <div class="legend-item">
            <img class="legend-icon" src={icons.partial} alt="Out Storage" />
            <span><strong>{counts.partial}</strong> : Out Storage</span>
          </div>

          <div class="legend-item">
            <img class="legend-icon" src={icons.empty} alt="Out of stock" />
            <span><strong>{counts.empty}</strong> : Out of stock</span>
          </div>
        </div>

        <button class="manage-btn">Managing Inventory →</button>
      </div>
    </div>
  </div>
</div>

<style>
  .main-container {
    display: flex;
    flex-direction: column;
    gap: 32px;
  }

  .column1 {
    display: flex;
    width: 140px;
    flex-direction: column;
    align-items: center;
    gap: 16px;
  }

  .hd {
    height: 1.5px;
    width: 100%;
    background-color: rgba(0, 0, 0, 0.08);
  }

  .column2 {
    display: flex;
    width: 140px;
    flex-direction: column;
    align-items: flex-start;
    gap: 40px;
  }

  .row {
    display: flex;
    align-items: center;
    gap: 32px;
  }

  .vd {
    flex: 0 0 1.5px;
    background-color: #000000;
    opacity: 0.08;
    align-self: stretch;
  }

  .inventory-status-container {
    display: flex;
    justify-content: flex-start;
    margin-top: 0;
  }

  /* Card */
  .container {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    width: fit-content;
    padding: 16px 20px;
    border-radius: 20px;
    border: 1px solid rgba(0, 0, 0, 0.3);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  }

  h3 {
    color: #000;
    font-size: 18px;
    font-weight: 700;
    margin: 0 0 14px 0;
  }

  /* Grid */
  .grid {
    display: grid;
    grid-template-columns: repeat(4, 27px);
    gap: 12px 32px;
    justify-content: center;
    margin-bottom: 18px;
  }

  .cell {
    width: 27px;
    height: 18px;
    display: block;
  }

  /* Legend */
  .legend {
    width: 100%;
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 6px;
    margin-bottom: 14px;
  }

  .legend-item {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 13px;
    color: #333;
  }

  .legend-icon {
    width: 27px;
    height: 18px;
    display: block;
    flex-shrink: 0;
  }

  /* Button */
  .manage-btn {
    width: 100%;
    padding: 10px 0;
    border-radius: 10px;
    font-size: 15px;
    font-weight: 500;
    color: #333;
    cursor: pointer;
    border-radius: 8.76px;
    border: 1.095px solid rgba(0, 0, 0, 0.68);
    background-color: rgba(0, 0, 0, 0);
    transition: all 0.2s ease;
  }
  .manage-btn:hover { background-color: rgba(0, 0, 0, 0.05); }
</style>

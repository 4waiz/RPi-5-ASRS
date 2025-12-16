<script lang="ts">
  import { ActiveTapHomePag } from "../../stores/AppStore.js";
  import Full from "../../assets/inventory/Full.svg";
  import Partial from "../../assets/inventory/Partial.svg";
  import Empty from "../../assets/inventory/Empty.svg";
  let { full = 14, pariallyFull = 5, empty = 5 } = $props();
  let total = 24;
  let fullPercent = (full / total) * 197;
  let partialPercent = (pariallyFull / total) * 197;
  let emptyPercent = (empty / total) * 197;
</script>

<div class="container">
  <h3>Inventory status</h3>
  <!-- Grid -->
  <div class="bar-container">
    <div class="bar" style="width:{fullPercent}px; background-color:green;"></div>
    <div class="bar" style="width: {partialPercent}px; background-color:gray;"></div>
    <div class="bar" style="width: {emptyPercent}px; background-color:red"></div>
  </div>

  <!-- Legend -->
  <div class="legend">
    <div class="legend-row">
      <div class="legend-item small">
        <img class="legend-icon" src={Full} alt="Full" />
        <span><strong>{full}</strong> : Full</span>
      </div>

      <div class="legend-item small">
        <img class="legend-icon" src={Empty} alt="Empty" />
        <span><strong>{empty}</strong> : Empty</span>
      </div>
    </div>

    <div class="legend-item">
      <img class="legend-icon" src={Partial} alt="Partial" />
      <span><strong>{pariallyFull}</strong> : Partially full</span>
    </div>
  </div>

  <button class="manage-btn" onclick={()=>{ActiveTapHomePag.set(1)}}>Managing Inventory →</button>
</div>

<style>
  /* === Container === */
  .container {
    margin-left: 16px;
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    width: fit-content;
    padding: 16px 20px;
    border-radius: 20px;
    border: 1px solid rgba(0, 0, 0, 0.3);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    height: fit-content;
  }

  .bar-container {
    display: flex;
    flex-direction: row;
    height: 18px;
    width: 197px;
    align-items: flex-start;
    align-content: flex-start;
    gap: 4px;
    align-self: stretch;
  }

  .bar {
    height: 18px;
    border-radius: 9px;
  }

  h3 {
    color: #000;
    font-size: 18px;
    font-weight: 700;
    margin: 0 0 14px 0;
  }

  /* === Legend === */
  .legend {
    width: 10%;
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
    margin-bottom: 14px;
  }

  .legend-row {
    display: flex;
    margin-top: 16px;
  }

  .legend-item {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 13px;
    color: #333;
    min-width: 200px;
  }

  .small {
    min-width: 104px;
  }

  .legend-icon {
    width: 27px;
    height: 18px;
    display: block;
    flex-shrink: 0;
  }

  /* === Button === */
  .manage-btn {
    width: 100%;
    height: 48px;
    padding: 10px 0;
    font-size: 15px;
    font-weight: 500;
    color: #333;
    cursor: pointer;
    border-radius: 12px;
    border: 1.095px solid rgba(0, 0, 0, 0.32);
    background-color: rgba(0, 0, 0, 0);
  }
</style>

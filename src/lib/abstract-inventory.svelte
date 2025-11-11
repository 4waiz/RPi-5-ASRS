<script lang="ts">
  import Empty from "../assets/inventory/Empty.svg";
  import Full from "../assets/inventory/Full.svg";
  import Partial from "../assets/inventory/Partial.svg";

  let {slots} = $props();
  const icons = { full: Full, empty: Empty, partial: Partial } as const;

  let counts = {
    full: slots.filter((s) => s === "full").length,
    empty: slots.filter((s) => s === "empty").length,
    partial: slots.filter((s) => s === "partial").length,
  };
</script>

<div class="container">
  <h3>Inventory status</h3>

  <!-- Grid -->
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

  <!-- Legend -->
  <div class="legend">
    <div class="legend-row">
      <div class="legend-item">
        <img class="legend-icon" src={icons.full} alt="Full" />
        <span><strong>{counts.full}</strong> : Full</span>
      </div>

      <div class="legend-item">
        <img class="legend-icon" src={icons.empty} alt="Empty" />
        <span><strong>{counts.empty}</strong> : Empty</span>
      </div>
    </div>

    <div class="legend-item">
      <img class="legend-icon" src={icons.partial} alt="Partial" />
      <span><strong>{counts.partial}</strong> : Partially full</span>
    </div>
  </div>

  <button class="manage-btn">Managing Inventory →</button>
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
  }

  h3 {
    color: #000;
    font-size: 18px;
    font-weight: 700;
    margin: 0 0 14px 0;
  }

  /* === Grid === */
  .grid {
    display: grid;
    grid-template-columns: repeat(4, 27px);
    gap: 12px 32px; /* row-gap / column-gap */
    justify-content: center;
    margin-bottom: 18px;
  }

  .cell {
    width: 27px;
    height: 18px;
    display: block;
  }

  /* === Legend === */
  .legend {
    width: 100%;
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
    margin-bottom: 14px;
  }

  .legend-row {
    display: flex;
    gap: 20px;
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

  /* === Button === */
  .manage-btn {
    width: 100%;
    padding: 10px 0;
    border-radius: 10px;
    font-size: 15px;
    font-weight: 500;
    color: #333;
    cursor: pointer;
    border-radius: 8.76px;
    border: 1.095px solid rgba(0, 0, 0, 0.32);
    background-color: rgba(0, 0, 0, 0);
  }

</style>

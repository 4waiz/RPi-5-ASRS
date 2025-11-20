<script>
  let { slots = [] } = $props();
</script>

<div class="inventory-status">
  <h3 class="title">Inventory Status</h3>
  <div class="slots-container">
    {#each slots as slot, index}
      <div class="slot {slot}" title="Slot {index + 1}: {slot}">
        <span class="slot-number">{index + 1}</span>
      </div>
    {/each}
  </div>
  <div class="legend">
    <div class="legend-item">
      <div class="legend-color full"></div>
      <span>Full</span>
    </div>
    <div class="legend-item">
      <div class="legend-color partial"></div>
      <span>Partial</span>
    </div>
    <div class="legend-item">
      <div class="legend-color empty"></div>
      <span>Empty</span>
    </div>
  </div>
</div>

<style>
  .inventory-status {
    display: flex;
    flex-direction: column;
    gap: 12px;
    padding: 16px;
    background: var(--bg-card, white);
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    transition: background 0.3s ease;
  }

  .title {
    font-size: 1rem;
    font-weight: 600;
    color: var(--primary, #424242);
    margin: 0;
    text-align: center;
  }

  .slots-container {
    display: grid;
    grid-template-columns: repeat(6, 1fr);
    gap: 8px;
    padding: 8px 0;
  }

  .slot {
    aspect-ratio: 1;
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.75rem;
    font-weight: 600;
    color: white;
    cursor: pointer;
    transition: all 0.2s;
    border: 2px solid transparent;
  }

  .slot.full {
    background: #4CAF50;
  }

  .slot.partial {
    background: #FFA726;
  }

  .slot.empty {
    background: #E0E0E0;
    color: #757575;
  }

  .slot-number {
    font-size: 0.7rem;
  }

  .legend {
    display: flex;
    justify-content: center;
    gap: 16px;
    padding-top: 8px;
    border-top: 1px solid var(--border, #E0E0E0);
  }

  .legend-item {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 0.85rem;
    color: var(--secondary, #757575);
  }

  .legend-color {
    width: 16px;
    height: 16px;
    border-radius: 4px;
  }

  .legend-color.full {
    background: #4CAF50;
  }

  .legend-color.partial {
    background: #FFA726;
  }

  .legend-color.empty {
    background: #E0E0E0;
  }
</style>

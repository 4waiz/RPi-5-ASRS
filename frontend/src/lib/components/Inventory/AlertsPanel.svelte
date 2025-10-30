<script>
  import SmallAlert from "../../small-alert.svelte";
  import { inventoryStore } from "../../stores/inventory.js";

  const MAX_QUALITY_ALERTS = 4;

  $: state = $inventoryStore;
  $: stockAlerts = state.items.filter((item) => item.hasAlert || item.qty === 0);
  $: qualityAlerts = state.liveEvents
    .filter((event) => event.type === "reject")
    .slice(0, MAX_QUALITY_ALERTS);

  function formatTime(time) {
    if (!time) return "";
    try {
      return new Date(time).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    } catch {
      return "";
    }
  }
</script>

<section class="alerts-panel" aria-label="Inventory alerts">
  <header>
    <h2>Alerts</h2>
  </header>

  {#if stockAlerts.length === 0 && qualityAlerts.length === 0}
    <p class="empty">No active alerts.</p>
  {:else}
    <div class="alerts">
      {#each stockAlerts as box (box.id)}
        <SmallAlert
          Massage={`Box ${box.id} stockout${box.sku ? ` for ${box.sku}` : ""}`}
          Type="Alert"
          Time={formatTime(box.lastOpAt)}
        />
      {/each}

      {#each qualityAlerts as event (event.id)}
        <SmallAlert Massage={event.message} Type="Alert" Time={formatTime(event.at)} />
      {/each}
    </div>
  {/if}
</section>

<style>
  .alerts-panel {
    display: flex;
    flex-direction: column;
    gap: 12px;
    padding: 16px;
    border-radius: 16px;
    border: 1px solid rgba(0, 0, 0, 0.08);
    background: #fff;
    min-height: 180px;
  }

  header h2 {
    margin: 0;
    font-size: 1.1rem;
    font-weight: 600;
    color: rgba(0, 0, 0, 0.87);
  }

  .alerts {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .empty {
    margin: 0;
    color: rgba(0, 0, 0, 0.5);
    font-style: italic;
  }
</style>

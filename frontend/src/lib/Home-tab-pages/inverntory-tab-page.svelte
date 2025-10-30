<script>
  import { onMount } from "svelte";
  import inventoryImage from "../../assets/inverntory/inventory storage.png";
  import {
    inventoryStore,
    kpiCounts,
    setStatus,
  } from "../stores/inventory.js";
  import { loadInventory, subscribeRealtime } from "../services/inventoryService.js";

  const BIN_COUNT = 20;
  const GRID_COLUMNS = 4;

  // Percent-based coordinates measured from the inventory image so overlay slots line up with the bins.
  const ROW_POSITIONS = [17.977, 32.14, 46.198, 60.09, 74.077];
  const COLUMN_POSITIONS = [24.499, 36.514, 51.105, 64.411];
  const CELL_WIDTH_PERCENT = 8.084;
  const CELL_HEIGHT_PERCENT = 6.948;

  const cellLayout = Array.from({ length: BIN_COUNT }, (_, index) => {
    const row = Math.floor(index / GRID_COLUMNS);
    const column = index % GRID_COLUMNS;

    return {
      top: ROW_POSITIONS[row] ?? 0,
      left: COLUMN_POSITIONS[column] ?? 0,
      width: CELL_WIDTH_PERCENT,
      height: CELL_HEIGHT_PERCENT,
    };
  });

  let unsubscribeRealtime = () => {};

  $: state = $inventoryStore;
  $: counts = $kpiCounts;
  $: bins = createBins(state.items ?? []);
  $: latestEvents = (state.liveEvents ?? []).slice(0, 2);
  $: showSkeleton = state.status === "loading" && !state.items?.length;

  $: primaryAlertBox =
    bins.find((box) => box.hasAlert) ??
    bins.find((box) => box.status === "empty") ??
    bins.find((box) => box.id === 8) ??
    null;

  $: secondaryAlertMessage =
    (state.liveEvents ?? []).find((event) => event.type === "reject")?.message ??
    "The supplier item with ID 9 has been rejected as it does not meet the quality standards.";

  function formatEventTime(timestamp) {
    if (!timestamp) return "Done at --";
    return `Done at ${timestamp}`;
  }

  function createBins(items) {
    const map = new Map();
    items.forEach((item) => {
      if (item?.id) {
        map.set(item.id, {
          ...item,
          status: normalizeStatus(item.status),
        });
      }
    });

    return Array.from({ length: BIN_COUNT }, (_, index) => {
      const id = index + 1;
      return (
        map.get(id) ?? {
          id,
          status: "empty",
          hasAlert: false,
          sku: null,
        }
      );
    });
  }

  function normalizeStatus(status) {
    const normalized = String(status ?? "").toLowerCase();
    if (normalized === "full" || normalized === "partial" || normalized === "empty") {
      return normalized;
    }
    return "empty";
  }

  function attachRealtime() {
    unsubscribeRealtime?.();
    unsubscribeRealtime = subscribeRealtime();
  }

  async function hydrateInventory() {
    setStatus("loading", null);
    await loadInventory();
    attachRealtime();
  }

  async function handleRetry() {
    await hydrateInventory();
  }

  onMount(() => {
    let active = true;
    (async () => {
      await hydrateInventory();
      if (!active) {
        unsubscribeRealtime?.();
      }
    })();

    return () => {
      active = false;
      unsubscribeRealtime?.();
    };
  });
</script>

<div class="inventory-page">
  {#if showSkeleton}
    <div class="skeleton layout"></div>
  {:else}
    <div class="layout">
      <section class="left-column">
        <div class="live-ops">
          <h2 class="live-ops-header">Live Operations</h2>
          <div class="event-stack">
          {#if latestEvents.length === 0}
            <div class="event-card empty-card">
              <p>No operations yet.</p>
            </div>
          {:else}
            {#each latestEvents as event (event.id)}
              <article class="event-card">
                <div class="event-icon" aria-hidden="true">
                  <svg viewBox="0 0 20 20" focusable="false">
                    <path
                      d="M8.293 13.293 5.5 10.5l1.414-1.414L8.293 10.464l4.793-4.793 1.414 1.414z"
                      fill="#2e7d32"
                    />
                  </svg>
                </div>
                <div class="event-copy">
                  <strong>{event.message ?? `Box ${event.boxId} update`}</strong>
                  <span>{formatEventTime(event.at)}</span>
                </div>
              </article>
            {/each}
            {#if latestEvents.length === 1}
              <article class="event-card placeholder-card">
                <div class="event-icon muted" aria-hidden="true">
                  <svg viewBox="0 0 20 20" focusable="false">
                    <path
                      d="M8.293 13.293 5.5 10.5l1.414-1.414L8.293 10.464l4.793-4.793 1.414 1.414z"
                      fill="#2e7d32"
                    />
                  </svg>
                </div>
                <div class="event-copy">
                  <strong>Waiting for next operation</strong>
                  <span>Done at --</span>
                </div>
              </article>
            {/if}
          {/if}
          </div>
        </div>

        <div class="legend">
          <div class="legend-item full">
            <span class="dot"></span>
            <span>{counts.full ?? 0} : Full</span>
          </div>
          <div class="legend-item partial">
            <span class="dot"></span>
            <span>{counts.partial ?? 0} Partially full</span>
          </div>
          <div class="legend-item empty">
            <span class="dot"></span>
            <span>{counts.empty ?? 0} Empty</span>
          </div>
        </div>
      </section>

      <section class="right-column">
        <div class="storage-frame">
          <img class="storage-image" src={inventoryImage} alt="Automated storage system" />
          <div class="overlay-grid" aria-hidden="true">
            {#each bins as box, index (box.id)}
              <div
                class="overlay-cell {box.status} {box.id === (primaryAlertBox?.id ?? null) ? 'alert' : ''}"
                style={`top:${cellLayout[index]?.top ?? 0}%; left:${cellLayout[index]?.left ?? 0}%; width:${
                  cellLayout[index]?.width ?? CELL_WIDTH_PERCENT
                }%; height:${cellLayout[index]?.height ?? CELL_HEIGHT_PERCENT}%;`}
              >
                <span class="number">{box.id}</span>
                {#if box.id === (primaryAlertBox?.id ?? null)}
                  <span class="alert-badge" aria-label="Alert">
                    <svg viewBox="0 0 16 16" focusable="false">
                      <path
                        d="M8.94 2.34a1 1 0 0 0-1.88 0L2.2 12.17A1 1 0 0 0 3.09 13.6h9.82a1 1 0 0 0 .9-1.43z"
                        fill="currentColor"
                      />
                      <rect x="7.25" y="5" width="1.5" height="4.5" rx=".75" fill="#fff" />
                      <rect x="7.25" y="10.5" width="1.5" height="1.5" rx=".75" fill="#fff" />
                    </svg>
                  </span>
                {/if}
              </div>
            {/each}
          </div>
        </div>
      </section>
    </div>
  {/if}

  <div class="alerts">
    <div class="alert-banner critical" role="alert">
      <div class="alert-copy">
        <span aria-hidden="true">⚠️</span>
        <p>
          {primaryAlertBox
            ? `There is no available stock in the Box ${primaryAlertBox.id} to meet the incoming orders.`
            : "There is no available stock in the Box 8 to meet the incoming orders."}
        </p>
      </div>
      <span class="alert-time">Now</span>
    </div>
    <div class="alert-banner caution" role="status">
      <div class="alert-copy">
        <span aria-hidden="true">⚠️</span>
        <p>{secondaryAlertMessage}</p>
      </div>
      <span class="alert-time">Now</span>
    </div>
  </div>
</div>

<style>
  .inventory-page {
    display: flex;
    flex-direction: column;
    gap: 36px;
    padding: 32px 40px 36px;
    background: #f5f7fa;
  }

  .layout {
    display: grid;
    grid-template-columns: 436px minmax(0, 1fr);
    gap: 24px;
    align-items: flex-start;
  }

  .left-column {
    position: relative;
    width: 100%;
    padding: 0 18px 0 0;
    box-sizing: border-box;
  }

  .live-ops {
    position: relative;
    padding: 0 0 16px 18px;
  }

  .live-ops::after {
    content: "";
    position: absolute;
    top: calc(28px + 8px);
    bottom: 8px;
    left: 0;
    width: 3px;
    border-radius: 2px;
    background: #1e66f5;
  }

  .live-ops-header {
    margin: 0 0 12px;
    font-size: 20px;
    line-height: 28px;
    font-weight: 600;
    color: #1e66f5;
  }

  .event-stack {
    display: flex;
    flex-direction: column;
    gap: 16px;
    overflow: hidden;
  }

  .event-card {
    display: flex;
    align-items: center;
    gap: 16px;
    width: 100%;
    padding: 18px 20px;
    border-radius: 18px;
    background: #ffffff;
    border: 2px solid #c9ced6;
    box-shadow: none;
    box-sizing: border-box;
  }

  .event-card.empty-card {
    justify-content: center;
    font-weight: 500;
    color: rgba(71, 85, 105, 0.75);
  }

  .placeholder-card {
    opacity: 0.65;
  }

  .event-icon {
    width: 48px;
    height: 48px;
    border-radius: 50%;
    background: linear-gradient(180deg, #e8ebef 0%, #dadde2 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: none;
  }

  .event-icon.muted {
    background: #e6e9ee;
  }

  .event-icon svg {
    width: 18px;
    height: 18px;
    opacity: 1;
  }

  .event-copy {
    display: flex;
    flex-direction: column;
    gap: 2px;
  }

  .event-copy strong {
    font-size: 20px;
    line-height: 24px;
    font-weight: 700;
    color: #111827;
  }

  .event-copy span {
    font-size: 14px;
    line-height: 20px;
    color: #4b5563;
  }

  .legend {
    display: flex;
    align-items: center;
    gap: 26px;
    padding: 16px 24px;
    border-radius: 18px;
    background: #f6f7fb;
    border: 1.2px solid #d7dce6;
    font-size: 15px;
  }

  .legend-item {
    display: flex;
    align-items: center;
    gap: 10px;
    font-weight: 500;
    color: rgba(30, 41, 59, 0.86);
  }

  .legend-item .dot {
    width: 16px;
    height: 16px;
    border-radius: 999px;
  }

  .legend-item.full .dot {
    background: #075a45;
  }

  .legend-item.partial .dot {
    background: #9aa2b3;
  }

  .legend-item.empty .dot {
    background: #d93025;
  }

  .right-column {
    display: flex;
    justify-content: flex-end;
  }

  .storage-frame {
    position: relative;
    border: none;
    border-radius: 18px;
    padding: 16px 18px;
    background: #ffffff;
    box-shadow: 0 20px 40px rgba(15, 23, 42, 0.1);
    max-width: 420px;
    width: 100%;
  }

  .storage-image {
    width: 100%;
    display: block;
    border-radius: 12px;
  }

  .overlay-grid {
    position: absolute;
    inset: 16px 18px;
    pointer-events: none;
  }

  .overlay-cell {
    position: absolute;
    display: flex;
    align-items: center;
    justify-content: center;
    transform: translate(-50%, -50%);
    color: rgba(255, 255, 255, 0.92);
    font-weight: 600;
    font-size: 18px;
    text-shadow: 0 2px 3px rgba(15, 23, 42, 0.55);
    letter-spacing: 0.01em;
  }

  .overlay-cell.partial {
    color: rgba(36, 50, 68, 0.9);
    text-shadow: 0 1px 2px rgba(255, 255, 255, 0.45);
  }

  .overlay-cell .number {
    position: relative;
    z-index: 1;
  }

  .overlay-cell.alert::before {
    content: "";
    position: absolute;
    inset: 0;
    border: 3px solid #ff3b30;
    border-radius: 14px;
    box-shadow: 0 0 0 2px rgba(255, 59, 48, 0.2);
  }

  .overlay-cell.alert::after {
    content: "";
    position: absolute;
    inset: 2px;
    border-radius: 12px;
    background: linear-gradient(180deg, rgba(255, 71, 58, 0.92), rgba(194, 30, 27, 0.9));
    opacity: 0.85;
  }

  .overlay-cell.alert .number {
    position: relative;
    z-index: 2;
  }

  .alert-badge {
    position: absolute;
    top: -12px;
    right: -12px;
    width: 26px;
    height: 26px;
    border-radius: 10px;
    background: #ff3b30;
    color: #ffffff;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 10px 22px rgba(255, 59, 48, 0.45);
    z-index: 3;
  }

  .alert-badge svg {
    width: 14px;
    height: 14px;
  }

  .alerts {
    display: flex;
    flex-direction: column;
    gap: 14px;
  }

  .alert-banner {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 18px 28px;
    border-radius: 18px;
    border: 1.4px solid rgba(148, 163, 184, 0.28);
    box-shadow: 0 14px 32px rgba(15, 23, 42, 0.09);
    font-size: 15px;
  }

  .alert-banner.critical {
    background: #f6d4cf;
    color: #7b231d;
  }

  .alert-banner.caution {
    background: #f7ebba;
    color: #775203;
  }

  .alert-copy {
    display: flex;
    align-items: center;
    gap: 14px;
    font-weight: 600;
  }

  .alert-copy span[aria-hidden="true"] {
    font-size: 18px;
  }

  .alert-copy p {
    margin: 0;
    line-height: 1.35;
  }

  .alert-time {
    font-weight: 600;
    font-size: 15px;
  }

  .skeleton.layout {
    height: 440px;
    border-radius: 20px;
    background: linear-gradient(90deg, rgba(226, 232, 240, 0.7), rgba(203, 213, 225, 0.9), rgba(226, 232, 240, 0.7));
    background-size: 200% 100%;
    animation: shimmer 1.5s ease-in-out infinite;
  }

  @keyframes shimmer {
    0% {
      background-position: 200% 0;
    }
    100% {
      background-position: -200% 0;
    }
  }

  @media (max-width: 1180px) {
    .layout {
      grid-template-columns: minmax(0, 1fr);
    }

    .right-column {
      justify-content: center;
    }
  }

  @media (max-width: 768px) {
    .inventory-page {
      padding: 20px;
      gap: 28px;
    }

    .legend {
      flex-direction: column;
      align-items: flex-start;
    }
  }
</style>

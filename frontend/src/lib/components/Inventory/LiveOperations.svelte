<script>
  import { inventoryStore } from "../../stores/inventory.js";

  const MAX_VISIBLE = 5;
  const rtf =
    typeof Intl !== "undefined"
      ? new Intl.RelativeTimeFormat([], { numeric: "auto" })
      : undefined;

  $: events = ($inventoryStore.liveEvents ?? []).slice(0, MAX_VISIBLE);

  function formatRelativeTime(timestamp) {
    if (!timestamp) return "";
    try {
      const diffMs = new Date(timestamp).getTime() - Date.now();
      const diffMinutes = Math.round(diffMs / 60000);
      if (Math.abs(diffMinutes) < 1) {
        return "just now";
      }
      if (Math.abs(diffMinutes) < 60) {
        return rtf ? rtf.format(diffMinutes, "minute") : `${diffMinutes}m`;
      }
      const diffHours = Math.round(diffMinutes / 60);
      if (Math.abs(diffHours) < 24) {
        return rtf ? rtf.format(diffHours, "hour") : `${diffHours}h`;
      }
      const diffDays = Math.round(diffHours / 24);
      return rtf ? rtf.format(diffDays, "day") : `${diffDays}d`;
    } catch {
      return "";
    }
  }
</script>

<section class="live-operations" aria-label="Live inventory operations">
  <header>
    <h2>Live Operations</h2>
  </header>

  {#if events.length === 0}
    <p class="empty">No live operations yet.</p>
  {:else}
    <ul>
      {#each events as event (event.id)}
        <li>
          <div class="details">
            <span class="type {event.type}">{event.type}</span>
            <p>{event.message}</p>
          </div>
          <span class="time" aria-label={`Occurred ${formatRelativeTime(event.at)}`}>
            {formatRelativeTime(event.at)}
          </span>
        </li>
      {/each}
    </ul>
  {/if}
</section>

<style>
  .live-operations {
    display: flex;
    flex-direction: column;
    gap: 12px;
    padding: 16px;
    border-radius: 16px;
    border: 1px solid rgba(0, 0, 0, 0.08);
    background: #fff;
    min-height: 220px;
  }

  header h2 {
    margin: 0;
    font-size: 1.1rem;
    font-weight: 600;
    color: rgba(0, 0, 0, 0.87);
  }

  ul {
    list-style: none;
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  li {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 12px;
  }

  .details {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .details p {
    margin: 0;
    color: rgba(0, 0, 0, 0.8);
    font-weight: 500;
  }

  .type {
    text-transform: uppercase;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    padding: 2px 6px;
    border-radius: 6px;
    align-self: flex-start;
  }

  .type.retrieve {
    background: rgba(0, 82, 204, 0.12);
    color: #0052cc;
  }

  .type.store {
    background: rgba(0, 184, 148, 0.16);
    color: #067a58;
  }

  .type.reject,
  .type.alert {
    background: rgba(204, 0, 0, 0.12);
    color: #b00020;
  }

  .time {
    font-size: 0.8rem;
    color: rgba(0, 0, 0, 0.45);
    min-width: 72px;
    text-align: right;
  }

  .empty {
    margin: 0;
    color: rgba(0, 0, 0, 0.5);
    font-style: italic;
  }
</style>

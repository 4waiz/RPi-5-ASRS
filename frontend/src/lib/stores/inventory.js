import { derived, writable } from "svelte/store";

export const BOX_STATUSES = ["full", "partial", "empty"];
const MAX_LIVE_EVENTS = 10;

/**
 * @typedef {Object} InventoryBox
 * @property {number} id
 * @property {string|null} sku
 * @property {number} qty
 * @property {number} capacity
 * @property {"full"|"partial"|"empty"} status
 * @property {number} reservedQty
 * @property {string} lastOpAt
 * @property {boolean} hasAlert
 */

/**
 * @typedef {Object} LiveEvent
 * @property {string} id
 * @property {"retrieve"|"store"|"reject"|"alert"} type
 * @property {number} boxId
 * @property {string} message
 * @property {string} at
 * @property {Partial<InventoryBox>=} box
 */

const DEFAULT_STATE = {
  status: "idle",
  error: null,
  updatedAt: null,
  items: [],
  liveEvents: [],
  filter: {
    query: "",
    status: "all",
    sort: "box-asc",
  },
  selectedBoxId: null,
};

const inventoryWritable = writable(DEFAULT_STATE);

export const inventoryStore = {
  subscribe: inventoryWritable.subscribe,
};

export function setStatus(status, error = null) {
  inventoryWritable.update((state) => ({
    ...state,
    status,
    error,
  }));
}

export function setItems(items, updatedAt = new Date().toISOString()) {
  inventoryWritable.update((state) => ({
    ...state,
    items: Array.isArray(items) ? items : [],
    updatedAt,
    status: state.status === "idle" ? "ready" : state.status,
  }));
}

export function setFilter(nextFilter) {
  inventoryWritable.update((state) => ({
    ...state,
    filter: {
      ...state.filter,
      ...nextFilter,
    },
  }));
}

export function selectBox(boxId) {
  inventoryWritable.update((state) => ({
    ...state,
    selectedBoxId: boxId,
  }));
}

export function clearSelection() {
  inventoryWritable.update((state) => ({
    ...state,
    selectedBoxId: null,
  }));
}

export function applyEvent(event) {
  if (!event || !event.boxId) {
    console.warn("[inventoryStore] Invalid event", event);
    return;
  }

  inventoryWritable.update((state) => {
    const { boxId } = event;
    const nextEvents = [{ ...event }, ...state.liveEvents].slice(0, MAX_LIVE_EVENTS);

    const nextItems = state.items.map((item) => {
      if (item.id !== boxId) return item;

      const changes = event.box ?? event.item ?? event.payload ?? {};
      const merged = {
        ...item,
        ...changes,
        status: normalizeStatus(changes.status ?? item.status),
        qty: typeof changes.qty === "number" ? changes.qty : item.qty,
        reservedQty:
          typeof changes.reservedQty === "number" ? changes.reservedQty : item.reservedQty,
        hasAlert: typeof changes.hasAlert === "boolean" ? changes.hasAlert : item.hasAlert,
        lastOpAt: event.at ?? changes.lastOpAt ?? item.lastOpAt,
      };

      return merged;
    });

    return {
      ...state,
      items: nextItems,
      liveEvents: nextEvents,
      updatedAt: event.at ?? state.updatedAt,
      status: state.status === "idle" ? "ready" : state.status,
    };
  });
}

export function setUpdatedAt(timestamp) {
  inventoryWritable.update((state) => ({
    ...state,
    updatedAt: timestamp ?? new Date().toISOString(),
  }));
}

export const kpiCounts = derived(inventoryWritable, ($state) => {
  const counts = { full: 0, partial: 0, empty: 0 };
  $state.items.forEach((item) => {
    const status = normalizeStatus(item.status);
    if (counts[status] !== undefined) {
      counts[status] += 1;
    }
  });
  return counts;
});

export const filteredItems = derived(inventoryWritable, ($state) => {
  const query = $state.filter.query.trim().toLowerCase();
  const statusFilter = $state.filter.status;
  const sortToken = $state.filter.sort ?? "box-asc";

  const filtered = $state.items.filter((item) => {
    const matchesStatus = statusFilter === "all" || normalizeStatus(item.status) === statusFilter;
    if (!matchesStatus) return false;

    if (!query) return true;

    const text = `${item.sku ?? ""} ${item.id}`.toLowerCase();
    return text.includes(query);
  });

  return sortItems(filtered, sortToken);
});

function normalizeStatus(status) {
  const normalized = String(status ?? "").toLowerCase();
  return BOX_STATUSES.includes(normalized) ? normalized : "empty";
}

function sortItems(items, token) {
  const [field, direction] = token.split("-");
  const factor = direction === "desc" ? -1 : 1;

  return [...items].sort((a, b) => {
    if (field === "qty") {
      return (a.qty - b.qty) * factor;
    }
    return (a.id - b.id) * factor;
  });
}

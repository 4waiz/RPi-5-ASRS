import { applyEvent, setItems, setStatus, setUpdatedAt } from "../stores/inventory.js";
import { subscribeToEvents } from "../realtime.js";

const INVENTORY_ENDPOINT = "/api/inventory";
const EVENTS_ENDPOINT = "/events/asrs";
const BOX_CAPACITY = 120;
const BOX_COUNT = 20;
const MOCK_EVENT_MIN_DELAY = 10000;
const MOCK_EVENT_MAX_DELAY = 20000;

let isMockMode = false;
let mockTimerId;

export async function loadInventory() {
  try {
    const response = await fetch(INVENTORY_ENDPOINT, { headers: { Accept: "application/json" } });
    if (!response.ok) {
      throw new Error(`Inventory request failed (${response.status})`);
    }

    const data = await response.json();
    const items = normalizeItems(data);

    setItems(items);
    setStatus("ready", null);
    setUpdatedAt(new Date().toISOString());
    stopMockStream();
    isMockMode = false;
    return { ok: true, source: "api" };
  } catch (error) {
    console.warn("[inventoryService] Falling back to mock data", error);
    const mockItems = createMockInventory();
    setItems(mockItems);
    setStatus("error", error?.message ?? "Unable to reach ASRS API. Showing mock data.");
    setUpdatedAt(new Date().toISOString());
    isMockMode = true;
    startMockStream();
    return { ok: false, source: "mock", error };
  }
}

export function subscribeRealtime() {
  if (typeof window === "undefined") {
    return () => {};
  }

  if (isMockMode) {
    startMockStream();
    return () => stopMockStream();
  }

  const unsubscribe = subscribeToEvents(EVENTS_ENDPOINT, (rawEvent) => {
    if (!rawEvent) return;
    const event = normalizeEvent(rawEvent);
    applyEvent(event);
  });

  return () => {
    unsubscribe?.();
  };
}

function normalizeItems(payload) {
  if (!payload) return [];

  const items = Array.isArray(payload) ? payload : payload.items ?? [];

  return items.map((item, index) => ({
    id: typeof item.id === "number" ? item.id : index + 1,
    sku: item.sku ?? null,
    qty: item.qty ?? 0,
    capacity: item.capacity ?? BOX_CAPACITY,
    status: (item.status ?? "empty").toLowerCase(),
    reservedQty: item.reservedQty ?? 0,
    lastOpAt: item.lastOpAt ?? new Date().toISOString(),
    hasAlert: Boolean(item.hasAlert),
  }));
}

function normalizeEvent(event) {
  const at = event.at ?? new Date().toISOString();
  const boxId = Number(event.boxId ?? event.id ?? 0);

  return {
    id: event.id ?? cryptoRandomId(),
    type: event.type ?? "store",
    boxId,
    message: event.message ?? `Box ${boxId} update`,
    at,
    box: normalizeBoxPatch(event.box ?? event.item ?? event.payload),
  };
}

function normalizeBoxPatch(patch) {
  if (!patch) return undefined;
  const output = {};
  if ("sku" in patch) output.sku = patch.sku;
  if ("qty" in patch) output.qty = patch.qty;
  if ("capacity" in patch) output.capacity = patch.capacity;
  if ("status" in patch) output.status = patch.status;
  if ("reservedQty" in patch) output.reservedQty = patch.reservedQty;
  if ("hasAlert" in patch) output.hasAlert = patch.hasAlert;
  if ("lastOpAt" in patch) output.lastOpAt = patch.lastOpAt;
  return output;
}

function cryptoRandomId() {
  if (typeof crypto?.randomUUID === "function") {
    return crypto.randomUUID();
  }
  return `evt-${Math.random().toString(36).slice(2, 11)}`;
}

function createMockInventory() {
  const now = Date.now();
  const items = [];
  for (let i = 1; i <= BOX_COUNT; i += 1) {
    const modulo = i % 3;
    const status = modulo === 1 ? "full" : modulo === 2 ? "partial" : "empty";
    const capacity = BOX_CAPACITY;
    const qty = status === "full" ? capacity : status === "partial" ? Math.floor(capacity * 0.4) : 0;
    items.push({
      id: i,
      sku: status === "empty" ? null : `SKU-${String(200 + i).padStart(3, "0")}`,
      qty,
      capacity,
      status,
      reservedQty: status === "partial" ? Math.floor(capacity * 0.1) : 0,
      lastOpAt: new Date(now - i * 3600 * 1000).toISOString(),
      hasAlert: status === "empty",
    });
  }
  return items;
}

function startMockStream() {
  if (typeof window === "undefined") return;
  if (mockTimerId) return;

  const schedule = () => {
    const delay =
      MOCK_EVENT_MIN_DELAY + Math.random() * (MOCK_EVENT_MAX_DELAY - MOCK_EVENT_MIN_DELAY);
    mockTimerId = window.setTimeout(() => {
      mockTimerId = null;
      const event = createMockEvent();
      applyEvent(event);
      schedule();
    }, delay);
  };

  schedule();
}

function stopMockStream() {
  if (mockTimerId) {
    clearTimeout(mockTimerId);
    mockTimerId = null;
  }
}

function createMockEvent() {
  const boxId = 1 + Math.floor(Math.random() * BOX_COUNT);
  const timestamp = new Date().toISOString();
  const typeRoll = Math.random();
  let type = "store";
  if (typeRoll > 0.7) type = "retrieve";
  if (typeRoll > 0.9) type = "reject";
  if (typeRoll < 0.1) type = "alert";

  const delta = Math.floor(Math.random() * 10);
  const status = type === "retrieve" ? "empty" : type === "reject" ? "partial" : "full";
  const qty = status === "full" ? BOX_CAPACITY : status === "partial" ? BOX_CAPACITY - delta * 2 : 0;

  return {
    id: cryptoRandomId(),
    type,
    boxId,
    message: `Box ${boxId} ${type === "store" ? "stored" : type === "retrieve" ? "retrieved" : type}`,
    at: timestamp,
    box: {
      qty,
      status,
      lastOpAt: timestamp,
      hasAlert: type === "alert" || qty === 0,
    },
  };
}

import { writable } from "svelte/store";
import { units } from "../catalog.js";

const DEFAULT_STATUS = "Unknown";

const defaultMap = units.reduce((acc, unit) => {
  unit.subcomponents.forEach((component) => {
    acc[component.id] = component.defaultStatus ?? DEFAULT_STATUS;
  });
  return acc;
}, {});

const createState = (overrides = {}) => ({
  statuses: { ...defaultMap },
  online: false,
  lastUpdatedAt: null,
  ...overrides,
});

const { subscribe, set, update } = writable(createState());

export const statusStore = { subscribe };

export function resetStatuses() {
  set(createState());
}

export function applySnapshot(snapshot) {
  if (!snapshot) {
    console.warn("[statusStore] Ignored empty snapshot");
    return;
  }

  const next = { ...defaultMap };
  const array = Array.isArray(snapshot)
    ? snapshot
    : typeof snapshot === "object"
    ? Object.values(snapshot)
    : [];

  array.forEach((unit) => {
    unit?.subcomponents?.forEach((component) => {
      if (!component?.id) return;
      next[component.id] = component.status ?? next[component.id] ?? DEFAULT_STATUS;
    });
  });

  set(
    createState({
      statuses: next,
      online: true,
      lastUpdatedAt: new Date().toISOString(),
    }),
  );
}

export function applyUpdate(payload) {
  const { componentId, status } = payload ?? {};
  if (!componentId) {
    console.warn("[statusStore] Ignored update missing componentId", payload);
    return;
  }

  update((state) => ({
    ...state,
    online: true,
    lastUpdatedAt: new Date().toISOString(),
    statuses: {
      ...state.statuses,
      [componentId]: status ?? DEFAULT_STATUS,
    },
  }));
}

export function getStatus(state, componentId, fallback = DEFAULT_STATUS) {
  const map = state?.statuses ?? defaultMap;
  if (state?.online !== true) {
    return DEFAULT_STATUS;
  }
  return map[componentId] ?? fallback;
}

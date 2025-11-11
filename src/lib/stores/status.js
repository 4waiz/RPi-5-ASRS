import { writable } from "svelte/store";

const STATUS_SEQUENCE = ["Running", "Live", "Online", "Idle", "Off"];

const DEFAULT_STATUSES = {
  SM1: "Running",
  SM2: "Running",
  SM3: "Off",
  PS1: "Live",
  PS2: "Live",
  PS3: "Live",
  PS4: "Idle",
  JO1: "Online",
  GD1: "Idle",
};

const INITIAL_STATE = {
  online: true,
  lastUpdated: new Date().toISOString(),
  statuses: DEFAULT_STATUSES,
};

const clone = (value) => JSON.parse(JSON.stringify(value));

const createStatusStore = () => {
  const store = writable(clone(INITIAL_STATE));

  if (typeof window !== "undefined") {
    const interval = setInterval(() => {
      store.update((state) => {
        const nextStatuses = Object.fromEntries(
          Object.entries(state.statuses).map(([id, status]) => [
            id,
            getNextStatus(status),
          ])
        );

        return {
          ...state,
          lastUpdated: new Date().toISOString(),
          statuses: nextStatuses,
        };
      });
    }, 3000);

    const unsubscribe = store.subscribe(() => {});

    if (import.meta?.hot) {
      import.meta.hot.dispose(() => {
        clearInterval(interval);
        unsubscribe();
      });
    }
  }

  return {
    subscribe: store.subscribe,
    setOnline(value) {
      store.update((state) => ({
        ...state,
        online: value ?? !state.online,
      }));
    },
    setStatus(id, status) {
      store.update((state) => ({
        ...state,
        statuses: {
          ...state.statuses,
          [id]: status,
        },
      }));
    },
    reset() {
      store.set(clone(INITIAL_STATE));
    },
  };
};

const getNextStatus = (current) => {
  const index = STATUS_SEQUENCE.indexOf(current);
  if (index === -1) {
    return STATUS_SEQUENCE[0];
  }
  return STATUS_SEQUENCE[(index + 1) % STATUS_SEQUENCE.length];
};

export const statusStore = createStatusStore();

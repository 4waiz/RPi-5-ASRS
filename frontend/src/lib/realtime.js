import { applySnapshot, applyUpdate, resetStatuses } from "./stores/status.js";

const WS_URL = "ws://localhost:8000/ws/status";
const BASE_DELAY_MS = 200;
const BACKOFF_FACTOR = 1.5;
const MAX_DELAY_MS = 2000;

let socket;
let reconnectTimer;
let reconnectDelay = BASE_DELAY_MS;
let hasConnected = false;
let onConnectCallback;
let onReconnectCallback;

const clearReconnectTimer = () => {
  if (reconnectTimer) {
    clearTimeout(reconnectTimer);
    reconnectTimer = undefined;
  }
};

const scheduleReconnect = () => {
  if (typeof window === "undefined" || reconnectTimer) return;

  reconnectTimer = setTimeout(() => {
    reconnectTimer = undefined;
    reconnectDelay = Math.min(reconnectDelay * BACKOFF_FACTOR, MAX_DELAY_MS);
    connectRealtime({ onConnect: onConnectCallback, onReconnect: onReconnectCallback });
  }, reconnectDelay);

  console.warn(`[ws] reconnect in ${reconnectDelay}ms`);
};

const handleMessage = (event) => {
  console.log("[ws] message received:", event.data);
  try {
    const message = JSON.parse(event.data);
    if (message?.type === "snapshot") {
      const payload = message.payload?.units ?? message.payload ?? [];
      applySnapshot(payload);
    } else if (message?.type === "update") {
      applyUpdate(message.payload);
    } else {
      console.warn("[ws] unknown message type", message);
    }
  } catch (error) {
    console.error("[ws] failed to parse message", error);
  }
};

export function connectRealtime({ onConnect, onReconnect } = {}) {
  if (typeof window === "undefined") return;

  onConnectCallback = onConnect;
  onReconnectCallback = onReconnect;
  disconnectRealtime();

  console.log("[ws] connecting to", WS_URL);
  socket = new WebSocket(WS_URL);

  socket.addEventListener("open", () => {
    const initialConnect = !hasConnected;
    console.log(`[ws] ${initialConnect ? "connected" : "reconnected"}`);
    clearReconnectTimer();
    reconnectDelay = BASE_DELAY_MS;

    if (initialConnect) {
      onConnectCallback?.();
      hasConnected = true;
    } else {
      onReconnectCallback?.();
    }
  });

  socket.addEventListener("message", handleMessage);

  socket.addEventListener("close", (event) => {
    console.warn("[ws] closed", event.code, event.reason);
    resetStatuses();
    scheduleReconnect();
  });

  socket.addEventListener("error", (error) => {
    console.error("[ws] error", error);
    resetStatuses();
    socket?.close?.();
  });
}

export function disconnectRealtime() {
  clearReconnectTimer();
  if (socket) {
    console.log("[ws] disconnecting");
    socket.removeEventListener("message", handleMessage);
    socket.close();
    socket = undefined;
  }
}

export function subscribeToEvents(path, onMessage) {
  if (typeof window === "undefined") {
    return () => {};
  }

  const url = createAbsoluteUrl(path);
  let source;

  const safeHandler = (event) => {
    try {
      const parsed = event?.data ? JSON.parse(event.data) : null;
      onMessage?.(parsed);
    } catch (error) {
      console.error("[events] failed to parse event", error, event?.data);
    }
  };

  try {
    source = new EventSource(url, { withCredentials: true });
    source.addEventListener("message", safeHandler);
  } catch (error) {
    console.error("[events] EventSource not available", error);
    return () => {};
  }

  source.addEventListener("error", (error) => {
    console.warn("[events] stream error", error);
  });

  return () => {
    source?.removeEventListener?.("message", safeHandler);
    source?.close?.();
  };
}

function createAbsoluteUrl(path) {
  if (!path) return window.location.origin;
  if (path.startsWith("http://") || path.startsWith("https://")) {
    return path;
  }
  return `${window.location.origin}${path.startsWith("/") ? "" : "/"}${path}`;
}

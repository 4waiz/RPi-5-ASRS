<script>
  import { onDestroy, onMount } from "svelte";
  import SideBar from "./lib/side-bar.svelte";
  import TopBar from "./lib/top-bar.svelte";
  import DigitalTwinTabPage from "./lib/Home-tab-pages/DigitalTwin-tab-page.svelte";
  import InverntoryTabPage from "./lib/Home-tab-pages/inverntory-tab-page.svelte";
  import CompunentsOverviewTab from "./components/Home-tab-pages/compunents-overview-tab.svelte";
  import OverviewTabPage from "./lib/Home-tab-pages/overview-tab-page.svelte";
  import { applySnapshot, resetStatuses } from "./lib/stores/status.js";
  import { connectRealtime, disconnectRealtime } from "./lib/realtime.js";

  const API_BASE_URL = import.meta.env.VITE_STATUS_API ?? "http://localhost:8000";
  const HTTP_STATUS_URL = `${API_BASE_URL}/api/status`;

  const Alerts = [2, 5];
  const Names = ["Overview", "Inventory", "Digital Twin", "Components"];
  const Pages = [
    OverviewTabPage,
    InverntoryTabPage,
    DigitalTwinTabPage,
    CompunentsOverviewTab,
  ];

  const fetchLatestUnits = async (reason = "initial") => {
    try {
      const response = await fetch(HTTP_STATUS_URL);
      console.log(`[data] GET /api/status (${reason}) ->`, response.status);
      const payload = await response.json();
      applySnapshot(payload?.units ?? payload ?? []);
    } catch (error) {
      console.error(`[data] Failed to load device status (${reason})`, error);
      resetStatuses();
    }
  };

  onMount(() => {
    resetStatuses();
    fetchLatestUnits("initial");
    connectRealtime({
      onConnect: () => fetchLatestUnits("connect"),
      onReconnect: () => fetchLatestUnits("reconnect"),
    });
  });

  onDestroy(() => {
    disconnectRealtime();
  });
</script>

<div class="main">
  <SideBar WoriginNum={Alerts[1]} AlertsNum={Alerts[0]} />

  <section class="right-con">
    <TopBar {Names} {Pages} />

    <div class="alert-section"></div>
  </section>
</div>

<style>
  .main {
    width: 100%;
    height: 100vh;
    background-color: #ebebeb;
    display: inline-flex;
    align-items: self-start;
    gap: 32px;
  }

  .right-con {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    height: 100%;
    width: 100%;
    margin-right: 16px;
  }

  .alert-section {
    height: 120px;
    width: 100%;
    margin: 24px 0px;

    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    align-items: flex-start;
    gap: 8px;
  }
</style>

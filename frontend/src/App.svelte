<script>
  import {
    currentPage,
    isModePopupOpen,
    isPassWordPopupOpen,
  } from "./stores/AppStore.js";
  import Home from "./pages/Home.svelte";
  import Settings from "./pages/Setting.svelte";
  import Alerts from "./pages/Alerts.svelte";
  import AIAssistant from "./pages/AIAssistant.svelte";
  import Analytics from "./pages/Analytics.svelte";
  import ModePopup from "./components/shared/mode_popup.svelte";
  import PasswordPopup from "./components/shared/password_popup.svelte";

  const pages = {
    Home: Home,
    Settings: Settings,
    Alerts: Alerts,
    AIAssistant: AIAssistant,
    Analytics: Analytics,
  };

  $: component = pages[$currentPage] || Home;

  function closeModePopup() {
    isModePopupOpen.set(false);
  }

  function closePasswordPopup() {
    isPassWordPopupOpen.set(false);
  }
</script>

<div class="main">
  <ModePopup open={$isModePopupOpen} onClose={closeModePopup} />
  <PasswordPopup open={$isPassWordPopupOpen} onClose={closePasswordPopup} changeMode={$currentPage !== 'Settings'} />
  <svelte:component this={component} />
</div>

<style>
  .main {
    width: 100%;
    height: 100vh;
  }
</style>

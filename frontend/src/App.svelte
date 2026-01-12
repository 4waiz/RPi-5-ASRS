<script>
  import { onMount, onDestroy } from "svelte";
  import {
    currentPage,
    isModePopupOpen,
    isPassWordPopupOpen,
    isHandDetectionPopupOpen,
  } from "./stores/AppStore.js";
  import Home from "./pages/Home.svelte";
  import Settings from "./pages/Setting.svelte";
  import Alerts from "./pages/Alerts.svelte";
  import AIAssistant from "./pages/AIAssistant.svelte";
  import Analytics from "./pages/Analytics.svelte";
  import QC from "./pages/QC.svelte";
  import ModePopup from "./components/shared/mode_popup.svelte";
  import PasswordPopup from "./components/shared/password_popup.svelte";
  import HandDetectionPopup from "./components/shared/HandDetectionPopup.svelte";

  const pages = {
    Home: Home,
    Settings: Settings,
    Alerts: Alerts,
    AIAssistant: AIAssistant,
    Analytics: Analytics,
    QC: QC,
  };

  let component = $derived(pages[$currentPage] || Home);

  // Video WebSocket and frame management
  let videoWs;
  let handWs;
  let currentVideoFrame = $state("");
  let userDismissedVideo = $state(false);

  function connectVideoWebSocket() {
    videoWs = new WebSocket("ws://127.0.0.1:8013/ws/video");
    videoWs.binaryType = "blob";

    videoWs.onopen = () => {
      console.log("Video WebSocket connected");
    };

    videoWs.onmessage = (event) => {
      // Update latest frame; popup visibility is controlled by hand-detection events
      if (currentVideoFrame) URL.revokeObjectURL(currentVideoFrame);
      currentVideoFrame = URL.createObjectURL(event.data);
    };

    videoWs.onclose = () => {
      console.log("Video WebSocket closed, reconnecting...");
      setTimeout(connectVideoWebSocket, 2000);
    };

    videoWs.onerror = () => {
      console.log("Video WebSocket error");
      videoWs.close();
    };
  }

  function connectHandDetectionWebSocket() {
    handWs = new WebSocket("ws://127.0.0.1:8013/ws/hand-detection");

    handWs.onopen = () => {
      console.log("Hand detection WebSocket connected");
    };

    handWs.onmessage = (event) => {
      let payload;
      try {
        payload = JSON.parse(event.data);
      } catch {
        return;
      }

      if (payload?.event === "hand_detected") {
        // Don't show popup when on QC page
        if (!userDismissedVideo && $currentPage !== 'QC') {
          isHandDetectionPopupOpen.set(true);
        }
      }

      if (payload?.event === "hand_removed") {
        console.log("[TIMING] hand_removed event received at:", Date.now());

        // Close popup immediately
        isHandDetectionPopupOpen.set(false);
        userDismissedVideo = false;

        // Clear frame reference immediately
        const oldFrame = currentVideoFrame;
        currentVideoFrame = "";

        // Defer URL revocation to avoid blocking
        if (oldFrame) {
          setTimeout(() => URL.revokeObjectURL(oldFrame), 0);
        }

        console.log("[TIMING] Popup closed at:", Date.now());
      }
    };

    handWs.onclose = () => {
      console.log("Hand detection WebSocket closed, reconnecting...");
      setTimeout(connectHandDetectionWebSocket, 2000);
    };

    handWs.onerror = () => {
      console.log("Hand detection WebSocket error");
      handWs.close();
    };
  }

  onMount(() => {
    connectVideoWebSocket();
    connectHandDetectionWebSocket();
  });

  onDestroy(() => {
    if (videoWs) videoWs.close();
    if (handWs) handWs.close();
    if (currentVideoFrame) URL.revokeObjectURL(currentVideoFrame);
  });

  function closeModePopup() {
    isModePopupOpen.set(false);
  }

  function closePasswordPopup() {
    isPassWordPopupOpen.set(false);
  }

  function closeHandDetectionPopup() {
    isHandDetectionPopupOpen.set(false);
    userDismissedVideo = true;
    if (currentVideoFrame) {
      URL.revokeObjectURL(currentVideoFrame);
      currentVideoFrame = "";
    }
  }
</script>

<div class="main">
  <ModePopup open={$isModePopupOpen} onClose={closeModePopup} />
  <PasswordPopup open={$isPassWordPopupOpen} onClose={closePasswordPopup} changeMode={$currentPage !== 'Settings'} />
  <HandDetectionPopup open={$isHandDetectionPopupOpen} onClose={closeHandDetectionPopup} imageSrc={currentVideoFrame} />
  <svelte:component this={component} />
</div>

<style>
  .main {
    width: 100%;
    height: 100vh;
  }
</style>

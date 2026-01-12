<script>
  import { onMount, onDestroy } from "svelte";
  import Sidebar from "../components/shared/Sidebar.svelte";

  let qcVideoWs;
  let currentFrame = $state("");

  function connectQCVideoWebSocket() {
    qcVideoWs = new WebSocket("ws://127.0.0.1:8013/ws/qc-video");
    qcVideoWs.binaryType = "blob";

    qcVideoWs.onopen = () => {
      console.log("QC video WebSocket connected");
    };

    qcVideoWs.onmessage = (event) => {
      // Update latest frame
      if (currentFrame) URL.revokeObjectURL(currentFrame);
      currentFrame = URL.createObjectURL(event.data);
    };

    qcVideoWs.onclose = () => {
      console.log("QC video WebSocket closed, reconnecting...");
      setTimeout(connectQCVideoWebSocket, 2000);
    };

    qcVideoWs.onerror = () => {
      console.log("QC video WebSocket error");
      qcVideoWs.close();
    };
  }

  onMount(() => {
    connectQCVideoWebSocket();
  });

  onDestroy(() => {
    if (qcVideoWs) qcVideoWs.close();
    if (currentFrame) URL.revokeObjectURL(currentFrame);
  });
</script>

<div class="page">
  <Sidebar ActivePage="QC" />

  <main class="content">
    <div class="header">
      <div class="kicker">QC</div>
      <h1 class="title">Crack Detection</h1>
    </div>

    <div class="videoSpace">
      {#if currentFrame}
        <img src={currentFrame} alt="QC Crack Detection Live Feed" class="video-stream" />
      {:else}
        <div class="label">Waiting for video stream...</div>
      {/if}
    </div>
  </main>
</div>

<style>
  .page {
    display: flex;
    min-height: 100vh;
    background: #f6f7fb;
    color: #0f172a;
  }

  .content {
    flex: 1;
    padding: 22px;
  }

  .header {
    margin-bottom: 14px;
  }

  .kicker {
    font-size: 12px;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    opacity: 0.6;
    margin-bottom: 4px;
  }

  .title {
    margin: 0;
    font-size: 26px;
    font-weight: 800;
  }

  .videoSpace {
    width: 100%;
    max-width: 900px;
    border-radius: 14px;
    border: 1px solid rgba(15, 23, 42, 0.12);
    background: white;
    box-shadow: 0 8px 18px rgba(2, 6, 23, 0.06);
    padding: 20px;

    /* center label */
    display: grid;
    place-items: center;
  }

  .label {
    font-size: 13px;
    opacity: 0.6;
  }

  .video-stream {
    width: 100%;
    max-width: 100%;
    max-height: 430px;
    height: auto;
    object-fit: contain;
    border-radius: 8px;
  }
</style>
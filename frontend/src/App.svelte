<script>
  import { onMount } from 'svelte';
  import { myVariable } from './store.js';
  import Home from './pages/Home.svelte';
  import Setting from './pages/Setting.svelte';

  myVariable.set(Home);

  const RFID_API_BASE = (import.meta && import.meta.env && import.meta.env.VITE_RFID_API_BASE)
    ? import.meta.env.VITE_RFID_API_BASE
    : 'http://localhost:8003';
  const KEY_GAP_MS = 180;
  let rfidBuffer = '';
  let lastKeyTimestamp = 0;

  async function postRfid(tag) {
    if (!tag) return;
    try {
      await fetch(`${RFID_API_BASE}/api/rfid/scan`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tag, source: 'keyboard_wedge' })
      });
    } catch (err) {
      console.error('RFID post failed', err);
    }
  }

  function handleGlobalKeydown(event) {
    const now = Date.now();

    if (/^[0-9]$/.test(event.key)) {
      if (now - lastKeyTimestamp > KEY_GAP_MS) {
        rfidBuffer = '';
      }
      rfidBuffer += event.key;
      lastKeyTimestamp = now;
      return;
    }

    if (event.key === 'Enter' && rfidBuffer) {
      const value = rfidBuffer;
      rfidBuffer = '';
      postRfid(value);
    }
  }

  onMount(() => {
    window.addEventListener('keydown', handleGlobalKeydown, { passive: true });
    return () => window.removeEventListener('keydown', handleGlobalKeydown);
  });
</script>

<div class="main">
  <svelte:component this={$myVariable} />
</div>

<style>
  .main {
    width: 100%;
    height: 100vh;
  }
</style>

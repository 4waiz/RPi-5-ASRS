<script lang="ts">
  import { onMount } from "svelte";
  import SideBar from "../lib/side-bar.svelte";

  import arrowBackIcon     from "../assets/settingPage/arrow-1.svg";
  import languageIcon      from "../assets/settingPage/frame6.svg";
  import brightnessIcon    from "../assets/settingPage/frame3.svg";
  import networkIcon       from "../assets/settingPage/frame4.svg";
  import padlockIcon       from "../assets/settingPage/frame7.svg";
  import revealIcon        from "../assets/settingPage/frame1.svg";
  import logsPadlockIcon   from "../assets/settingPage/frame8.svg";
  import logsFilterIcon    from "../assets/settingPage/frame.svg";
  import exportIcon        from "../assets/settingPage/frame2.svg";
  import checkIcon         from "../assets/settingPage/check.svg";
  import viewIcon          from "../assets/settingPage/arrow-6.svg";
  import sliderThumb       from "../assets/settingPage/slider.svg";

  import { myVariable } from "../store";
  import Home from "./Home.svelte";

  let previousBodyOverflow = "";
  onMount(() => {
    if (typeof document === "undefined") return;
    previousBodyOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";

    return () => {
      document.body.style.overflow = previousBodyOverflow || "";
    };
  });

  // Prevent browser zoom
  $effect(() => {
    if (typeof window === "undefined") return;
    const wheel = (e: WheelEvent) => { if (e.ctrlKey || e.metaKey) e.preventDefault(); };
    const keyd  = (e: KeyboardEvent) => { if ((e.ctrlKey||e.metaKey) && ["+","-","=","_","0"].includes(e.key)) e.preventDefault(); };
    window.addEventListener("wheel", wheel, { passive: false });
    window.addEventListener("keydown", keyd);
    return () => {
      window.removeEventListener("wheel", wheel);
      window.removeEventListener("keydown", keyd);
    };
  });

  // Demo values
  const asrsId    = $state("ASRS-2025-001");
  const runtime   = $state("00:08:20");
  const timestamp = $state("11/03/2025, 06:38:08");

  let language   = $state<"en"|"ar">("en");
  let brightness = $state(60);
  let activeLogTab = $state<"all"|"error"|"operation">("all");

  // ===== Network IP (masked input with inline eye button) =====
  let ip1Value = $state("192.168.0.101");
  let ip2Value = $state("192.168.0.102");
  let ip1Masked = $state(true);
  let ip2Masked = $state(true);
  const maskIP = (s: string) => s.replace(/\d/g, "•");

  // ===== Backup logic (hold-to-activate) =====
  const HOLD_MS = 2000;
  let storeTimestamp = $state("--");
  let restoreTimestamp = $state("--");
  let storeTimer: ReturnType<typeof setInterval> | null = null;
  let restoreTimer: ReturnType<typeof setInterval> | null = null;
  let storeProgress = $state(0);
  let restoreProgress = $state(0);
  const nowString = () => new Date().toLocaleString();

  function startHold(kind: "store" | "restore") {
    cancelHold(kind);
    const t0 = Date.now();
    const tick = () => {
      const p = Math.min(1, (Date.now() - t0) / HOLD_MS);
      if (kind === "store") storeProgress = p; else restoreProgress = p;
      if (p >= 1) {
        cancelHold(kind);
        if (kind === "store") storeTimestamp = nowString();
        else restoreTimestamp = nowString();
      }
    };
    const id = setInterval(tick, 16);
    if (kind === "store") storeTimer = id; else restoreTimer = id;
  }
  function cancelHold(kind: "store" | "restore") {
    if (kind === "store") {
      if (storeTimer) clearInterval(storeTimer);
      storeTimer = null; storeProgress = 0;
    } else {
      if (restoreTimer) clearInterval(restoreTimer);
      restoreTimer = null; restoreProgress = 0;
    }
  }

  // Slider gradient + SVG thumb
  const sliderStyle = $derived(`
    background: linear-gradient(90deg,
      var(--brand) 0%,
      var(--brand) ${brightness}%,
      var(--track-rest) ${brightness}%,
      var(--track-rest) 100%);
    --slider-thumb: url("${sliderThumb}");
  `);
</script>

<svelte:head>
  <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link
    rel="stylesheet"
    href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"
  />
</svelte:head>

<div class="page">
  <!-- Header with better spacing from top -->
  <div class="topbar">
    <button class="iconbtn" aria-label="Back" onclick={() => myVariable.set(Home)}>
      <img class="icon" src={arrowBackIcon} alt="Back" width="24" height="24" />
    </button>

    <div class="titleblock">
      <h1 class="h1">System Setting</h1>
      <div class="meta">
        <span class="meta-label">ASRS ID:</span>&nbsp;{asrsId}&nbsp;&nbsp;·&nbsp;&nbsp;
        <span class="meta-label">Runtime:</span>&nbsp;{runtime}&nbsp;&nbsp;·&nbsp;&nbsp;
        <span class="meta-label">Timestamp:</span>&nbsp;{timestamp}
      </div>
    </div>
  </div>

  <div class="divider"></div>

  <!-- Main grid - optimized for 1024x600 -->
  <div class="content-grid">
    <!-- Language -->
    <section class="card card-language">
      <div class="card-header">
        <img class="icon" src={languageIcon} alt="Language" width="20" height="20" />
        <h2 class="card-title">Language</h2>
      </div>

      <div class="card-content">
        <div class="lang-toggle">
          <button 
            type="button" 
            class="lang-btn {language==='en' ? 'active' : ''}" 
            aria-pressed={language==='en'} 
            onclick={() => (language = 'en')}
          >
            {#if language==='en'}
              <span class="check-dot"><img src={checkIcon} alt="" width="10" height="10" /></span>
            {/if}
            English
          </button>

          <button 
            type="button" 
            class="lang-btn {language==='ar' ? 'active' : ''}" 
            aria-pressed={language==='ar'} 
            onclick={() => (language = 'ar')}
          >
            {#if language==='ar'}
              <span class="check-dot"><img src={checkIcon} alt="" width="10" height="10" /></span>
            {/if}
            عربي / Arabic
          </button>
        </div>
      </div>
    </section>

    <!-- Brightness -->
    <section class="card card-brightness">
      <div class="card-header">
        <img class="icon" src={brightnessIcon} alt="Brightness" width="20" height="20" />
        <h2 class="card-title">Display Brightness</h2>
      </div>

      <div class="card-content">
        <div class="slider-container">
          <input
            class="slider"
            type="range"
            min="0"
            max="100"
            bind:value={brightness}
            style={sliderStyle}
            aria-label="Brightness"
          />
        </div>
      </div>
    </section>

    <!-- Network -->
    <section class="card card-network">
      <div class="card-header">
        <img class="icon" src={networkIcon} alt="Network" width="20" height="20" />
        <h2 class="card-title">Network Configuration</h2>
        <img class="icon lock-icon" src={padlockIcon} alt="Locked" width="18" height="18" />
      </div>

      <div class="card-content">
        <div class="section-label">Machine IPs:</div>

        <div class="ip-wrapper">
          <input
            class="ip-input"
            value={ip1Masked ? maskIP(ip1Value) : ip1Value}
            readonly
            aria-label="Machine IP 1"
          />
          <button
            class="reveal-btn"
            type="button"
            aria-label={ip1Masked ? "Show IP 1" : "Hide IP 1"}
            onclick={() => (ip1Masked = !ip1Masked)}
          >
            <svg class="eye-icon" viewBox="0 0 24 24" width="18" height="18">
              <path d="M12 5C7 5 2.73 8.11 1 12.5 2.73 16.89 7 20 12 20s9.27-3.11 11-7.5C21.27 8.11 17 5 12 5z" 
                    fill="none" 
                    stroke="currentColor" 
                    stroke-width="2"/>
              <circle cx="12" cy="12.5" r="3.5" 
                      fill="none" 
                      stroke="currentColor" 
                      stroke-width="2"/>
              {#if ip1Masked}
                <line x1="4" y1="4" x2="20" y2="21" 
                      stroke="currentColor" 
                      stroke-width="2" 
                      stroke-linecap="round"/>
              {/if}
            </svg>
          </button>
        </div>

        <div class="ip-wrapper">
          <input
            class="ip-input"
            value={ip2Masked ? maskIP(ip2Value) : ip2Value}
            readonly
            aria-label="Machine IP 2"
          />
          <button
            class="reveal-btn"
            type="button"
            aria-label={ip2Masked ? "Show IP 2" : "Hide IP 2"}
            onclick={() => (ip2Masked = !ip2Masked)}
          >
            <svg class="eye-icon" viewBox="0 0 24 24" width="18" height="18">
              <path d="M12 5C7 5 2.73 8.11 1 12.5 2.73 16.89 7 20 12 20s9.27-3.11 11-7.5C21.27 8.11 17 5 12 5z" 
                    fill="none" 
                    stroke="currentColor" 
                    stroke-width="2"/>
              <circle cx="12" cy="12.5" r="3.5" 
                      fill="none" 
                      stroke="currentColor" 
                      stroke-width="2"/>
              {#if ip2Masked}
                <line x1="4" y1="4" x2="20" y2="21" 
                      stroke="currentColor" 
                      stroke-width="2" 
                      stroke-linecap="round"/>
              {/if}
            </svg>
          </button>
        </div>
      </div>
    </section>

    <!-- Logs -->
    <section class="card card-logs">
      <div class="card-header">
        <img class="icon" src={logsPadlockIcon} alt="Locked" width="20" height="20" />
        <h2 class="card-title">Machine Logs</h2>
        <img class="icon lock-icon" src={logsFilterIcon} alt="Filter" width="18" height="18" />
      </div>

      <div class="card-content">
        <div class="log-tabs">
          <button 
            type="button" 
            class="log-tab {activeLogTab==='all' ? 'active' : ''}" 
            aria-pressed={activeLogTab==='all'} 
            onclick={() => (activeLogTab='all')}
          >
            All
          </button>
          <button 
            type="button" 
            class="log-tab {activeLogTab==='error' ? 'active' : ''}" 
            aria-pressed={activeLogTab==='error'} 
            onclick={() => (activeLogTab='error')}
          >
            Errors
          </button>
          <button 
            type="button" 
            class="log-tab {activeLogTab==='operation' ? 'active' : ''}" 
            aria-pressed={activeLogTab==='operation'} 
            onclick={() => (activeLogTab='operation')}
          >
            Operations
          </button>
        </div>

        <div class="log-actions">
          <button class="action-btn">
            <img class="icon" src={exportIcon} alt="Export" width="18" height="18" />
            <span>Export</span>
          </button>
          <button class="action-btn">
            <span>View</span>
            <img class="icon" src={viewIcon} alt="View" width="18" height="18" />
          </button>
        </div>
      </div>
    </section>

    <!-- Backup - spans both columns on bottom -->
    <section class="card card-backup">
      <div class="card-header">
        <svg class="icon" viewBox="0 0 24 24" aria-hidden="true" width="20" height="20">
          <path d="M5 3h11l5 5v13H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2Z" fill="none" stroke="currentColor" stroke-width="2"/>
          <rect x="7" y="3" width="8" height="5" fill="none" stroke="currentColor" stroke-width="2"/>
          <rect x="7" y="13" width="10" height="6" rx="1" fill="none" stroke="currentColor" stroke-width="2"/>
        </svg>
        <h2 class="card-title">Backup</h2>
      </div>

      <div class="card-content">
        <p class="help-text">Hold 2s to save/restore</p>

        <div class="backup-row">
          <div class="backup-group">
            <button
              class="hold-button"
              style={`--p:${storeProgress}`}
              onpointerdown={() => startHold('store')}
              onpointerup={() => cancelHold('store')}
              onpointerleave={() => cancelHold('store')}
              onpointercancel={() => cancelHold('store')}
            >
              <span class="progress-ring"></span>
              <svg width="16" height="16" viewBox="0 0 24 24" aria-hidden="true">
                <path d="M5 3h11l5 5v13H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2Z" fill="none" stroke="currentColor" stroke-width="2"/>
                <rect x="7" y="3" width="8" height="5" fill="none" stroke="currentColor" stroke-width="2"/>
              </svg>
              <span>Store</span>
            </button>
            <input class="timestamp-input" value={storeTimestamp} readonly />
          </div>

          <div class="backup-group">
            <button
              class="hold-button"
              style={`--p:${restoreProgress}`}
              onpointerdown={() => startHold('restore')}
              onpointerup={() => cancelHold('restore')}
              onpointerleave={() => cancelHold('restore')}
              onpointercancel={() => cancelHold('restore')}
            >
              <span class="progress-ring"></span>
              <svg width="16" height="16" viewBox="0 0 24 24" aria-hidden="true">
                <path d="M12 3v10M7 8l5 5 5-5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M5 21h14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              </svg>
              <span>Restore</span>
            </button>
            <input class="timestamp-input" value={restoreTimestamp} readonly />
          </div>
        </div>
      </div>
    </section>
  </div>
</div>

<style>
  :global(html, body) { 
    height: 100%; 
    margin: 0; 
    padding: 0; 
    overflow: hidden;
  }
  
  :global(*), :global(*::before), :global(*::after) { 
    box-sizing: border-box; 
  }

  :global(:root) {
    --primary: #111827;
    --secondary: #6B7280;
    --border: #E5E7EB;
    --bg-card: #FFFFFF;
    --bg-page: #F9FAFB;
    --brand: #E54817;
    --brand-light: rgba(229, 72, 23, 0.1);
    --track-rest: #E5E7EB;
  }

  :global(body) {
    font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    color: var(--primary);
    background: var(--bg-page);
    line-height: 1.5;
    -webkit-font-smoothing: antialiased;
  }

  /* Page optimized for 1024x600 */
  .page {
    width: 1024px;
    height: 600px;
    padding: 20px 24px;
    display: flex;
    flex-direction: column;
    gap: 16px;
    background: var(--bg-page);
    overflow: hidden;
    margin: 0 auto;
  }

  /* Header with natural spacing */
  .topbar {
    display: flex;
    align-items: flex-start;
    gap: 14px;
    flex-shrink: 0;
  }

  .iconbtn {
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 1px solid var(--border);
    border-radius: 8px;
    background: var(--bg-card);
    cursor: pointer;
    transition: all 0.2s;
    flex-shrink: 0;
  }

  .iconbtn:hover {
    background: var(--bg-page);
    border-color: var(--secondary);
  }

  .titleblock {
    flex: 1;
    min-width: 0;
  }

  .h1 {
    font-size: 26px;
    font-weight: 700;
    margin: 0 0 6px 0;
    color: var(--primary);
    letter-spacing: -0.02em;
    line-height: 1.2;
  }

  .meta {
    font-size: 13px;
    color: var(--secondary);
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
    line-height: 1.3;
  }

  .meta-label {
    font-weight: 600;
    color: var(--primary);
  }

  .divider {
    height: 1px;
    background: var(--border);
    margin: 0;
    flex-shrink: 0;
  }

  /* Grid Layout - Optimized for 1024x600 */
  .content-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 14px;
    flex: 1;
    min-height: 0;
    overflow: hidden;
    grid-template-rows: 1fr 1fr auto;
    grid-template-areas:
      "language brightness"
      "network logs"
      "backup backup";
  }

  .card-language { grid-area: language; }
  .card-brightness { grid-area: brightness; }
  .card-network { grid-area: network; }
  .card-logs { grid-area: logs; }
  .card-backup { grid-area: backup; }

  /* Card with proper content structure */
  .card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 16px;
    display: flex;
    flex-direction: column;
    gap: 0;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
    min-height: 0;
    overflow: hidden;
  }

  .card-header {
    display: flex;
    align-items: center;
    gap: 10px;
    flex-shrink: 0;
    margin-bottom: 14px;
  }

  .card-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 10px;
    min-height: 0;
  }

  /* BIGGER card titles */
  .card-title {
    font-size: 18px;
    font-weight: 700;
    margin: 0;
    color: var(--primary);
    line-height: 1.2;
  }

  .icon {
    width: 20px;
    height: 20px;
    flex-shrink: 0;
  }

  .lock-icon {
    margin-left: auto;
    opacity: 0.5;
    width: 18px;
    height: 18px;
  }

  /* Language Section */
  .lang-toggle {
    display: flex;
    flex-direction: column;
    gap: 10px;
    flex: 1;
  }

  .lang-btn {
    flex: 1;
    min-height: 0;
    padding: 0 14px;
    border: 1.5px solid var(--border);
    border-radius: 8px;
    background: var(--bg-card);
    font-size: 14px;
    font-weight: 500;
    color: var(--secondary);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    transition: all 0.2s;
  }

  .lang-btn:hover {
    border-color: var(--secondary);
    background: var(--bg-page);
  }

  .lang-btn.active {
    border-color: var(--brand);
    color: var(--brand);
    background: var(--brand-light);
  }

  .check-dot {
    width: 16px;
    height: 16px;
    border-radius: 50%;
    background: var(--brand);
    display: flex;
    align-items: center;
    justify-content: center;
  }

  /* Brightness Slider */
  .slider-container {
    width: 100%;
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .slider {
    -webkit-appearance: none;
    appearance: none;
    width: 100%;
    height: 8px;
    border-radius: 8px;
    outline: none;
    cursor: pointer;
  }

  .slider::-webkit-slider-thumb {
    -webkit-appearance: none;
    appearance: none;
    width: 22px;
    height: 22px;
    background: var(--slider-thumb) center/contain no-repeat;
    border: 0;
    cursor: pointer;
    transition: transform 0.1s;
  }

  .slider::-webkit-slider-thumb:hover {
    transform: scale(1.1);
  }

  .slider::-moz-range-thumb {
    width: 22px;
    height: 22px;
    background: var(--slider-thumb) center/contain no-repeat;
    border: 0;
    cursor: pointer;
    transition: transform 0.1s;
  }

  /* Network Section */
  .section-label {
    font-size: 12px;
    font-weight: 600;
    color: var(--primary);
    margin-bottom: 4px;
  }

  .ip-wrapper {
    position: relative;
    display: flex;
    align-items: center;
  }

  .ip-input {
    width: 100%;
    height: 38px;
    padding: 0 44px 0 12px;
    border: 1.5px solid var(--border);
    border-radius: 8px;
    background: var(--bg-card);
    font-size: 13px;
    color: var(--secondary);
    font-family: "Inter", monospace;
  }

  .reveal-btn {
    position: absolute;
    right: 6px;
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    border: none;
    background: transparent;
    border-radius: 6px;
    cursor: pointer;
    transition: background 0.2s;
  }

  .reveal-btn:hover {
    background: var(--bg-page);
  }

  .eye-icon {
    color: var(--secondary);
    transition: color 0.2s;
  }

  .reveal-btn:hover .eye-icon {
    color: var(--primary);
  }

  /* Backup Section - Compact */
  .card-backup .card-content {
    gap: 8px;
  }

  .help-text {
    font-size: 12px;
    color: var(--secondary);
    margin: 0;
    line-height: 1.4;
  }

  .backup-row {
    display: flex;
    gap: 14px;
    align-items: center;
  }

  .backup-group {
    display: flex;
    flex-direction: column;
    gap: 6px;
    flex: 1;
  }

  .hold-button {
    width: 100%;
    height: 36px;
    padding: 0 12px;
    border: 1.5px solid var(--border);
    border-radius: 8px;
    background: var(--bg-card);
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 13px;
    font-weight: 500;
    color: var(--primary);
    cursor: pointer;
    position: relative;
    transition: all 0.2s;
  }

  .hold-button:hover {
    border-color: var(--secondary);
    background: var(--bg-page);
  }

  .progress-ring {
    width: 16px;
    height: 16px;
    border-radius: 50%;
    background: conic-gradient(var(--brand) calc(var(--p, 0) * 360deg), var(--track-rest) 0);
    flex-shrink: 0;
  }

  .timestamp-input {
    width: 100%;
    height: 32px;
    padding: 0 12px;
    border: 1.5px solid var(--border);
    border-radius: 8px;
    background: var(--bg-page);
    font-size: 11px;
    color: var(--secondary);
    font-family: "Inter", monospace;
  }

  /* Logs Section */
  .log-tabs {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
  }

  .log-tab {
    height: 34px;
    padding: 0 12px;
    border: 1.5px solid var(--border);
    border-radius: 8px;
    background: var(--bg-card);
    font-size: 12px;
    font-weight: 500;
    color: var(--secondary);
    cursor: pointer;
    transition: all 0.2s;
    white-space: nowrap;
  }

  .log-tab:hover {
    border-color: var(--secondary);
    background: var(--bg-page);
  }

  .log-tab.active {
    border-color: var(--brand);
    color: var(--brand);
    background: var(--brand-light);
  }

  .log-actions {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    margin-top: auto;
  }

  .action-btn {
    flex: 1;
    min-width: 0;
    height: 38px;
    padding: 0 12px;
    border: 1.5px solid var(--border);
    border-radius: 8px;
    background: var(--bg-card);
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    font-size: 13px;
    font-weight: 600;
    color: var(--primary);
    cursor: pointer;
    transition: all 0.2s;
  }

  .action-btn:hover {
    border-color: var(--secondary);
    background: var(--bg-page);
  }
</style>

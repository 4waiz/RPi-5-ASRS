<script lang="ts">
  import { onMount, onDestroy } from "svelte";
  import { currentPage, USER_TOKEN, isPassWordPopupOpen, curentMode } from "../stores/AppStore";

  import arrowBackIcon from "../assets/settingPage/arrow-1.svg";
  import languageIcon from "../assets/settingPage/frame6.svg";
  import brightnessIcon from "../assets/settingPage/frame3.svg";
  import networkIcon from "../assets/settingPage/frame4.svg";
  import padlockIcon from "../assets/settingPage/frame7.svg";
  import revealIcon from "../assets/settingPage/frame1.svg";
  import logsPadlockIcon from "../assets/settingPage/frame8.svg";
  import logsFilterIcon from "../assets/settingPage/frame.svg";
  import exportIcon from "../assets/settingPage/frame2.svg";
  import checkIcon from "../assets/settingPage/check.svg";
  import viewIcon from "../assets/settingPage/arrow-6.svg";
  import sliderThumb from "../assets/settingPage/slider.svg";
  import { t, currentLanguage, setLanguage } from "../lib/i18n";



  let previousBodyOverflow = "";
  onMount(() => {
    if (typeof document === "undefined") return;
    previousBodyOverflow = document.body.style.overflow;
    document.body.style.overflow = previousBodyOverflow || "auto";

    // Apply initial brightness
    applyBrightness(brightness);

    return () => {
      document.body.style.overflow = previousBodyOverflow || "";
    };
  });

  // Clear the token when leaving the Settings page only if in Live mode
  // If in Edit/Test mode, keep the token so user stays authenticated
  let currentModeValue: string;
  const unsubscribeMode = curentMode.subscribe((mode) => {
    currentModeValue = mode;
  });

  onDestroy(() => {
    unsubscribeMode();
    // Only reset token if user is in Live mode
    if (currentModeValue === "Live") {
      USER_TOKEN.set("");
    }
  });

  // Prevent browser zoom
  $effect(() => {
    if (typeof window === "undefined") return;
    const wheel = (e: WheelEvent) => {
      if (e.ctrlKey || e.metaKey) e.preventDefault();
    };
    const keyd = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && ["+", "-", "=", "_", "0"].includes(e.key))
        e.preventDefault();
    };
    window.addEventListener("wheel", wheel, { passive: false });
    window.addEventListener("keydown", keyd);
    return () => {
      window.removeEventListener("wheel", wheel);
      window.removeEventListener("keydown", keyd);
    };
  });

  // Demo values
  const asrsId = $state("Station A01");
  const runtime = $state("00:08:20");
  const timestamp = $state("11/03/2025, 06:38:08");

  // Sync local language state with the i18n store
  let language = $state<"en" | "ar">("en");

  // Subscribe to currentLanguage store to keep local state in sync
  $effect(() => {
    const unsubscribe = currentLanguage.subscribe((lang) => {
      language = lang;
    });
    return unsubscribe;
  });
  // Load brightness from localStorage or default to 100
  let brightness = $state(
    typeof localStorage !== "undefined"
      ? parseInt(localStorage.getItem("display-brightness") || "100", 10)
      : 100,
  );
  let activeLogTab = $state<"all" | "error" | "operation">("all");

  // Network authentication state - reactive to USER_TOKEN
  let isNetworkAuthenticated = $derived($USER_TOKEN !== "");

  function handleUnlockNetwork() {
    isPassWordPopupOpen.set(true);
  }

  // Apply brightness to display
  function applyBrightness(value: number) {
    // For web/browser: adjust opacity of a dimming overlay
    if (typeof document !== "undefined") {
      // Set minimum brightness to 10% so screen is never completely black
      const minBrightness = 10;
      const adjustedValue = Math.max(minBrightness, value);
      const dimValue = 1 - adjustedValue / 100;
      document.documentElement.style.setProperty(
        "--screen-brightness",
        `${dimValue}`,
      );

      // Also try to use the Screen Brightness API if available
      if ("setBrightness" in navigator) {
        (navigator as any).setBrightness(adjustedValue / 100).catch(() => {
          console.log("Screen Brightness API not available");
        });
      }
    }
  }

  // Watch brightness changes and apply them
  $effect(() => {
    applyBrightness(brightness);
  });

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
      if (kind === "store") storeProgress = p;
      else restoreProgress = p;
      if (p >= 1) {
        cancelHold(kind);
        if (kind === "store") storeTimestamp = nowString();
        else restoreTimestamp = nowString();
      }
    };
    const id = setInterval(tick, 16);
    if (kind === "store") storeTimer = id;
    else restoreTimer = id;
  }
  function cancelHold(kind: "store" | "restore") {
    if (kind === "store") {
      if (storeTimer) clearInterval(storeTimer);
      storeTimer = null;
      storeProgress = 0;
    } else {
      if (restoreTimer) clearInterval(restoreTimer);
      restoreTimer = null;
      restoreProgress = 0;
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
  <meta
    name="viewport"
    content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no"
  />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link
    rel="stylesheet"
    href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"
  />
</svelte:head>

<button class="back-button" onclick={() => currentPage.set("Home")}>
  <img src={arrowBackIcon} alt="Back" />
</button>

<div class="page">
  <div class="settings-shell">
    <!-- Header -->
    <div class="topbar">
      <div class="titleblock">
        <h1 class="h1">{$t('settings.title')}</h1>
        <div class="meta">
          <span class="meta-label">{$t('settings.asrsId')}:</span
          >&nbsp;{asrsId}&nbsp;&nbsp;·&nbsp;&nbsp;
          <span class="meta-label">{$t('settings.runtime')}:</span
          >&nbsp;{runtime}&nbsp;&nbsp;·&nbsp;&nbsp;
          <span class="meta-label">{$t('settings.timestamp')}:</span>&nbsp;{timestamp}
        </div>
      </div>
    </div>

    <div class="divider"></div>

    <!-- Main grid -->
    <div class="content-grid">
      <!-- Language -->
      <section class="card card-language">
        <div class="card-header">
          <img
            class="icon"
            src={languageIcon}
            alt="Language"
            width="18"
            height="18"
          />
          <h2 class="card-title">{$t('settings.language')}</h2>
        </div>

        <div class="lang-toggle">
          <button
            type="button"
            class="lang-btn {language === 'en' ? 'active' : ''}"
            aria-pressed={language === "en"}
            onclick={() => setLanguage("en")}
          >
            {#if language === "en"}
              <span class="check-dot"
                ><img src={checkIcon} alt="" width="10" height="10" /></span
              >
            {/if}
            {$t('settings.english')}
          </button>

          <button
            type="button"
            class="lang-btn {language === 'ar' ? 'active' : ''}"
            aria-pressed={language === "ar"}
            onclick={() => setLanguage("ar")}
          >
            {#if language === "ar"}
              <span class="check-dot"
                ><img src={checkIcon} alt="" width="10" height="10" /></span
              >
            {/if}
            {$t('settings.arabic')}
          </button>
        </div>
      </section>

      <!-- Brightness -->
      <section class="card card-brightness">
        <div class="card-header">
          <img
            class="icon"
            src={brightnessIcon}
            alt="Brightness"
            width="18"
            height="18"
          />
          <h2 class="card-title">{$t('settings.brightness')}</h2>
          <span class="brightness-value">{brightness}%</span>
        </div>

        <div class="slider-wrapper">
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
      </section>

      <!-- Network -->
      <section class="card card-network">
        <div class="card-header">
          <img
            class="icon"
            src={networkIcon}
            alt="Network"
            width="18"
            height="18"
          />
          <h2 class="card-title">{$t('settings.network')}</h2>
          <img
            class="icon lock-icon"
            src={padlockIcon}
            alt={isNetworkAuthenticated ? "Unlocked" : "Locked"}
            width="16"
            height="16"
          />
        </div>

        {#if isNetworkAuthenticated}
          <div class="network-content">
            <div class="section-label">{$t('settings.machineIps')}</div>

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
                <svg class="eye-icon" viewBox="0 0 24 24" width="16" height="16">
                  <path
                    d="M12 5C7 5 2.73 8.11 1 12.5 2.73 16.89 7 20 12 20s9.27-3.11 11-7.5C21.27 8.11 17 5 12 5z"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                  />
                  <circle
                    cx="12"
                    cy="12.5"
                    r="3.5"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                  />
                  {#if ip1Masked}
                    <line
                      x1="4"
                      y1="4"
                      x2="20"
                      y2="21"
                      stroke="currentColor"
                      stroke-width="2"
                      stroke-linecap="round"
                    />
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
                <svg class="eye-icon" viewBox="0 0 24 24" width="16" height="16">
                  <path
                    d="M12 5C7 5 2.73 8.11 1 12.5 2.73 16.89 7 20 12 20s9.27-3.11 11-7.5C21.27 8.11 17 5 12 5z"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                  />
                  <circle
                    cx="12"
                    cy="12.5"
                    r="3.5"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                  />
                  {#if ip2Masked}
                    <line
                      x1="4"
                      y1="4"
                      x2="20"
                      y2="21"
                      stroke="currentColor"
                      stroke-width="2"
                      stroke-linecap="round"
                    />
                  {/if}
                </svg>
              </button>
            </div>
          </div>
        {:else}
          <div class="network-locked">
            <div class="locked-icon">
              <svg viewBox="0 0 24 24" width="32" height="32">
                <rect
                  x="3"
                  y="11"
                  width="18"
                  height="11"
                  rx="2"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                />
                <path
                  d="M7 11V7a5 5 0 0 1 10 0v4"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                />
              </svg>
            </div>
            <p class="locked-text">{$t('settings.authRequired') || 'Authentication required to view IP addresses'}</p>
            <button
              class="unlock-btn"
              type="button"
              onclick={handleUnlockNetwork}
            >
              <svg viewBox="0 0 24 24" width="14" height="14">
                <rect
                  x="3"
                  y="11"
                  width="18"
                  height="11"
                  rx="2"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                />
                <path
                  d="M7 11V7a5 5 0 0 1 9.9-1"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                />
              </svg>
              <span>{$t('settings.unlock') || 'Unlock'}</span>
            </button>
          </div>
        {/if}
      </section>

      <!-- Logs -->
      <section class="card card-logs">
        <div class="card-header">
          <img
            class="icon"
            src={logsPadlockIcon}
            alt="Locked"
            width="18"
            height="18"
          />
          <h2 class="card-title">{$t('settings.logs')}</h2>
          <img
            class="icon lock-icon"
            src={logsFilterIcon}
            alt="Filter"
            width="16"
            height="16"
          />
        </div>

        <div class="logs-content">
          <div class="log-tabs">
            <button
              type="button"
              class="log-tab {activeLogTab === 'all' ? 'active' : ''}"
              aria-pressed={activeLogTab === "all"}
              onclick={() => (activeLogTab = "all")}
            >
              {$t('settings.all')}
            </button>
            <button
              type="button"
              class="log-tab {activeLogTab === 'error' ? 'active' : ''}"
              aria-pressed={activeLogTab === "error"}
              onclick={() => (activeLogTab = "error")}
            >
              {$t('settings.errors')}
            </button>
            <button
              type="button"
              class="log-tab {activeLogTab === 'operation' ? 'active' : ''}"
              aria-pressed={activeLogTab === "operation"}
              onclick={() => (activeLogTab = "operation")}
            >
              {$t('settings.operations')}
            </button>
          </div>

          <div class="log-actions">
            <button class="action-btn">
              <img
                class="icon"
                src={exportIcon}
                alt="Export"
                width="16"
                height="16"
              />
              <span>{$t('settings.export')}</span>
            </button>
            <button class="action-btn">
              <span>{$t('settings.view')}</span>
              <img
                class="icon"
                src={viewIcon}
                alt="View"
                width="16"
                height="16"
              />
            </button>
          </div>
        </div>
      </section>

      <!-- Backup -->
      <section class="card card-backup">
        <div class="card-header">
          <svg
            class="icon"
            viewBox="0 0 24 24"
            aria-hidden="true"
            width="18"
            height="18"
          >
            <path
              d="M5 3h11l5 5v13H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2Z"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            />
            <rect
              x="7"
              y="3"
              width="8"
              height="5"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            />
            <rect
              x="7"
              y="13"
              width="10"
              height="6"
              rx="1"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            />
          </svg>
          <h2 class="card-title">{$t('settings.backup')}</h2>
        </div>

        <p class="help-text">{$t('settings.holdToSaveRestore')}</p>

        <div class="backup-row">
          <div class="backup-group">
            <button
              class="hold-button"
              style={`--p:${storeProgress}`}
              onpointerdown={() => startHold("store")}
              onpointerup={() => cancelHold("store")}
              onpointerleave={() => cancelHold("store")}
              onpointercancel={() => cancelHold("store")}
            >
              <span class="progress-ring"></span>
              <svg
                width="14"
                height="14"
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <path
                  d="M5 3h11l5 5v13H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2Z"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                />
                <rect
                  x="7"
                  y="3"
                  width="8"
                  height="5"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                />
              </svg>
              <span>{$t('settings.store')}</span>
            </button>
            <input class="timestamp-input" value={storeTimestamp} readonly />
          </div>

          <div class="backup-group">
            <button
              class="hold-button"
              style={`--p:${restoreProgress}`}
              onpointerdown={() => startHold("restore")}
              onpointerup={() => cancelHold("restore")}
              onpointerleave={() => cancelHold("restore")}
              onpointercancel={() => cancelHold("restore")}
            >
              <span class="progress-ring"></span>
              <svg
                width="14"
                height="14"
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <path
                  d="M12 3v10M7 8l5 5 5-5"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                />
                <path
                  d="M5 21h14"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                />
              </svg>
              <span>{$t('settings.restore')}</span>
            </button>
            <input class="timestamp-input" value={restoreTimestamp} readonly />
          </div>
        </div>
      </section>
    </div>
  </div>
</div>

<style>
  .back-button {
    position: absolute;
    top: 40px;
    left: 32px;
    border: 1px solid #00000044;
    height: 56px;
    width: 56px;
    display: flex;
    justify-content: center;
    align-items: center;
    border-radius: 200%;
  }

  :global(html, body) {
    min-height: 100%;
    margin: 0;
    padding: 0;
  }

  :global(*),
  :global(*::before),
  :global(*::after) {
    box-sizing: border-box;
  }

  :global(:root) {
    --primary: #111827;
    --secondary: #6b7280;
    --border: #e5e7eb;
    --bg-card: #ffffff;
    --bg-page: #f9fafb;
    --brand: #e54817;
    --brand-light: rgba(229, 72, 23, 0.1);
    --track-rest: #e5e7eb;
    --screen-brightness: 0;
  }

  :global(body::before) {
    content: "";
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: rgba(0, 0, 0, var(--screen-brightness));
    pointer-events: none;
    z-index: 9999;
    transition: background 0.2s ease;
  }

  :global(body) {
    font-family:
      "Inter",
      -apple-system,
      BlinkMacSystemFont,
      "Segoe UI",
      Roboto,
      sans-serif;
    color: var(--primary);
    background: var(--bg-page);
    line-height: 1.5;
    -webkit-font-smoothing: antialiased;
    overflow-y: auto;
  }

  .page {
    width: 100%;
    min-height: 100vh;
    display: flex;
    gap: 48px;
    background: #ebebeb;
    align-items: top;
    justify-content: center;
    box-sizing: border-box;
    overflow-y: auto;
  }

  .settings-shell {
    flex: 1;
    max-width: 80%;
    display: flex;
    flex-direction: column;
    align-items: right;
    justify-content: center;
    gap: 12px;
    padding: 16px 24px;
    max-height: 100vh;
    overflow-y: auto;
  }

  /* Compact Header */
  .topbar {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    flex-shrink: 0;
    height: auto;
    min-height: 40px;
  }

  .titleblock {
    flex: 1;
    min-width: 0;
  }

  .h1 {
    font-size: 32px;
    font-weight: 700;
    margin: 16 0 8px 0;
    color: var(--primary);
    letter-spacing: -0.02em;
    line-height: 1.2;
  }

  .meta {
    font-size: 14px;
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

  .content-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 12px;
    width: 100%;
    flex: 1;
    align-content: start;
    grid-auto-rows: minmax(min-content, max-content);
    grid-template-areas:
      "language brightness"
      "network logs"
      "backup  backup";
  }

  .card-language {
    grid-area: language;
    align-self: stretch;
  }
  .card-brightness {
    grid-area: brightness;
    align-self: stretch;
  }
  .card-network {
    grid-area: network;
    align-self: stretch;
  }
  .card-logs {
    grid-area: logs;
    align-self: stretch;
  }
  .card-backup {
    grid-area: backup;
  }

  /* Compact Card */
  .card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 14px 16px;
    display: flex;
    flex-direction: column;
    gap: 10px;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
    min-height: 0;
    overflow: hidden;
    height: 100%;
  }

  .card-header {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-shrink: 0;
  }

  .card-title {
    font-size: 14px;
    font-weight: 700;
    margin: 0;
    color: var(--primary);
    line-height: 1.2;
  }

  .icon {
    width: 18px;
    height: 18px;
    flex-shrink: 0;
  }

  .lock-icon {
    margin-left: auto;
    opacity: 0.5;
    width: 16px;
    height: 16px;
  }

  /* Language */
  .lang-toggle {
    display: flex;
    flex-direction: column;
    gap: 8px;
    flex: 1;
    min-height: 0;
    justify-content: space-evenly;
  }

  .lang-btn {
    flex: 1;
    min-height: 38px;
    height: 38px;
    padding: 0 12px;
    border: 1.5px solid var(--border);
    border-radius: 8px;
    background: var(--bg-card);
    font-size: 12px;
    font-weight: 500;
    color: var(--secondary);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
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
    width: 14px;
    height: 14px;
    border-radius: 50%;
    background: var(--brand);
    display: flex;
    align-items: center;
    justify-content: center;
  }

  /* Brightness */
  .brightness-value {
    margin-left: auto;
    font-size: 16px;
    font-weight: 700;
    color: var(--brand);
    padding: 2px 10px;
    border-radius: 6px;
    background: var(--brand-light);
    min-width: 50px;
    text-align: center;
  }

  .slider-wrapper {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 4px 0;
  }

  .slider {
    -webkit-appearance: none;
    appearance: none;
    width: 100%;
    height: 7px;
    border-radius: 7px;
    outline: none;
    cursor: pointer;
  }

  .slider::-webkit-slider-thumb {
    -webkit-appearance: none;
    appearance: none;
    width: 20px;
    height: 20px;
    background: var(--slider-thumb) center/contain no-repeat;
    border: 0;
    cursor: pointer;
    transition: transform 0.1s;
  }

  .slider::-webkit-slider-thumb:hover {
    transform: scale(1.1);
  }

  .slider::-moz-range-thumb {
    width: 20px;
    height: 20px;
    background: var(--slider-thumb) center/contain no-repeat;
    border: 0;
    cursor: pointer;
    transition: transform 0.1s;
  }

  /* Network */
  .network-content {
    display: flex;
    flex-direction: column;
    gap: 8px;
    flex: 1;
    justify-content: space-evenly;
  }

  .section-label {
    font-size: 11px;
    font-weight: 600;
    color: var(--primary);
  }

  .ip-wrapper {
    position: relative;
    display: flex;
    align-items: center;
  }

  .ip-input {
    width: 100%;
    height: 34px;
    padding: 0 42px 0 10px;
    border: 1.5px solid var(--border);
    border-radius: 7px;
    background: var(--bg-card);
    font-size: 11px;
    color: var(--secondary);
    font-family: "Inter", monospace;
  }

  .reveal-btn {
    position: absolute;
    right: 4px;
    width: 30px;
    height: 30px;
    display: flex;
    align-items: center;
    justify-content: center;
    border: none;
    background: transparent;
    border-radius: 5px;
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

  /* Network Locked State */
  .network-locked {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 12px;
    flex: 1;
    padding: 16px 0;
  }

  .locked-icon {
    color: var(--secondary);
    opacity: 0.6;
  }

  .locked-text {
    font-size: 12px;
    color: var(--secondary);
    text-align: center;
    margin: 0;
    line-height: 1.4;
  }

  .unlock-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    padding: 8px 16px;
    border: 1.5px solid var(--brand);
    border-radius: 8px;
    background: var(--brand-light);
    color: var(--brand);
    font-size: 12px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
  }

  .unlock-btn:hover {
    background: var(--brand);
    color: white;
  }

  .unlock-btn svg {
    flex-shrink: 0;
  }

  /* Logs */
  .logs-content {
    display: flex;
    flex-direction: column;
    gap: 10px;
    flex: 1;
    justify-content: space-evenly;
  }

  .log-tabs {
    display: flex;
    gap: 6px;
    flex-wrap: wrap;
  }

  .log-tab {
    height: 32px;
    padding: 0 10px;
    border: 1.5px solid var(--border);
    border-radius: 7px;
    background: var(--bg-card);
    font-size: 11px;
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
    gap: 8px;
  }

  .action-btn {
    flex: 1;
    height: 36px;
    padding: 0 10px;
    border: 1.5px solid var(--border);
    border-radius: 7px;
    background: var(--bg-card);
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    font-size: 12px;
    font-weight: 600;
    color: var(--primary);
    cursor: pointer;
    transition: all 0.2s;
  }

  .action-btn:hover {
    border-color: var(--secondary);
    background: var(--bg-page);
  }

  /* Backup - Compact */
  .card-backup {
    gap: 8px;
    height: auto !important;
  }

  .help-text {
    font-size: 11px;
    color: var(--secondary);
    margin: 0;
    line-height: 1.3;
  }

  .backup-row {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }

  .backup-group {
    display: flex;
    flex-direction: column;
    gap: 10px;
    flex: 1;
    min-width: 0;
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
    justify-content: center;
    gap: 8px;
    font-size: 12px;
    font-weight: 600;
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
    width: 14px;
    height: 14px;
    border-radius: 50%;
    background: conic-gradient(
      var(--brand) calc(var(--p, 0) * 360deg),
      var(--track-rest) 0
    );
    flex-shrink: 0;
  }

  .timestamp-input {
    width: 100%;
    height: 32px;
    padding: 0 10px;
    border: 1.5px solid var(--border);
    border-radius: 8px;
    background: #f3f4f6;
    font-size: 11px;
    color: var(--secondary);
    font-family: "Inter", monospace;
  }

  @media (max-width: 840px) {
    .content-grid {
      grid-template-columns: 1fr;
      grid-template-areas:
        "language"
        "brightness"
        "network"
        "logs"
        "backup";
      gap: 12px;
    }
  }

  @media (max-width: 680px) {
    .topbar {
      flex-direction: column;
      gap: 8px;
      height: auto;
    }
    .page {
      flex-direction: column;
      padding: 16px;
    }

    .settings-shell {
      padding: 0;
    }
  }

  @media (max-height: 620px) {
    .settings-shell {
      padding: 12px;
      margin-left: 48px;
    }

    .card {
      padding: 12px;
      gap: 8px;
    }

    .hold-button {
      height: 28px;
    }

    .timestamp-input {
      height: 24px;
    }
  }
</style>
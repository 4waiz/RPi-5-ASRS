<script lang="ts">
  import { onMount } from "svelte";
  import SideBar from "../components/shared/Sidebar.svelte";

  import checkIcon         from "../assets/settingPage/check.svg";
  import sliderThumb       from "../assets/settingPage/slider.svg";

  import { myVariable } from "../store";
  import Home from "./Home.svelte";

  // i18n importss
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
  const asrsId    = $state("Station A01");
  const runtime   = $state("00:08:20");
  const timestamp = $state("11/03/2025, 06:38:08");

  // Load brightness from localStorage or default to 100
  let brightness = $state(
    typeof localStorage !== 'undefined'
      ? parseInt(localStorage.getItem('display-brightness') || '100', 10)
      : 100
  );
  let activeLogTab = $state<"all"|"error"|"operation">("all");

  // Language handler
  const handleLanguageChange = (lang: 'en' | 'ar') => {
    setLanguage(lang);
  };

  // Apply brightness to display
  function applyBrightness(value: number) {
    // For web/browser: adjust opacity of a dimming overlay
    if (typeof document !== 'undefined') {
      // Set minimum brightness to 10% so screen is never completely black
      const minBrightness = 10;
      const adjustedValue = Math.max(minBrightness, value);
      const dimValue = 1 - (adjustedValue / 100);
      document.documentElement.style.setProperty('--screen-brightness', `${dimValue}`);

      // Also try to use the Screen Brightness API if available
      if ('setBrightness' in navigator) {
        (navigator as any).setBrightness(adjustedValue / 100).catch(() => {
          console.log('Screen Brightness API not available');
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

  // Password modal for revealing IPs
  let showIpPasswordModal = $state(false);
  let ipPassword = $state('');
  let ipPasswordError = $state('');
  let pendingIpReveal: 1 | 2 | null = $state(null);
  let showKeyboard = $state(false);

  const handleIpRevealClick = (ipNumber: 1 | 2) => {
    const isMasked = ipNumber === 1 ? ip1Masked : ip2Masked;

    // If already revealed, just hide it (no password needed)
    if (!isMasked) {
      if (ipNumber === 1) ip1Masked = true;
      else ip2Masked = true;
      return;
    }

    // If masked, ask for password to reveal
    pendingIpReveal = ipNumber;
    showIpPasswordModal = true;
    ipPassword = '';
    ipPasswordError = '';
  };

  const closeIpPasswordModal = () => {
    showIpPasswordModal = false;
    showKeyboard = false;
    ipPassword = '';
    ipPasswordError = '';
    pendingIpReveal = null;
  };

  const handleIpPasswordSubmit = () => {
    const CORRECT_PASSWORD = 'changeme';

    if (ipPassword === CORRECT_PASSWORD) {
      // Reveal the IP
      if (pendingIpReveal === 1) ip1Masked = false;
      else if (pendingIpReveal === 2) ip2Masked = false;
      closeIpPasswordModal();
    } else {
      // Set error flag (message will be translated in template)
      ipPasswordError = 'error';
      ipPassword = '';
    }
  };

  // Virtual Keyboard Functions
  const handleKeyPress = (key: string) => {
    if (key === 'backspace') {
      ipPassword = ipPassword.slice(0, -1);
    } else if (key === 'clear') {
      ipPassword = '';
    } else {
      ipPassword += key;
    }
    ipPasswordError = ''; // Clear error when typing
  };

  const showVirtualKeyboard = () => {
    showKeyboard = true;
  };

  // Animation for key press
  const animateKeyPress = (event: MouseEvent) => {
    const button = event.currentTarget as HTMLElement;
    button.classList.add('key-pressed');

    // Create ripple effect
    const ripple = document.createElement('span');
    ripple.classList.add('ripple');
    button.appendChild(ripple);

    setTimeout(() => {
      button.classList.remove('key-pressed');
      ripple.remove();
    }, 600);
  };

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
  <SideBar AlertsNum={5} ActivePage="Settings" />

  <div class="settings-shell">
    <!-- Header -->
    <div class="topbar">

      <div class="titleblock">
        <h1 class="h1">{$t('settings.title')}</h1>
      <div class="meta">
        <span class="meta-label">{$t('settings.asrsId')}:</span>&nbsp;{asrsId}&nbsp;&nbsp;·&nbsp;&nbsp;
        <span class="meta-label">{$t('settings.runtime')}:</span>&nbsp;{runtime}&nbsp;&nbsp;·&nbsp;&nbsp;
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
        <svg class="icon icon-animated" viewBox="0 0 24 24" width="18" height="18">
          <circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" stroke-width="2"/>
          <path d="M12 2C7 2 3 6 3 12c0 6 4 10 9 10" fill="none" stroke="currentColor" stroke-width="2"/>
          <path d="M12 2c-1.5 3-2.5 7-2.5 10s1 7 2.5 10M12 2c1.5 3 2.5 7 2.5 10s-1 7-2.5 10" fill="none" stroke="currentColor" stroke-width="2"/>
          <path d="M2 12h20M3.5 7h17M3.5 17h17" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
        <h2 class="card-title">{$t('settings.language')}</h2>
      </div>

      <div class="lang-toggle">
        <button
          type="button"
          class="lang-btn {$currentLanguage==='en' ? 'active' : ''}"
          aria-pressed={$currentLanguage==='en'}
          onclick={() => handleLanguageChange('en')}
        >
          {#if $currentLanguage==='en'}
            <span class="check-dot"><img src={checkIcon} alt="" width="10" height="10" /></span>
          {/if}
          {$t('settings.english')}
        </button>

        <button
          type="button"
          class="lang-btn {$currentLanguage==='ar' ? 'active' : ''}"
          aria-pressed={$currentLanguage==='ar'}
          onclick={() => handleLanguageChange('ar')}
        >
          {#if $currentLanguage==='ar'}
            <span class="check-dot"><img src={checkIcon} alt="" width="10" height="10" /></span>
          {/if}
          {$t('settings.arabic')}
        </button>
      </div>
    </section>

    <!-- Brightness -->
    <section class="card card-brightness">
      <div class="card-header">
        <svg class="icon icon-animated" viewBox="0 0 24 24" width="18" height="18">
          <circle cx="12" cy="12" r="4" fill="none" stroke="currentColor" stroke-width="2"/>
          <path d="M12 2v4M12 18v4M22 12h-4M6 12H2M19.07 4.93l-2.83 2.83M7.76 16.24l-2.83 2.83M19.07 19.07l-2.83-2.83M7.76 7.76L4.93 4.93" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
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
        <svg class="icon icon-animated" viewBox="0 0 24 24" width="18" height="18">
          <circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" stroke-width="2"/>
          <ellipse cx="12" cy="12" rx="5" ry="10" fill="none" stroke="currentColor" stroke-width="2"/>
          <path d="M2 12h20M12 2c-2.5 3-4 7-4 10s1.5 7 4 10M12 2c2.5 3 4 7 4 10s-1.5 7-4 10" fill="none" stroke="currentColor" stroke-width="2"/>
        </svg>
        <h2 class="card-title">{$t('settings.network')}</h2>
        <svg class="icon lock-icon" viewBox="0 0 24 24" width="16" height="16">
          <rect x="6" y="10" width="12" height="10" rx="2" fill="none" stroke="currentColor" stroke-width="2"/>
          <path d="M8 10V7a4 4 0 0 1 8 0v3" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          <circle cx="12" cy="15" r="1.5" fill="currentColor"/>
        </svg>
      </div>

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
            onclick={() => handleIpRevealClick(1)}
          >
            <svg class="eye-icon" viewBox="0 0 24 24" width="16" height="16">
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
            onclick={() => handleIpRevealClick(2)}
          >
            <svg class="eye-icon" viewBox="0 0 24 24" width="16" height="16">
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
        <svg class="icon icon-animated" viewBox="0 0 24 24" width="18" height="18">
          <rect x="4" y="4" width="16" height="16" rx="2" fill="none" stroke="currentColor" stroke-width="2"/>
          <path d="M8 8h8M8 12h6M8 16h4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
        <h2 class="card-title">{$t('settings.logs')}</h2>
        <svg class="icon lock-icon" viewBox="0 0 24 24" width="16" height="16">
          <path d="M3 7l9-4 9 4v10l-9 4-9-4V7z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
          <path d="M3 7l9 4m0 0l9-4m-9 4v10" stroke="currentColor" stroke-width="2"/>
        </svg>
      </div>

      <div class="logs-content">
        <div class="log-tabs">
          <button
            type="button"
            class="log-tab {activeLogTab==='all' ? 'active' : ''}"
            aria-pressed={activeLogTab==='all'}
            onclick={() => (activeLogTab='all')}
          >
            {$t('settings.all')}
          </button>
          <button
            type="button"
            class="log-tab {activeLogTab==='error' ? 'active' : ''}"
            aria-pressed={activeLogTab==='error'}
            onclick={() => (activeLogTab='error')}
          >
            {$t('settings.errors')}
          </button>
          <button
            type="button"
            class="log-tab {activeLogTab==='operation' ? 'active' : ''}"
            aria-pressed={activeLogTab==='operation'}
            onclick={() => (activeLogTab='operation')}
          >
            {$t('settings.operations')}
          </button>
        </div>

        <div class="log-actions">
          <button class="action-btn">
            <svg class="icon" viewBox="0 0 24 24" width="16" height="16">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
            </svg>
            <span>{$t('settings.export')}</span>
          </button>
          <button class="action-btn">
            <span>{$t('settings.view')}</span>
            <svg class="icon" viewBox="0 0 24 24" width="16" height="16">
              <path d="M5 12h14M12 5l7 7-7 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
            </svg>
          </button>
        </div>
      </div>
    </section>

    <!-- Backup -->
    <section class="card card-backup">
      <div class="card-header">
        <svg class="icon" viewBox="0 0 24 24" aria-hidden="true" width="18" height="18">
          <path d="M5 3h11l5 5v13H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2Z" fill="none" stroke="currentColor" stroke-width="2"/>
          <rect x="7" y="3" width="8" height="5" fill="none" stroke="currentColor" stroke-width="2"/>
          <rect x="7" y="13" width="10" height="6" rx="1" fill="none" stroke="currentColor" stroke-width="2"/>
        </svg>
        <h2 class="card-title">{$t('settings.backup')}</h2>
      </div>

      <p class="help-text">{$t('settings.holdToSaveRestore')}</p>

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
            <svg width="14" height="14" viewBox="0 0 24 24" aria-hidden="true">
              <path d="M5 3h11l5 5v13H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2Z" fill="none" stroke="currentColor" stroke-width="2"/>
              <rect x="7" y="3" width="8" height="5" fill="none" stroke="currentColor" stroke-width="2"/>
            </svg>
            <span>{$t('settings.store')}</span>
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
            <svg width="14" height="14" viewBox="0 0 24 24" aria-hidden="true">
              <path d="M12 3v10M7 8l5 5 5-5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M5 21h14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
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

<!-- IP Password Modal -->
{#if showIpPasswordModal}
  <div class="modal-overlay" onclick={closeIpPasswordModal}>
    <div class="modal-content" class:keyboard-visible={showKeyboard} onclick={(e) => e.stopPropagation()}>
      <div class="modal-header">
        <h2>{$t('settings.passwordModal.title')}</h2>
        <button class="close-btn" onclick={closeIpPasswordModal}>
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <line x1="18" y1="6" x2="6" y2="18" stroke-width="2" stroke-linecap="round"/>
            <line x1="6" y1="6" x2="18" y2="18" stroke-width="2" stroke-linecap="round"/>
          </svg>
        </button>
      </div>

      <div class="modal-body">
        <p class="modal-description">{$t('settings.passwordModal.description')}</p>

        <div class="input-group">
          <svg class="input-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <rect x="3" y="11" width="18" height="11" rx="2" ry="2" stroke-width="2"/>
            <path d="M7 11V7a5 5 0 0110 0v4" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <div class="password-display" class:error={ipPasswordError} onclick={showVirtualKeyboard}>
            {#if ipPassword}
              {'•'.repeat(ipPassword.length)}
            {:else}
              <span class="placeholder-text">{$t('settings.passwordModal.placeholder')}</span>
            {/if}
          </div>
          <input
            type="text"
            class="password-input-hidden"
            value={ipPassword}
            readonly
            onclick={showVirtualKeyboard}
            onfocus={showVirtualKeyboard}
          />
        </div>

        {#if ipPasswordError}
          <div class="error-message">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <circle cx="12" cy="12" r="10" stroke-width="2"/>
              <line x1="12" y1="8" x2="12" y2="12" stroke-width="2" stroke-linecap="round"/>
              <line x1="12" y1="16" x2="12.01" y2="16" stroke-width="2" stroke-linecap="round"/>
            </svg>
            {$t('settings.passwordModal.error')}
          </div>
        {/if}
      </div>

      <div class="modal-footer">
        <button class="btn-cancel" onclick={closeIpPasswordModal}>{$t('common.cancel')}</button>
        <button class="btn-submit" onclick={handleIpPasswordSubmit}>{$t('common.submit')}</button>
      </div>
    </div>
  </div>
{/if}

<!-- Virtual Keyboard - Separate Overlay -->
{#if showKeyboard && showIpPasswordModal}
  <div class="keyboard-overlay">
    <div class="virtual-keyboard">
      <div class="keyboard-body">
        <!-- Row 1 - Numbers -->
        <div class="keyboard-row">
          <button class="key" onclick={(e) => { animateKeyPress(e); handleKeyPress('1'); }}>1</button>
          <button class="key" onclick={(e) => { animateKeyPress(e); handleKeyPress('2'); }}>2</button>
          <button class="key" onclick={(e) => { animateKeyPress(e); handleKeyPress('3'); }}>3</button>
          <button class="key" onclick={(e) => { animateKeyPress(e); handleKeyPress('4'); }}>4</button>
          <button class="key" onclick={(e) => { animateKeyPress(e); handleKeyPress('5'); }}>5</button>
          <button class="key" onclick={(e) => { animateKeyPress(e); handleKeyPress('6'); }}>6</button>
          <button class="key" onclick={(e) => { animateKeyPress(e); handleKeyPress('7'); }}>7</button>
          <button class="key" onclick={(e) => { animateKeyPress(e); handleKeyPress('8'); }}>8</button>
          <button class="key" onclick={(e) => { animateKeyPress(e); handleKeyPress('9'); }}>9</button>
          <button class="key" onclick={(e) => { animateKeyPress(e); handleKeyPress('0'); }}>0</button>
        </div>

        <!-- Row 2 - QWERTY -->
        <div class="keyboard-row">
          <button class="key" onclick={(e) => { animateKeyPress(e); handleKeyPress('q'); }}>Q</button>
          <button class="key" onclick={(e) => { animateKeyPress(e); handleKeyPress('w'); }}>W</button>
          <button class="key" onclick={(e) => { animateKeyPress(e); handleKeyPress('e'); }}>E</button>
          <button class="key" onclick={(e) => { animateKeyPress(e); handleKeyPress('r'); }}>R</button>
          <button class="key" onclick={(e) => { animateKeyPress(e); handleKeyPress('t'); }}>T</button>
          <button class="key" onclick={(e) => { animateKeyPress(e); handleKeyPress('y'); }}>Y</button>
          <button class="key" onclick={(e) => { animateKeyPress(e); handleKeyPress('u'); }}>U</button>
          <button class="key" onclick={(e) => { animateKeyPress(e); handleKeyPress('i'); }}>I</button>
          <button class="key" onclick={(e) => { animateKeyPress(e); handleKeyPress('o'); }}>O</button>
          <button class="key" onclick={(e) => { animateKeyPress(e); handleKeyPress('p'); }}>P</button>
        </div>

        <!-- Row 3 - ASDFGH -->
        <div class="keyboard-row">
          <button class="key" onclick={(e) => { animateKeyPress(e); handleKeyPress('a'); }}>A</button>
          <button class="key" onclick={(e) => { animateKeyPress(e); handleKeyPress('s'); }}>S</button>
          <button class="key" onclick={(e) => { animateKeyPress(e); handleKeyPress('d'); }}>D</button>
          <button class="key" onclick={(e) => { animateKeyPress(e); handleKeyPress('f'); }}>F</button>
          <button class="key" onclick={(e) => { animateKeyPress(e); handleKeyPress('g'); }}>G</button>
          <button class="key" onclick={(e) => { animateKeyPress(e); handleKeyPress('h'); }}>H</button>
          <button class="key" onclick={(e) => { animateKeyPress(e); handleKeyPress('j'); }}>J</button>
          <button class="key" onclick={(e) => { animateKeyPress(e); handleKeyPress('k'); }}>K</button>
          <button class="key" onclick={(e) => { animateKeyPress(e); handleKeyPress('l'); }}>L</button>
          <button class="key key-backspace" onclick={(e) => { animateKeyPress(e); handleKeyPress('backspace'); }}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M9 3h11a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H9l-7-9 7-9z" stroke-linecap="round" stroke-linejoin="round"/>
              <line x1="14" y1="9" x2="18" y2="13" stroke-linecap="round"/>
              <line x1="18" y1="9" x2="14" y2="13" stroke-linecap="round"/>
            </svg>
          </button>
        </div>

        <!-- Row 4 - ZXCVBN -->
        <div class="keyboard-row">
          <button class="key" onclick={(e) => { animateKeyPress(e); handleKeyPress('z'); }}>Z</button>
          <button class="key" onclick={(e) => { animateKeyPress(e); handleKeyPress('x'); }}>X</button>
          <button class="key" onclick={(e) => { animateKeyPress(e); handleKeyPress('c'); }}>C</button>
          <button class="key" onclick={(e) => { animateKeyPress(e); handleKeyPress('v'); }}>V</button>
          <button class="key" onclick={(e) => { animateKeyPress(e); handleKeyPress('b'); }}>B</button>
          <button class="key" onclick={(e) => { animateKeyPress(e); handleKeyPress('n'); }}>N</button>
          <button class="key" onclick={(e) => { animateKeyPress(e); handleKeyPress('m'); }}>M</button>
          <button class="key key-clear" onclick={(e) => { animateKeyPress(e); handleKeyPress('clear'); }}>{$t('settings.passwordModal.clear')}</button>
        </div>
      </div>
    </div>
  </div>
{/if}

<style>
  :global(html, body) {
    min-height: 100%;
    margin: 0;
    padding: 0;
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
    --screen-brightness: 0;
  }

  
  :global(body::before) {
    content: '';
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
    font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    color: var(--primary);
    background: var(--bg-page);
    line-height: 1.5;
    -webkit-font-smoothing: antialiased;
    overflow-y: auto;
  }

  /* Arabic font support */
  :global(html[lang="ar"] body) {
    font-family: "Cairo", "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  }

  .page {
    width: 100%;
    min-height: 100vh;
    display: flex;
    gap: 48px;
    background: #ebebeb;
    padding-left: 220px;
    padding-right: 32px;
    box-sizing: border-box;
    overflow-y: auto;
  }

  .settings-shell {
    flex: 1;
    min-width: 0;
    display: flex;
    flex-direction: column;
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
    margin: 0 0 2px 0;
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

  /* Icon Animations */
  .icon-animated {
    animation: iconFloat 3s ease-in-out infinite;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  }

  @keyframes iconFloat {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-2px); }
  }

  .card:hover .icon-animated {
    animation: iconBounce 0.6s ease-in-out;
    transform: scale(1.1);
  }

  @keyframes iconBounce {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.15); }
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
    background: conic-gradient(var(--brand) calc(var(--p, 0) * 360deg), var(--track-rest) 0);
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

  /* Modal Styles */
  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    backdrop-filter: blur(4px);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 10000;
    animation: fadeIn 0.2s ease-out;
  }

  @keyframes fadeIn {
    from {
      opacity: 0;
    }
    to {
      opacity: 1;
    }
  }

  .modal-content {
    background: white;
    border-radius: 20px;
    width: 90%;
    max-width: 450px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
    animation: modalSlide 0.3s ease-out;
    overflow: hidden;
    transition: transform 0.3s ease-out;
  }

  .modal-content.keyboard-visible {
    transform: translateY(-40vh);
    animation: modalSlideUp 0.3s ease-out;
  }

  @keyframes modalSlideUp {
    from {
      transform: translateY(0);
    }
    to {
      transform: translateY(-40vh);
    }
  }

  @keyframes modalSlide {
    from {
      opacity: 0;
      transform: translateY(-20px) scale(0.95);
    }
    to {
      opacity: 1;
      transform: translateY(0) scale(1);
    }
  }

  .modal-header {
    padding: 24px 24px 16px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid #E0E0E0;
  }

  .modal-header h2 {
    margin: 0;
    font-size: 1.5rem;
    font-weight: 700;
    color: #212121;
  }

  .close-btn {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    border: none;
    background: #F5F5F5;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s ease;
    color: #757575;
  }

  .close-btn:hover {
    background: #EEEEEE;
    color: #424242;
    transform: rotate(90deg);
  }

  .modal-body {
    padding: 24px;
  }

  .modal-description {
    margin: 0 0 20px 0;
    color: #616161;
    font-size: 0.95rem;
    line-height: 1.5;
  }

  .input-group {
    position: relative;
    display: flex;
    align-items: center;
  }

  .input-icon {
    position: absolute;
    left: 16px;
    color: #9E9E9E;
    pointer-events: none;
  }

  .password-input-hidden {
    position: absolute;
    opacity: 0;
    pointer-events: none;
  }

  .password-display {
    width: 100%;
    padding: 14px 16px 14px 48px;
    border: 2px solid #E0E0E0;
    border-radius: 12px;
    font-size: 1.5rem;
    font-weight: 500;
    background: #FAFAFA;
    cursor: pointer;
    min-height: 52px;
    display: flex;
    align-items: center;
    letter-spacing: 4px;
    color: #212121;
    transition: all 0.2s ease;
  }

  .password-display:hover {
    border-color: var(--brand);
    background: white;
    box-shadow: 0 0 0 3px rgba(229, 72, 23, 0.1);
  }

  .password-display.error {
    border-color: #F44336;
    background: #FFEBEE;
    animation: shake 0.3s ease-in-out;
  }

  .password-display.error:hover {
    box-shadow: 0 0 0 3px rgba(244, 67, 54, 0.1);
  }

  .placeholder-text {
    font-size: 0.95rem;
    color: #9E9E9E;
    letter-spacing: normal;
    font-weight: 400;
  }

  .input-group:has(.password-display) {
    position: relative;
  }

  .error-message {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-top: 12px;
    padding: 12px;
    background: #FFEBEE;
    border-radius: 8px;
    color: #D32F2F;
    font-size: 0.9rem;
    font-weight: 500;
    animation: shake 0.3s ease-in-out;
  }

  @keyframes shake {
    0%, 100% {
      transform: translateX(0);
    }
    25% {
      transform: translateX(-8px);
    }
    75% {
      transform: translateX(8px);
    }
  }

  .modal-footer {
    padding: 16px 24px 24px;
    display: flex;
    gap: 12px;
    justify-content: flex-end;
  }

  .btn-cancel,
  .btn-submit {
    padding: 12px 28px;
    border-radius: 10px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
    border: none;
  }

  .btn-cancel {
    background: #F5F5F5;
    color: #616161;
  }

  .btn-cancel:hover {
    background: #EEEEEE;
    color: #424242;
  }

  .btn-submit {
    background: linear-gradient(135deg, var(--brand) 0%, #F4511E 100%);
    color: white;
    box-shadow: 0 4px 12px rgba(229, 72, 23, 0.3);
  }

  .btn-submit:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(229, 72, 23, 0.4);
  }

  .btn-submit:active {
    transform: translateY(0);
  }

  /* Virtual Keyboard Overlay */
  .keyboard-overlay {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    z-index: 10001;
    animation: slideUpKeyboard 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  }

  @keyframes slideUpKeyboard {
    from {
      transform: translateY(100%);
      opacity: 0;
    }
    to {
      transform: translateY(0);
      opacity: 1;
    }
  }

  .virtual-keyboard {
    background: transparent;
    padding: 16px;
  }

  .keyboard-body {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .keyboard-row {
    display: flex;
    justify-content: center;
    gap: 8px;
  }

  .key {
    flex: 1;
    max-width: 50px;
    height: 45px;
    border: none;
    border-radius: 10px;
    background: linear-gradient(135deg, #FFFFFF 0%, #FFE0B2 100%);
    font-size: 1rem;
    font-weight: 800;
    color: #E64A19;
    cursor: pointer;
    transition: all 0.15s ease;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15),
                0 2px 4px rgba(0, 0, 0, 0.1);
    display: flex;
    align-items: center;
    justify-content: center;
    user-select: none;
    -webkit-user-select: none;
    -webkit-tap-highlight-color: transparent;
    position: relative;
    overflow: hidden;
  }

  .key:hover {
    background: linear-gradient(135deg, #FFF3E0 0%, #FFCC80 100%);
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2),
                0 0 0 3px rgba(255, 152, 0, 0.2);
    transform: translateY(-2px);
  }

  .key:active {
    transform: translateY(0) scale(0.95);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    background: linear-gradient(135deg, #FFCC80 0%, #FFB74D 100%);
  }

  /* Key press animation */
  .key-pressed {
    animation: keyPop 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  }

  @keyframes keyPop {
    0% {
      transform: scale(1);
    }
    50% {
      transform: scale(1.15) rotate(2deg);
    }
    100% {
      transform: scale(1);
    }
  }

  /* Ripple effect */
  .ripple {
    position: absolute;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.6);
    width: 10px;
    height: 10px;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    animation: rippleEffect 0.6s ease-out;
    pointer-events: none;
  }

  @keyframes rippleEffect {
    0% {
      width: 10px;
      height: 10px;
      opacity: 1;
    }
    100% {
      width: 80px;
      height: 80px;
      opacity: 0;
    }
  }

  .key-backspace {
    background: linear-gradient(135deg, #E64A19 0%, #D84315 100%);
    color: white;
  }

  .key-backspace .ripple {
    background: rgba(255, 255, 255, 0.5);
  }

  .key-backspace:hover {
    background: linear-gradient(135deg, #F4511E 0%, #E64A19 100%);
    box-shadow: 0 6px 16px rgba(230, 74, 25, 0.3),
                0 0 0 3px rgba(230, 74, 25, 0.2);
  }

  .key-backspace:active {
    background: linear-gradient(135deg, #D84315 0%, #BF360C 100%);
  }

  .key-clear {
    flex: 2;
    max-width: 110px;
    background: linear-gradient(135deg, #FF6F00 0%, #E65100 100%);
    color: white;
    font-size: 0.95rem;
    font-weight: 800;
  }

  .key-clear .ripple {
    background: rgba(255, 255, 255, 0.5);
  }

  .key-backspace svg {
    width: 20px;
    height: 20px;
  }

  .key-clear:hover {
    background: linear-gradient(135deg, #FF8F00 0%, #FF6F00 100%);
    box-shadow: 0 6px 16px rgba(255, 111, 0, 0.3),
                0 0 0 3px rgba(255, 111, 0, 0.2);
  }

  .key-clear:active {
    background: linear-gradient(135deg, #E65100 0%, #BF360C 100%);
  }

  /* Modal positioning when keyboard is visible */
  .modal-content.keyboard-visible {
    transform: translateY(-25vh);
  }

  @keyframes modalSlideUp {
    from {
      transform: translateY(0);
    }
    to {
      transform: translateY(-25vh);
    }
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

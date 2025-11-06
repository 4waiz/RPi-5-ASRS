<script lang="ts">
  import SideBar from "../lib/side-bar.svelte";
  import arrowBackIcon from '../assets/settingPage/arrow-1.svg';
  import languageIcon from '../assets/settingPage/frame6.svg';
  import brightnessIcon from '../assets/settingPage/frame3.svg';
  import networkIcon from '../assets/settingPage/frame4.svg';
  import padlockIcon from '../assets/settingPage/frame7.svg';
  import revealIcon from '../assets/settingPage/frame1.svg';
  import logsPadlockIcon from '../assets/settingPage/frame8.svg';
  import logsFilterIcon from '../assets/settingPage/frame.svg';
  import exportIcon from '../assets/settingPage/frame2.svg';
  import checkIcon from '../assets/settingPage/check.svg';
  import viewIcon from '../assets/settingPage/arrow-6.svg';
  import sliderThumb from '../assets/settingPage/slider.svg';
    import { myVariable } from "../store";
    import Home from "./Home.svelte";

  $effect(() => {
    if (typeof window === 'undefined') return;

    const handleWheel = (event: WheelEvent) => {
      if (event.ctrlKey || event.metaKey) {
        event.preventDefault();
      }
    };

    const handleKeyDown = (event: KeyboardEvent) => {
      if ((event.ctrlKey || event.metaKey) && ['+', '-', '=', '_', '0'].includes(event.key)) {
        event.preventDefault();
      }
    };

    window.addEventListener('wheel', handleWheel, { passive: false });
    window.addEventListener('keydown', handleKeyDown);

    return () => {
      window.removeEventListener('wheel', handleWheel);
      window.removeEventListener('keydown', handleKeyDown);
    };
  });

  // Demo values - wire to your data later
  const asrsId = $state('ASRS-2025-001');
  const runtime = $state('00:08:20');
  const timestamp = $state('11/03/2025, 06:38:08');
  let language = $state<'en' | 'ar'>('en');
  let brightness = $state(60); // percent
  let activeLogTab = $state<'all' | 'error' | 'operation'>('all');

  // Backup timestamps (simulate persistence)
  let storeTimestamp = $state('- -');
  let restoreTimestamp = $state('- -');

  // Hold-to-activate logic (2 seconds)
  const HOLD_MS = 2000;
  let storeTimer: ReturnType<typeof setInterval> | null = null;
  let restoreTimer: ReturnType<typeof setInterval> | null = null;
  let storeProgress = $state(0);    // 0..1
  let restoreProgress = $state(0);  // 0..1

  function nowString() {
    return new Date().toLocaleString();
  }

  function startHold(kind: 'store' | 'restore') {
    cancelHold(kind); // reset
    const t0 = Date.now();
    const tick = () => {
      const p = Math.min(1, (Date.now() - t0) / HOLD_MS);
      if (kind === 'store') storeProgress = p; else restoreProgress = p;
      if (p >= 1) {
        cancelHold(kind);
        if (kind === 'store') {
          storeTimestamp = nowString();
        } else {
          restoreTimestamp = nowString();
        }
      }
    };
    const id = setInterval(tick, 16);
    if (kind === 'store') storeTimer = id; else restoreTimer = id;
  }

  function cancelHold(kind: 'store' | 'restore') {
    if (kind === 'store') {
      if (storeTimer) clearInterval(storeTimer);
      storeTimer = null;
      storeProgress = 0;
    } else {
      if (restoreTimer) clearInterval(restoreTimer);
      restoreTimer = null;
      restoreProgress = 0;
    }
  }

  // Build a colored track like your Figma rectangles
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
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link
    rel="stylesheet"
    href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&family=Noto+Sans+Arabic:wght@400;600&display=swap"
  />
</svelte:head>

<!-- Responsive wrapper: centers up to 1024px, breathes on small screens -->
<div class="page">
  <!-- Header -->
  <div class="topbar">
    <button class="iconbtn pressable" aria-label="Back" onclick={() => myVariable.set(Home)}>
      <img class="icon" src={arrowBackIcon} alt="Back" width="24" height="24" />
    </button>

    <div class="titleblock">
      <h1 class="h1">System Setting</h1>
      <div class="meta muted">
        <span class="strong">ASRS ID:</span>&nbsp;{asrsId}&nbsp;&nbsp;·&nbsp;&nbsp;
        <span class="strong">Runtime:</span>&nbsp;{runtime}&nbsp;&nbsp;·&nbsp;&nbsp;
        <span class="strong">Timestamp:</span>&nbsp;{timestamp}
      </div>
    </div>
  </div>

  <hr class="rule" />

  <!-- Main grid -->
  <div class="grid">
    <!-- Language -->
    <section class="card card--language">
      <div class="card-head">
        <img class="icon" src={languageIcon} alt="Language" width="24" height="24" />
        <h2 class="h2">Language</h2>
      </div>

      <div class="row gap lang-toggle" class:lang-en={language==='en'} class:lang-ar={language==='ar'}>
        <button type="button" class="pill pressable {language==='en' ? 'pill--active' : ''}" aria-pressed={language==='en'} onclick={() => (language = 'en')}>
          <span class="pill-dot">
            <img src={checkIcon} alt="" width="14" height="14" />
          </span>
          English
        </button>

        <button
          type="button"
          class="pill pressable {language==='ar' ? 'pill--active' : ''}"
          aria-pressed={language==='ar'}
          onclick={() => (language = 'ar')}
        >
          <span class="pill-dot">
            <img src={checkIcon} alt="" width="14" height="14" />
          </span>
          عربي / Arabic
        </button>
      </div>
    </section>

    <!-- Brightness -->
    <section class="card card--brightness">
      <div class="card-head">
        <img class="icon" src={brightnessIcon} alt="Brightness" width="24" height="24" />
        <h2 class="h2">Display Brightness</h2>
      </div>

      <div class="slider-wrap">
        <!-- Track color via inline style, knob styled in CSS to match Figma -->
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
    <section class="card card--network">
      <div class="card-head">
        <img class="icon" src={networkIcon} alt="Network" width="24" height="24" />
        <h2 class="h2">Network Configuration</h2>
        <img class="icon ml8" src={padlockIcon} alt="Locked" width="24" height="24" />
      </div>

      <div class="label">Machine IPs:</div>

      <div class="iprow">
        <input class="ip" value="*** ***** *" readonly />
        <button class="iconbtn pressable" title="Reveal">
          <img class="icon" src={revealIcon} alt="Reveal" width="24" height="24" />
        </button>
      </div>

      <div class="iprow">
        <input class="ip" value="*** ***** *" readonly />
        <button class="iconbtn pressable" title="Reveal">
          <img class="icon" src={revealIcon} alt="Reveal" width="24" height="24" />
        </button>
      </div>
    </section>

    <!-- ===== BACKUP (new, right column) ===== -->
    <section class="card card--backup">
      <div class="card-head">
        <!-- Save / backup icon -->
        <svg class="icon" viewBox="0 0 24 24" aria-hidden="true">
          <!-- floppy disk -->
          <path d="M5 3h11l5 5v13a0 0 0 0 1 0 0H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2Z" fill="none" stroke="black" stroke-width="2"/>
          <rect x="7" y="3" width="8" height="5" fill="none" stroke="black" stroke-width="2"/>
          <rect x="7" y="13" width="10" height="6" rx="1" fill="none" stroke="black" stroke-width="2"/>
        </svg>
        <h2 class="h2">Backup</h2>
      </div>

      <p class="muted small">Press and hold for at least 2 seconds to save/restore parameters.</p>

      <!-- Store parameters -->
      <div class="backup-row">
        <button
          class="holdbtn pressable"
          style={`--p:${storeProgress}`}
          onpointerdown={() => startHold('store')}
          onpointerup={() => cancelHold('store')}
          onpointerleave={() => cancelHold('store')}
          onpointercancel={() => cancelHold('store')}
        >
          <span class="ring" aria-hidden="true"></span>
          <svg width="20" height="20" viewBox="0 0 24 24" aria-hidden="true">
            <!-- save -->
            <path d="M5 3h11l5 5v13H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2Z" fill="none" stroke="black" stroke-width="2"/>
            <rect x="7" y="3" width="8" height="5" fill="none" stroke="black" stroke-width="2"/>
          </svg>
          <span>Store parameters</span>
        </button>

        <input class="stamp" value={storeTimestamp} readonly />
      </div>

      <!-- Restore parameters -->
      <div class="backup-row">
        <button
          class="holdbtn pressable"
          style={`--p:${restoreProgress}`}
          onpointerdown={() => startHold('restore')}
          onpointerup={() => cancelHold('restore')}
          onpointerleave={() => cancelHold('restore')}
          onpointercancel={() => cancelHold('restore')}
        >
          <span class="ring" aria-hidden="true"></span>
          <svg width="20" height="20" viewBox="0 0 24 24" aria-hidden="true">
            <!-- restore (arrow into tray) -->
            <path d="M12 3v10M7 8l5 5 5-5" fill="none" stroke="black" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M5 21h14" fill="none" stroke="black" stroke-width="2" stroke-linecap="round"/>
          </svg>
          <span>Restore parameters</span>
        </button>

        <input class="stamp" value={restoreTimestamp} readonly />
      </div>
    </section>

    <!-- Logs -->
    <section class="card card--logs">
      <div class="card-head">
        <img class="icon ml8" src={logsPadlockIcon} alt="Locked" width="24" height="24" />
        <h2 class="h2">Machine Logs</h2>
        <img class="icon ml8" src={logsFilterIcon} alt="Locked" width="24" height="24" />
      </div>

      <div class="row gap">
        <button
          type="button"
          class="pill pressable {activeLogTab === 'all' ? 'pill--active' : ''}"
          aria-pressed={activeLogTab === 'all'}
          onclick={() => (activeLogTab = 'all')}
        >
          All logs
        </button>
        <button
          type="button"
          class="pill pressable {activeLogTab === 'error' ? 'pill--active' : ''}"
          aria-pressed={activeLogTab === 'error'}
          onclick={() => (activeLogTab = 'error')}
        >
          Error logs
        </button>
        <button
          type="button"
          class="pill pressable {activeLogTab === 'operation' ? 'pill--active' : ''}"
          aria-pressed={activeLogTab === 'operation'}
          onclick={() => (activeLogTab = 'operation')}
        >
          Operation logs
        </button>
      </div>

      <div class="row gap mt12">
        <button class="btn pressable">
          <img class="icon" src={exportIcon} alt="Export" width="24" height="24" />
          <span>Export</span>
        </button>

        <button class="btn pressable">
          <span>View</span>
          <img class="icon" src={viewIcon} alt="View" width="24" height="24" />
        </button>
      </div>
    </section>
  </div>
</div>

<style>
  :global(html, body){ height:100%; margin:0; padding:0; }
  :global(*), :global(*::before), :global(*::after){ box-sizing:border-box; }

  :global(:root){
    --ink:#111;
    --muted:rgba(0,0,0,.68);
    --brand:#E54817;
    --track-rest:rgba(0,0,0,.30);
    --border:rgba(0,0,0,.08);
    --border-strong:rgba(0,0,0,.30);
    --ring:rgba(229,72,23,.35);
    --ui-scale:1.1;
  }

  :global(body){
    font:16px/1.35 "Inter", system-ui, -apple-system, Segoe UI, Roboto, "Helvetica Neue", Arial, "Noto Sans", "Liberation Sans", sans-serif;
    color:var(--ink);
    background:#fff;
    overflow:hidden;
  }

  :global(button){
    cursor:pointer;
    font:inherit;
    color:inherit;
    background:#fff;
    border:1px solid transparent;
  }

  :global(input){
    font:inherit;
  }

  /* Responsive canvas */
  .page{
    width: calc(100vw / var(--ui-scale));
    margin: 0;
    padding: 8px 16px;
    background:#fff;
    box-sizing:border-box;
    height: calc(100vh / var(--ui-scale));
    display:flex;
    flex-direction:column;
    gap:8px;
    transform: scale(var(--ui-scale));
    transform-origin: top left;
    overflow:hidden;
  }
  @media (max-width: 900px){
    .page{
      transform:none;
      width: 100%;
      height:auto;
      padding: clamp(16px, 4vw, 24px);
      gap:16px;
    }
  }

  /* Header */
  .topbar{ display:flex; align-items:flex-start; gap:12px; }
  .iconbtn{
    width:40px; height:40px; display:grid; place-items:center;
    border:1px solid var(--muted); border-radius:8px; background:#fff;
  }
    .titleblock{ flex:1; }
    .meta{ margin-top:10px; font-size:15px; }
    .h1{ font-size: clamp(30px, 3vw, 36px); line-height:1.1; margin:0; }
    .h2{ font-size: clamp(19px, 2.2vw, 24px); margin:0; }
    .muted{ color:var(--muted); }
    .strong{ font-weight:700; }
    .icon{ width:24px; height:24px; display:inline-block; }
    .pressable{
      transition:transform .12s ease, box-shadow .12s ease, border-color .12s ease, background-color .12s ease, color .12s ease;
    }
    .pressable:hover{
      box-shadow:0 1px 2px rgba(0,0,0,.06), 0 4px 12px rgba(0,0,0,.08);
    }
    .pressable:active{ transform:translateY(1px) scale(.98); }
    .pressable:focus-visible{ outline:2px solid var(--ring); outline-offset:2px; }

  .rule{
    margin: 10px 0 8px;
    height:1px; border:none; background:var(--border);
  }

  /* Grid: 1 column on small, 2 columns on >= 900px */
  .grid{
    display:grid;
    grid-template-columns: 1fr;
    gap: 10px;
    flex:1 1 auto;
    min-height:0;
  }
  @media (min-width: 900px){
    .grid{
      grid-template-columns: repeat(2, minmax(0, 1fr));
      column-gap: 14px;
      row-gap: 10px;
      
      grid-template-areas:
        "language brightness"
        "network backup"
        "logs backup";
      align-content:stretch;
    }
    .grid > .card{ height:auto; }
    .card--language{ grid-area: language; }
    .card--brightness{ grid-area: brightness; }
    .card--network{ grid-area: network; }
    .card--backup{ grid-area: backup; }
    .card--logs{ grid-area: logs; }
  }

  /* Cards */
  .card{
    display:flex;
    flex-direction:column;
    justify-content:space-between;
    padding-bottom:0;
    gap:6px;
  }
  .card-head{
    display:flex; align-items:center; gap:8px; margin-bottom:2px;
  }
  .ml8{ margin-left:8px; }
  .small{ font-size:12.5px; margin: 0 0 12px; }

  /* Pills */
  .row{ display:flex; align-items:center; flex-wrap: wrap; }
  .gap{ gap:12px; }
  .mt12{ margin-top:12px; }

  .pill{
    height:40px; padding:0 18px;
    border-radius:24px;
    border:1px solid var(--muted);
    color:var(--muted); background:#fff;
    font-size:15px; font-weight:500;
    display:inline-flex; align-items:center; gap:9px;
  }
  .pill--active{
    border-color:var(--brand);
    color:var(--brand);
    font-weight:500;
  }
  .lang-toggle .pill-dot{ display:none; }
  .lang-toggle .pill.pill--active .pill-dot{ display:grid; }
  .lang-toggle.lang-en .pill:first-child,
  .lang-toggle.lang-ar .pill:last-child{
    border-color:var(--brand);
    color:var(--brand);
    font-weight:500;
  }
  .lang-toggle.lang-en .pill:first-child .pill-dot,
  .lang-toggle.lang-ar .pill:last-child .pill-dot{ display:grid; }
  .pill-dot{
    width:20px; height:20px; border-radius:999px;
    display:grid; place-items:center;
    background:var(--brand);
    border:1px solid #fff;
  }

  /* Slider area */
  .slider-wrap{ width: 100%; max-width: 320px; height: 32px; display:flex; align-items:center; }

  /* Track via background gradient on the input element itself */
  .slider{
    -webkit-appearance:none; appearance:none;
    width: 100%;
    height: 12px;
    border-radius: 140px;
    --slider-thumb: none;
    outline: none;
  }

/* WebKit (Chrome / Edge / Safari) */
.slider::-webkit-slider-thumb{
  -webkit-appearance:none; appearance:none;

  /* same physical size as your SVG artboard */
  width:34px; 
  height:29px;

  /* center the 28px thumb on a 10px track: (28-10)/2 = 9 */
  margin-top:-0px;

  /* the SVG IS the thumb */
  background: var(--slider-thumb) center/100% 100% no-repeat transparent !important;
  border:0; 
  border-radius:0; 
  box-shadow:none;                 /* optional: keep it clean since SVG has stroke */
  /* optional subtle shadow if you still want depth:
     filter: drop-shadow(0 1px 0 rgba(0,0,0,.10)) drop-shadow(0 2px 6px rgba(0,0,0,.12));
  */

  transition: transform .12s ease;
}
.slider:active::-webkit-slider-thumb{ transform: scale(0.96); }

/* Firefox */
.slider::-moz-range-thumb{
  width:34px; 
  height:28px;
  background: var(--slider-thumb) center/100% 100% no-repeat transparent !important;
  border:0; 
  border-radius:0; 
  box-shadow:none;
  /* optional: filter: drop-shadow(...) like above */
  transition: transform .12s ease;
}
.slider:active::-moz-range-thumb{ transform: scale(0.96); }
  .label{ font-size:16px; font-weight:600; line-height:22px; margin:4px 0 8px; }
  .iprow{ display:flex; align-items:center; gap:8px; margin-bottom:8px; }
  .ip{
    flex:1; height:40px; border-radius:8px;
    border:1px solid var(--border-strong); background:#fff;
    color:var(--muted); padding:0 12px;
    font-size:14px;
  }

  /* Buttons */
  .btn{
    height:44px; padding:0 22px;
    border-radius:8px; border:1px solid var(--border-strong);
    background:#fff; display:inline-flex; align-items:center; gap:10px;
    font-size:14.5px; font-weight:600;
  }

  /* ===== BACKUP styles ===== */
  .backup-row{
    display:flex; gap:10px; align-items:center; margin-top:6px; flex-wrap:wrap;
  }
  .holdbtn{
    position:relative;
    height:48px; padding:0 16px;
    border:1px solid var(--border-strong); border-radius:8px;
    background:#fff;
    display:inline-flex; align-items:center; gap:10px;
    font-size:14.5px;
  }
  /* small circular progress indicator */
  .holdbtn .ring{
    width:18px; height:18px; border-radius:999px; flex:0 0 18px;
    background: conic-gradient(var(--brand) calc(var(--p,0)*1*1turn), #eee 0);
    transition: background .05s linear;
  }
  .stamp{
    flex:1 1 280px;
    height:40px;
    border-radius:10px;
    border:1px solid var(--border-strong);
    padding:0 12px;
    color:var(--muted);
    font-size:14px;
    background:#fff;
  }
</style>

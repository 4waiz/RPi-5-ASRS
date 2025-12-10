<script>
  import { myVariable, currentMode } from '../../store.js';
  import Home from '../../pages/Home.svelte';
  import Alerts from '../../pages/Alerts.svelte';
  import AIAssistant from '../../pages/AIAssistant.svelte';
  import Analytics from '../../pages/Analytics.svelte';
  import Setting from '../../pages/Setting.svelte';
  import EdgeLogo from '../../assets/Icons/Edge_logo.png?url';
  import { t } from '../../lib/i18n';
  import PasswordModal from './PasswordModal.svelte';

  // Password hashing
  import { verifyPassword } from '../../utils/passwordHash';
  import { credentials } from '../../config/credentials';

  let { AlertsNum = 0, ActivePage = "Home" } = $props();

  let dropdownOpen = $state(false);
  let showPasswordModal = $state(false);
  let modalType = $state(''); // 'editMode' or 'settings'
  let audioCtx = null;
  let passwordModalRef;

  // Translate mode text based on current mode
  let translatedMode = $derived(
    $currentMode === 'LIVE Mode' ? $t('sidebar.liveMode') :
    $currentMode === 'Edit Mode' ? $t('sidebar.editMode') :
    $currentMode
  );

  const navigateTo = (page) => {
    switch(page) {
      case 'Home':
        myVariable.set(Home);
        break;
      case 'Alerts':
        myVariable.set(Alerts);
        break;
      case 'AIAssistant':
        myVariable.set(AIAssistant);
        break;
      case 'Analytics':
        myVariable.set(Analytics);
        break;
      case 'Settings':
        // If we're already on Settings, don't re-open the password modal
        if (ActivePage === 'Settings') return;
        // Show password modal for Settings
        showPasswordModal = true;
        modalType = 'settings';
        password = '';
        passwordError = '';
        break;
    }
  };

  const toggleDropdown = () => {
    dropdownOpen = !dropdownOpen;
  };

  const selectEditMode = () => {
    dropdownOpen = false;
    showPasswordModal = true;
    modalType = 'editMode';
  };

  const closePasswordModal = () => {
    showPasswordModal = false;
    modalType = '';
  };

  const handlePasswordSubmit = async (event) => {
    const password = event.detail.password;

    // Verify password against stored hash
    console.log('🔑 Sidebar password check:', password);
    console.log('📋 Against hash:', credentials.ipRevealPasswordHash);

    const isValid = await verifyPassword(password, credentials.ipRevealPasswordHash);
    console.log('✅ Valid:', isValid);

    if (isValid) {
      if (modalType === 'editMode') {
        currentMode.set('Edit Mode');
      } else if (modalType === 'settings') {
        myVariable.set(Setting);
      }
      closePasswordModal();
    } else {
      playErrorSound();
      // Set error based on modal type
      if (modalType === 'editMode') {
        passwordModalRef?.setError($t('sidebar.editPasswordModal.error'));
      } else if (modalType === 'settings') {
        passwordModalRef?.setError($t('sidebar.settingsPasswordModal.error'));
      }
    }
  };

  const selectLiveMode = () => {
    currentMode.set('LIVE Mode');
    dropdownOpen = false;
  };

  // Close dropdown when clicking outside
  const handleClickOutside = (event) => {
    if (dropdownOpen && !event.target.closest('.mode-selector')) {
      dropdownOpen = false;
    }
  };

  const getAudioContext = () => {
    if (typeof window === 'undefined') return null;
    const Ctx = window.AudioContext || window.webkitAudioContext;
    if (!Ctx) return null;
    if (!audioCtx) {
      audioCtx = new Ctx();
    }
    if (audioCtx.state === 'suspended') {
      audioCtx.resume().catch(() => {});
    }
    return audioCtx;
  };

  const playErrorSound = () => {
    const ctx = getAudioContext();
    if (!ctx) return;
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = 'sine';
    const now = ctx.currentTime;
    osc.frequency.setValueAtTime(520, now);
    osc.frequency.exponentialRampToValueAtTime(340, now + 0.18);
    gain.gain.value = 1.0;
    osc.connect(gain).connect(ctx.destination);
    osc.start(now);
    gain.gain.setValueAtTime(gain.gain.value, now);
    gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.28);
    osc.stop(now + 0.3);
  };
</script>

<svelte:window onclick={handleClickOutside} />

<div class="sidebar">
  <div class="logo-section">
    <img src={EdgeLogo} alt="EDGE Logo" class="logo-image" />
  </div>

  <div class="mode-selector-container">
    <button class="mode-selector" onclick={toggleDropdown}>
      <div class="mode-dot" class:edit-mode={$currentMode === 'Edit Mode'}></div>
      <span class="mode-text">{translatedMode}</span>
      <span class="dropdown-arrow" class:open={dropdownOpen}>▼</span>
    </button>

    {#if dropdownOpen}
      <div class="mode-dropdown">
        <button
          class="mode-option"
          class:active={$currentMode === 'LIVE Mode'}
          onclick={selectLiveMode}
        >
          <div class="option-dot live"></div>
          <span>{$t('sidebar.liveMode')}</span>
          {#if $currentMode === 'LIVE Mode'}
            <svg class="check-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <polyline points="20 6 9 17 4 12" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          {/if}
        </button>
        <button
          class="mode-option"
          class:active={$currentMode === 'Edit Mode'}
          onclick={selectEditMode}
        >
          <div class="option-dot edit"></div>
          <span>{$t('sidebar.editMode')}</span>
          {#if $currentMode === 'Edit Mode'}
            <svg class="check-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <polyline points="20 6 9 17 4 12" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          {/if}
        </button>
      </div>
    {/if}
  </div>

  <nav class="nav-menu">
    <div class="nav-item" class:active={ActivePage === "Home"} onclick={() => navigateTo('Home')}>
      <svg class="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/>
      </svg>
      <span>{$t('sidebar.home')}</span>
    </div>

    <div class="nav-item" class:active={ActivePage === "Alerts"} onclick={() => navigateTo('Alerts')}>
      <svg class="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"/>
      </svg>
      <span>{$t('sidebar.alerts')}</span>
      <div class="badge-group">
        {#if AlertsNum > 0}
          <div class="badge alert">{AlertsNum}</div>
        {/if}
      </div>
    </div>

    <div class="nav-item" class:active={ActivePage === "AIAssistant"} onclick={() => navigateTo('AIAssistant')}>
      <svg class="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/>
      </svg>
      <span>{$t('sidebar.aiAssistant')}</span>
    </div>

    <div class="nav-item" class:active={ActivePage === "Analytics"} onclick={() => navigateTo('Analytics')}>
      <svg class="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
      </svg>
      <span>Analytics</span>
    </div>
  </nav>

  <div class="settings-button" class:active={ActivePage === "Settings"} onclick={() => navigateTo('Settings')}>
    <svg class="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/>
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
    </svg>
    <span>{$t('sidebar.settings')}</span>
  </div>
</div>

<!-- Password Modal -->
<PasswordModal
  bind:this={passwordModalRef}
  show={showPasswordModal}
  title={modalType === 'editMode' ? $t('sidebar.editPasswordModal.title') : $t('sidebar.settingsPasswordModal.title')}
  description={modalType === 'editMode' ? $t('sidebar.editPasswordModal.description') : $t('sidebar.settingsPasswordModal.description')}
  on:submit={handlePasswordSubmit}
  on:cancel={closePasswordModal}
/>

<style>
  .sidebar {
    position: fixed;
    left: 0;
    top: 0;
    width: 220px;
    height: 100vh;
    background: var(--bg-card, white);
    border-right: 2px solid var(--border, #E0E0E0);
    display: flex;
    flex-direction: column;
    z-index: 100;
    transition: background 0.3s ease, border 0.3s ease;
  }

  .logo-section {
    padding: 1.5rem 1rem;
    border-bottom: 2px solid var(--border, #E0E0E0);
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
  }

  .logo-image {
    width: 120px;
    height: auto;
    object-fit: contain;
    transition: filter 0.3s ease;
  }

  :global(html.dark-mode) .logo-image {
    filter: brightness(0) invert(1);
  }

  .station-text {
    font-size: 1.2rem;
    color: var(--secondary, #757575);
    margin-top: 0.5rem;
  }

  .mode-selector-container {
    position: relative;
    margin: 1.5rem 1.25rem;
  }

  .mode-selector {
    width: 100%;
    padding: 0.875rem 1.25rem;
    background: var(--bg-page, #FAFAFA);
    border: 2px solid var(--border, #D0D0D0);
    border-radius: 50px;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    cursor: pointer;
    font-size: 1.05rem;
    white-space: nowrap;
    transition: all 0.2s ease;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  }

  .mode-dot {
    width: 10px;
    height: 10px;
    background: var(--success);
    border-radius: 50%;
    box-shadow: 0 0 8px color-mix(in srgb, var(--success) 60%, transparent);
    animation: pulse 2s ease-in-out infinite;
    flex-shrink: 0;
  }

  .mode-dot.edit-mode {
    background: var(--warning);
    box-shadow: 0 0 8px color-mix(in srgb, var(--warning) 60%, transparent);
  }

  @keyframes pulse {
    0%, 100% {
      opacity: 1;
    }
    50% {
      opacity: 0.6;
    }
  }

  .mode-text {
    flex: 1;
    font-weight: 600;
    color: var(--primary, #212121);
  }

  .dropdown-arrow {
    transition: transform 0.2s ease;
    color: var(--secondary, #757575);
    font-size: 0.8rem;
  }

  .dropdown-arrow.open {
    transform: rotate(180deg);
  }

  /* Dropdown Menu */
  .mode-dropdown {
    position: absolute;
    top: calc(100% + 8px);
    left: 0;
    right: 0;
    background: var(--bg-card, white);
    border-radius: 16px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
    overflow: hidden;
    z-index: 1000;
    animation: dropdownSlide 0.2s ease-out;
    border: 1px solid var(--border, #E0E0E0);
  }

  @keyframes dropdownSlide {
    from {
      opacity: 0;
      transform: translateY(-10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  .mode-option {
    width: 100%;
    padding: 12px 16px;
    background: var(--bg-card, white);
    border: none;
    display: flex;
    align-items: center;
    gap: 12px;
    cursor: pointer;
    transition: background 0.2s ease;
    font-size: 0.95rem;
    color: var(--primary, #424242);
    font-weight: 500;
  }

  .mode-option.active {
    background: var(--brand-light);
    color: var(--brand);
  }

  .option-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    flex-shrink: 0;
  }

  .option-dot.live {
    background: var(--success);
  }

  .option-dot.edit {
    background: var(--warning);
  }

  .check-icon {
    margin-left: auto;
    color: var(--brand);
  }

  .nav-menu {
    flex: 1;
    padding: 1.5rem 0;
  }

  .nav-item {
    padding: 1.25rem 2rem;
    display: flex;
    align-items: center;
    gap: 1.25rem;
    cursor: pointer;
    transition: all 0.2s;
    color: var(--primary, #424242);
    font-weight: 500;
    font-size: 1.1rem;
  }

  .nav-item.active {
    background: var(--brand-light);
    color: var(--brand);
    border-right: 4px solid var(--brand);
  }

  .nav-icon {
    width: 28px;
    height: 28px;
    transition: transform 0.3s ease;
  }

  /* Home icon - Bounce animation when active */
  .nav-item.active:nth-child(1) .nav-icon {
    animation: bounce 0.6s ease-in-out;
  }

  @keyframes bounce {
    0%, 100% {
      transform: translateY(0);
    }
    25% {
      transform: translateY(-8px);
    }
    50% {
      transform: translateY(0);
    }
    75% {
      transform: translateY(-4px);
    }
  }

  /* Alerts icon - Bell ring animation when active */
  .nav-item.active:nth-child(2) .nav-icon {
    animation: ring 0.6s ease-in-out;
  }

  @keyframes ring {
    0%, 100% {
      transform: rotate(0deg);
    }
    10%, 30%, 50%, 70% {
      transform: rotate(-15deg);
    }
    20%, 40%, 60% {
      transform: rotate(15deg);
    }
    80% {
      transform: rotate(-8deg);
    }
    90% {
      transform: rotate(8deg);
    }
  }

  /* AI Assistant icon - Glow pulse animation when active */
  .nav-item.active:nth-child(3) .nav-icon {
    animation: glow 1.5s ease-in-out infinite;
    filter: drop-shadow(0 0 8px rgba(255, 87, 34, 0.6));
  }

  @keyframes glow {
    0%, 100% {
      filter: drop-shadow(0 0 4px rgba(255, 87, 34, 0.4));
      transform: scale(1);
    }
    50% {
      filter: drop-shadow(0 0 12px rgba(255, 87, 34, 0.8));
      transform: scale(1.1);
    }
  }

  /* Settings icon - Gentle rotation when active */
  .settings-button.active .nav-icon {
    animation: rotate 0.8s ease-in-out;
  }

  @keyframes rotate {
    0% {
      transform: rotate(0deg);
    }
    100% {
      transform: rotate(180deg);
    }
  }

  .badge-group {
    display: flex;
    gap: 0.75rem;
    margin-left: auto;
  }

  .badge {
    min-width: 32px;
    height: 32px;
    border-radius: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.95rem;
    font-weight: 700;
    padding: 0 0.75rem;
  }

  .badge.alert {
    background: var(--surface-critical, rgba(211, 47, 47, 0.12));
    color: var(--danger);
    animation: alertPulse 2s ease-in-out infinite;
    box-shadow: 0 0 0 0 color-mix(in srgb, var(--danger) 70%, transparent);
  }

  @keyframes alertPulse {
    0%, 100% {
      background: var(--surface-critical, rgba(211, 47, 47, 0.12));
      color: var(--danger);
      box-shadow: 0 0 0 0 color-mix(in srgb, var(--danger) 70%, transparent);
      transform: scale(1);
    }
    50% {
      background: var(--danger);
      color: var(--on-brand, #ffffff);
      box-shadow: 0 0 0 8px transparent;
      transform: scale(1.1);
    }
  }

  .badge.warning {
    background: var(--surface-warning, rgba(245, 158, 11, 0.12));
    color: var(--warning);
  }

  .settings-button {
    padding: 1.25rem 2rem;
    border-top: 2px solid var(--border, #E0E0E0);
    display: flex;
    align-items: center;
    gap: 1.25rem;
    cursor: pointer;
    transition: all 0.2s;
    color: var(--primary, #424242);
    font-weight: 500;
    font-size: 1.1rem;
  }

  .settings-button.active {
    background: var(--brand-light);
    color: var(--brand);
    border-right: 4px solid var(--brand);
  }
</style>

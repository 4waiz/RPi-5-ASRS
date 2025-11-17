<script>
  import { myVariable } from '../../store.js';
  import Home from '../../pages/Home.svelte';
  import Alerts from '../../pages/Alerts.svelte';
  import AIAssistant from '../../pages/AIAssistant.svelte';
  import Setting from '../../pages/Setting.svelte';
  import EdgeLogo from '../../assets/Icons/Edge_logo.png?url';

  let { AlertsNum = 0, ActivePage = "Home" } = $props();

  let dropdownOpen = $state(false);
  let showPasswordModal = $state(false);
  let password = $state('');
  let passwordError = $state('');
  let currentMode = $state('LIVE Mode');

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
      case 'Settings':
        myVariable.set(Setting);
        break;
    }
  };

  const toggleDropdown = () => {
    dropdownOpen = !dropdownOpen;
  };

  const selectEditMode = () => {
    dropdownOpen = false;
    showPasswordModal = true;
    password = '';
    passwordError = '';
  };

  const closePasswordModal = () => {
    showPasswordModal = false;
    password = '';
    passwordError = '';
  };

  const handlePasswordSubmit = () => {
    // Change this password to whatever you want
    const CORRECT_PASSWORD = 'changeme';

    if (password === CORRECT_PASSWORD) {
      currentMode = 'Edit Mode';
      closePasswordModal();
    } else {
      passwordError = 'Incorrect password. Please try again.';
      password = '';
    }
  };

  const selectLiveMode = () => {
    currentMode = 'LIVE Mode';
    dropdownOpen = false;
  };

  // Close dropdown when clicking outside
  const handleClickOutside = (event) => {
    if (dropdownOpen && !event.target.closest('.mode-selector')) {
      dropdownOpen = false;
    }
  };
</script>

<svelte:window onclick={handleClickOutside} />

<div class="sidebar">
  <div class="logo-section">
    <img src={EdgeLogo} alt="EDGE Logo" class="logo-image" />
  </div>

  <div class="mode-selector-container">
    <button class="mode-selector" onclick={toggleDropdown}>
      <div class="mode-dot" class:edit-mode={currentMode === 'Edit Mode'}></div>
      <span class="mode-text">{currentMode}</span>
      <span class="dropdown-arrow" class:open={dropdownOpen}>▼</span>
    </button>

    {#if dropdownOpen}
      <div class="mode-dropdown">
        <button
          class="mode-option"
          class:active={currentMode === 'LIVE Mode'}
          onclick={selectLiveMode}
        >
          <div class="option-dot live"></div>
          <span>LIVE Mode</span>
          {#if currentMode === 'LIVE Mode'}
            <svg class="check-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <polyline points="20 6 9 17 4 12" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          {/if}
        </button>
        <button
          class="mode-option"
          class:active={currentMode === 'Edit Mode'}
          onclick={selectEditMode}
        >
          <div class="option-dot edit"></div>
          <span>Edit Mode</span>
          {#if currentMode === 'Edit Mode'}
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
      <span>Home</span>
    </div>

    <div class="nav-item" class:active={ActivePage === "Alerts"} onclick={() => navigateTo('Alerts')}>
      <svg class="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"/>
      </svg>
      <span>Alerts</span>
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
      <span>AI Assistant</span>
    </div>
  </nav>

  <div class="settings-button" class:active={ActivePage === "Settings"} onclick={() => navigateTo('Settings')}>
    <svg class="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/>
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
    </svg>
    <span>Settings</span>
  </div>
</div>

<!-- Password Modal -->
{#if showPasswordModal}
  <div class="modal-overlay" onclick={closePasswordModal}>
    <div class="modal-content" onclick={(e) => e.stopPropagation()}>
      <div class="modal-header">
        <h2>Enter Password</h2>
        <button class="close-btn" onclick={closePasswordModal}>
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <line x1="18" y1="6" x2="6" y2="18" stroke-width="2" stroke-linecap="round"/>
            <line x1="6" y1="6" x2="18" y2="18" stroke-width="2" stroke-linecap="round"/>
          </svg>
        </button>
      </div>

      <div class="modal-body">
        <p class="modal-description">Please enter the password to switch to Edit Mode</p>

        <div class="input-group">
          <svg class="input-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <rect x="3" y="11" width="18" height="11" rx="2" ry="2" stroke-width="2"/>
            <path d="M7 11V7a5 5 0 0110 0v4" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <input
            type="password"
            class="password-input"
            class:error={passwordError}
            bind:value={password}
            placeholder="Enter password"
            onkeydown={(e) => e.key === 'Enter' && handlePasswordSubmit()}
            autofocus
          />
        </div>

        {#if passwordError}
          <div class="error-message">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <circle cx="12" cy="12" r="10" stroke-width="2"/>
              <line x1="12" y1="8" x2="12" y2="12" stroke-width="2" stroke-linecap="round"/>
              <line x1="12" y1="16" x2="12.01" y2="16" stroke-width="2" stroke-linecap="round"/>
            </svg>
            {passwordError}
          </div>
        {/if}
      </div>

      <div class="modal-footer">
        <button class="btn-cancel" onclick={closePasswordModal}>Cancel</button>
        <button class="btn-submit" onclick={handlePasswordSubmit}>Submit</button>
      </div>
    </div>
  </div>
{/if}

<style>
  .sidebar {
    position: fixed;
    left: 0;
    top: 0;
    width: 220px;
    height: 100vh;
    background: white;
    border-right: 2px solid #E0E0E0;
    display: flex;
    flex-direction: column;
    z-index: 100;
  }

  .logo-section {
    padding: 1.5rem 1rem;
    border-bottom: 2px solid #E0E0E0;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
  }

  .logo-image {
    width: 120px;
    height: auto;
    object-fit: contain;
  }

  .station-text {
    font-size: 1.2rem;
    color: #757575;
    margin-top: 0.5rem;
  }

  .mode-selector-container {
    position: relative;
    margin: 1.5rem 1.25rem;
  }

  .mode-selector {
    width: 100%;
    padding: 0.875rem 1.25rem;
    background: #FAFAFA;
    border: 2px solid #D0D0D0;
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

  .mode-selector:hover {
    background: #F5F5F5;
    border-color: #B0B0B0;
    box-shadow: 0 3px 6px rgba(0, 0, 0, 0.08);
  }

  .mode-dot {
    width: 10px;
    height: 10px;
    background: #4CAF50;
    border-radius: 50%;
    box-shadow: 0 0 8px rgba(76, 175, 80, 0.5);
    animation: pulse 2s ease-in-out infinite;
    flex-shrink: 0;
  }

  .mode-dot.edit-mode {
    background: #FF9800;
    box-shadow: 0 0 8px rgba(255, 152, 0, 0.5);
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
    color: #212121;
  }

  .dropdown-arrow {
    transition: transform 0.2s ease;
    color: #757575;
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
    background: white;
    border-radius: 16px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
    overflow: hidden;
    z-index: 1000;
    animation: dropdownSlide 0.2s ease-out;
    border: 1px solid #E0E0E0;
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
    background: white;
    border: none;
    display: flex;
    align-items: center;
    gap: 12px;
    cursor: pointer;
    transition: background 0.2s ease;
    font-size: 0.95rem;
    color: #424242;
    font-weight: 500;
  }

  .mode-option:hover {
    background: #F5F5F5;
  }

  .mode-option.active {
    background: #FFF3E0;
    color: #FF5722;
  }

  .option-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    flex-shrink: 0;
  }

  .option-dot.live {
    background: #4CAF50;
  }

  .option-dot.edit {
    background: #FF9800;
  }

  .check-icon {
    margin-left: auto;
    color: #FF5722;
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
    max-width: 420px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
    animation: modalSlide 0.3s ease-out;
    overflow: hidden;
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

  .password-input {
    width: 100%;
    padding: 14px 16px 14px 48px;
    border: 2px solid #E0E0E0;
    border-radius: 12px;
    font-size: 1rem;
    font-weight: 500;
    transition: all 0.2s ease;
    outline: none;
    background: #FAFAFA;
  }

  .password-input:focus {
    border-color: #FF5722;
    background: white;
    box-shadow: 0 0 0 3px rgba(255, 87, 34, 0.1);
  }

  .password-input.error {
    border-color: #F44336;
    background: #FFEBEE;
  }

  .password-input.error:focus {
    box-shadow: 0 0 0 3px rgba(244, 67, 54, 0.1);
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
    background: linear-gradient(135deg, #FF5722 0%, #F4511E 100%);
    color: white;
    box-shadow: 0 4px 12px rgba(255, 87, 34, 0.3);
  }

  .btn-submit:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(255, 87, 34, 0.4);
  }

  .btn-submit:active {
    transform: translateY(0);
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
    color: #424242;
    font-weight: 500;
    font-size: 1.1rem;
  }

  .nav-item:hover {
    background: #F5F5F5;
  }

  .nav-item.active {
    background: #FFF3E0;
    color: #FF5722;
    border-right: 4px solid #FF5722;
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

  /* Hover animations for all icons */
  .nav-item:hover .nav-icon,
  .settings-button:hover .nav-icon {
    transform: scale(1.15);
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
    background: #FFEBEE;
    color: #D32F2F;
    animation: alertPulse 2s ease-in-out infinite;
    box-shadow: 0 0 0 0 rgba(211, 47, 47, 0.7);
  }

  @keyframes alertPulse {
    0%, 100% {
      background: #FFEBEE;
      color: #D32F2F;
      box-shadow: 0 0 0 0 rgba(211, 47, 47, 0.7);
      transform: scale(1);
    }
    50% {
      background: #D32F2F;
      color: white;
      box-shadow: 0 0 0 8px rgba(211, 47, 47, 0);
      transform: scale(1.1);
    }
  }

  .badge.warning {
    background: #FFF9C4;
    color: #F57C00;
  }

  .settings-button {
    padding: 1.25rem 2rem;
    border-top: 2px solid #E0E0E0;
    display: flex;
    align-items: center;
    gap: 1.25rem;
    cursor: pointer;
    transition: all 0.2s;
    color: #424242;
    font-weight: 500;
    font-size: 1.1rem;
  }

  .settings-button:hover {
    background: #F5F5F5;
  }

  .settings-button.active {
    background: #FFF3E0;
    color: #FF5722;
    border-right: 4px solid #FF5722;
  }
</style>
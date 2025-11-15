<script>
  import { myVariable } from '../../store.js';
  import Home from '../../pages/Home.svelte';
  import Alerts from '../../pages/Alerts.svelte';
  import AIAssistant from '../../pages/AIAssistant.svelte';
  import Setting from '../../pages/Setting.svelte';
  import EdgeLogo from '../../assets/Icons/Edge_logo.png?url';

  let { AlertsNum = 0, ActivePage = "Home" } = $props();

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
</script>

<div class="sidebar">
  <div class="logo-section">
    <img src={EdgeLogo} alt="EDGE Logo" class="logo-image" />
  </div>

  <div class="mode-selector">
    <div class="mode-dot"></div>
    <span class="mode-text">LIVE Mode</span>
    <span>▼</span>
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

  .mode-selector {
    margin: 1.5rem 1.25rem;
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
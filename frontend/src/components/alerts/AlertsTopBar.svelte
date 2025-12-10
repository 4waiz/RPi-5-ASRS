<script>
  let { currentFilter = $bindable('all'), onStartDiagnosis = () => {}, onStartVoiceDiagnosis = () => {} } = $props();

  function setFilter(filter) {
    console.log('TopBar: Setting filter to:', filter);
    currentFilter = filter;
  }
</script>

<div class="topbar">
  <div class="filter-section">
    <button
      class="filter-btn {currentFilter === 'all' ? 'active' : ''}"
      onclick={() => setFilter('all')}
    >
      All
    </button>
    <button
      class="filter-btn critical {currentFilter === 'critical' ? 'active' : ''}"
      onclick={() => setFilter('critical')}
    >
      Critical
    </button>
    <button
      class="filter-btn error {currentFilter === 'error' ? 'active' : ''}"
      onclick={() => setFilter('error')}
    >
      Errors
    </button>
    <button
      class="filter-btn warning {currentFilter === 'warning' ? 'active' : ''}"
      onclick={() => setFilter('warning')}
    >
      Warnings
    </button>
  </div>

  <div class="action-buttons">
    <button class="diagnosis-btn" onclick={() => onStartDiagnosis()}>
      <svg width="22" height="22" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/>
      </svg>
      Start AI Diagnosis
    </button>

    <button class="voice-btn" onclick={() => onStartVoiceDiagnosis()}>
      <svg width="22" height="22" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"/>
      </svg>
      Voice Diagnosis
    </button>
  </div>
</div>

<style>
  .topbar {
    background: white;
    padding: 1.75rem 2.5rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 2px solid #E0E0E0;
  }

  .filter-section {
    display: flex;
    gap: 0.75rem;
  }

  .filter-btn {
    padding: 1rem 1.75rem;
    border: 2px solid #E0E0E0;
    border-radius: 10px;
    background: white;
    cursor: pointer;
    font-weight: 600;
    font-size: 1.1rem;
    transition: all 0.2s;
    white-space: nowrap;
  }

  .filter-btn.active {
    background: #FF5722;
    color: white;
    border-color: #FF5722;
  }

  .filter-btn.critical.active {
    background: #D32F2F;
    border-color: #D32F2F;
  }

  .filter-btn.error.active {
    background: #FB8C00;
    border-color: #FB8C00;
  }

  .filter-btn.warning.active {
    background: #F9A825;
    border-color: #F9A825;
  }

  .action-buttons {
    display: flex;
    gap: 1rem;
  }

  .diagnosis-btn {
    padding: 1rem 1.75rem;
    background: white;
    color: #FF6B35;
    border: 1.5px solid #FF6B35;
    border-radius: 10px;
    cursor: pointer;
    font-weight: 600;
    font-size: 1.1rem;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    transition: all 0.2s;
    box-shadow: 0 2px 6px rgba(255, 107, 53, 0.15);
    white-space: nowrap;
  }

  .diagnosis-btn:hover {
    transform: translateY(-1px);
    background: rgba(255, 107, 53, 0.08);
    box-shadow: 0 4px 10px rgba(255, 107, 53, 0.25);
  }

  .voice-btn {
    padding: 1rem 1.75rem;
    background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%);
    color: white;
    border: none;
    border-radius: 10px;
    cursor: pointer;
    font-weight: 600;
    font-size: 1.1rem;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    transition: all 0.2s;
    box-shadow: 0 3px 10px rgba(255, 107, 53, 0.3);
    white-space: nowrap;
  }

  .voice-btn:hover {
    transform: translateY(-1px);
    box-shadow: 0 5px 15px rgba(255, 107, 53, 0.4);
  }

  @media (max-width: 1024px) {
    .topbar {
      flex-direction: column;
      gap: 1rem;
      align-items: stretch;
    }

    .filter-section {
      width: 100%;
      justify-content: center;
    }

    .action-buttons {
      width: 100%;
      flex-direction: column;
    }

    .diagnosis-btn,
    .voice-btn {
      width: 100%;
      justify-content: center;
    }
  }
</style>

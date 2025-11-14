<script>
  import { onMount } from 'svelte';
  import SideBar from '../lib/side-bar.svelte';
  import AlertCard from './AlertPages/AlertCard.svelte';
  import AlertDetailModal from './AlertPages/AlertDetailModal.svelte';
  import DiagnosticModal from './AlertPages/DiagnosticModal.svelte';
  import VoiceDiagnosticModal from './AlertPages/VoiceDiagnosticModal.svelte';
  import ResultsModal from './AlertPages/ResultsModal.svelte';
  import { alertsData, diagnosticOptions, currentFilter } from '../stores/alertStore.js';

  const API_BASE = import.meta.env?.VITE_ALERTS_API_BASE ?? 'http://localhost:8000';

  const DEMO_DIAGNOSTIC_OPTIONS = [
    'conveyor',
    'elevator',
    'gantry',
    'storage',
    'plc_network',
    'qc_vision',
    'pneumatics',
    'hmi'
  ];

  const DEMO_ALERTS = [
    {
      id: 'demo-critical',
      title: 'Gantry Z-Axis Drift',
      severity: 'critical',
      status: 'active',
      rpn: 180,
      severity_rating: 9,
      occurrence_rating: 5,
      detection_rating: 4,
      code: 'SM-GAN-201',
      subsystem: 'gantry',
      component: 'Z Axis Motor',
      detection_source: 'plc alarm',
      timestamp: new Date().toLocaleString(),
      machine: 'Stacker Crane A-01',
      message: 'Servo encoder feedback divergence detected exceeding ±1.5 mm.',
      probable_causes: 'Loose coupling,Encoder failure',
      quick_checks: 'Inspect encoder cable,Run homing routine',
      fix: 'Tighten the motor-to-hoist coupling and run the offset calibration procedure.',
      prevent_recurrence: 'Add encoder cable inspection to the weekly PM checklist.'
    },
    {
      id: 'demo-error',
      title: 'Elevator brake response slow',
      severity: 'error',
      status: 'active',
      rpn: 96,
      severity_rating: 8,
      occurrence_rating: 3,
      detection_rating: 4,
      code: 'EL-BRK-088',
      subsystem: 'elevator',
      component: 'Brake Assembly',
      detection_source: 'drive fault',
      timestamp: new Date().toLocaleString(),
      machine: 'Lift Tower 2',
      message: 'Brake release time exceeded safe limit by 120 ms.',
      probable_causes: 'Low air pressure,Worn pads',
      quick_checks: 'Verify air pressure,Check brake gap',
      fix: 'Adjust brake clearance and restore pneumatic line pressure to 90 PSI.',
      prevent_recurrence: 'Monitor pneumatic regulator trend for weekly drift.'
    },
    {
      id: 'demo-warning',
      title: 'Pick station photoeye blocked',
      severity: 'warning',
      status: 'active',
      rpn: 48,
      severity_rating: 4,
      occurrence_rating: 3,
      detection_rating: 4,
      code: 'PS-PE-014',
      subsystem: 'conveyor',
      component: 'Photoeye (PE1)',
      detection_source: 'sensor diag',
      timestamp: new Date().toLocaleString(),
      machine: 'Pick Station 2',
      message: 'Downstream photoeye blocked for more than 5 seconds.',
      probable_causes: 'Dust buildup,Obstruction on belt',
      quick_checks: 'Wipe photoeye,Clear belt',
      fix: 'Clean PE1 lens and confirm the takeaway belt is free of cartons.',
      prevent_recurrence: 'Add hourly wipe instruction to the operator checklist.'
    },
    {
      id: 'demo-critical-2',
      title: 'Conveyor drive overheating',
      severity: 'critical',
      status: 'active',
      rpn: 162,
      severity_rating: 9,
      occurrence_rating: 4,
      detection_rating: 4,
      code: 'CV-DRV-332',
      subsystem: 'conveyor',
      component: 'Drive Motor',
      detection_source: 'thermal sensor',
      timestamp: new Date().toLocaleString(),
      machine: 'Merge Conveyor 1',
      message: 'Drive housing temperature exceeded safety threshold for more than 90 seconds.',
      probable_causes: 'Fan failure,Restricted airflow',
      quick_checks: 'Inspect fan guard,Verify ventilation louvers',
      fix: 'Replace failed fan and clear debris blocking airflow.',
      prevent_recurrence: 'Schedule quarterly fan cleaning.'
    },
    {
      id: 'demo-critical-3',
      title: 'Storage shuttle misalignment',
      severity: 'critical',
      status: 'active',
      rpn: 174,
      severity_rating: 9,
      occurrence_rating: 5,
      detection_rating: 4,
      code: 'ST-SHL-441',
      subsystem: 'storage',
      component: 'Shuttle Rail',
      detection_source: 'vision system',
      timestamp: new Date().toLocaleString(),
      machine: 'Rack Lane B-04',
      message: 'Camera flagged shuttle tracking deviation greater than 3 mm.',
      probable_causes: 'Loose fasteners,Obstacle on rail',
      quick_checks: 'Inspect rail clamps,Remove debris',
      fix: 'Tighten fasteners to torque spec and recalibrate guidance camera.',
      prevent_recurrence: 'Add misalignment check to daily inspection.'
    }
  ];

  const MAX_ALERTS_DISPLAYED = 5;
  const DISPLAY_LIMITS = Object.freeze({
    critical: 3,
    warning: 1,
    error: 1
  });

  function normalizeAlerts(list = []) {
    const buckets = {
      critical: [],
      error: [],
      warning: [],
      other: []
    };

    for (const alert of list ?? []) {
      const severity = (alert.severity ?? '').toLowerCase();
      if (severity === 'critical' || severity === 'error' || severity === 'warning') {
        buckets[severity].push(alert);
      } else {
        buckets.other.push(alert);
      }
    }

    const ordered = [];
    const takeFromBucket = (bucketName, limit) => {
      const bucket = buckets[bucketName];
      while (
        bucket?.length &&
        ordered.length < MAX_ALERTS_DISPLAYED &&
        (limit === undefined || limit > 0)
      ) {
        ordered.push(bucket.shift());
        if (limit !== undefined) limit -= 1;
      }
    };

    takeFromBucket('critical', DISPLAY_LIMITS.critical);
    takeFromBucket('error', DISPLAY_LIMITS.error);
    takeFromBucket('warning', DISPLAY_LIMITS.warning);

    const leftovers = [
      ...buckets.critical,
      ...buckets.error,
      ...buckets.warning,
      ...buckets.other
    ];

    for (const alert of leftovers) {
      if (ordered.length >= MAX_ALERTS_DISPLAYED) break;
      ordered.push(alert);
    }

    return ordered;
  }

  function meetsDisplayTargets(list = []) {
    return (
      list.length >= MAX_ALERTS_DISPLAYED &&
      list.filter((alert) => (alert.severity ?? '').toLowerCase() === 'critical').length >=
        DISPLAY_LIMITS.critical &&
      list.filter((alert) => (alert.severity ?? '').toLowerCase() === 'warning').length >=
        DISPLAY_LIMITS.warning &&
      list.filter((alert) => (alert.severity ?? '').toLowerCase() === 'error').length >=
        DISPLAY_LIMITS.error
    );
  }

  function prepareAlerts(list = [], { fillWithDemo = true } = {}) {
    const normalized = normalizeAlerts(list);
    if (fillWithDemo && !meetsDisplayTargets(normalized)) {
      return normalizeAlerts([...(list ?? []), ...DEMO_ALERTS]);
    }
    return normalized;
  }

  alertsData.set(prepareAlerts(DEMO_ALERTS));

  let loading = true;
  let error = '';
  let selectedAlertId = null;
  let showDiagnosticModal = false;
  let showVoiceModal = false;
  let showResultsModal = false;
  let diagnosticResult = '';

  let selectedAlert = null;
  let totalTrackedAlerts = 0;
  let sidebarAlertCount = MAX_ALERTS_DISPLAYED;

  $: alerts = $alertsData;
  $: filterValue = $currentFilter;
  $: {
    const foundAlert = alerts.find((alert) => alert.id === selectedAlertId);
    selectedAlert = foundAlert ?? null;
    if (selectedAlertId && !foundAlert) {
      selectedAlertId = null;
    }
  }
  $: criticalCount = alerts.filter((alert) => alert.severity === 'critical').length;
  $: errorCount = alerts.filter((alert) => alert.severity === 'error').length;
  $: warningCount = alerts.filter((alert) => alert.severity === 'warning').length;
  $: totalTrackedAlerts = criticalCount + errorCount + warningCount;
  $: sidebarAlertCount =
    totalTrackedAlerts > 0 ? Math.min(MAX_ALERTS_DISPLAYED, totalTrackedAlerts) : MAX_ALERTS_DISPLAYED;

  onMount(() => {
    currentFilter.set('all');
    loadInitialData();
  });

  async function loadInitialData() {
    loading = true;
    error = '';
    try {
      const response = await fetch(`${API_BASE}/api/initial-data`);
      if (!response.ok) {
        throw new Error(`Alerts service responded with ${response.status}`);
      }
      const data = await response.json();
      const remoteOptions = Array.isArray(data.diagnostic_options)
        ? data.diagnostic_options
        : Array.isArray(data.diagnosticOptions)
        ? data.diagnosticOptions
        : [];
      diagnosticOptions.set(
        remoteOptions.length ? remoteOptions : DEMO_DIAGNOSTIC_OPTIONS
      );
      const incomingAlerts = Array.isArray(data.alerts) ? data.alerts : [];
      alertsData.set(prepareAlerts(incomingAlerts));
    } catch (err) {
      console.error('Failed to load initial alerts data', err);
      diagnosticOptions.set(DEMO_DIAGNOSTIC_OPTIONS);
      alertsData.set(prepareAlerts(DEMO_ALERTS));
      error = 'Unable to reach the alerts service. Showing demo data for now.';
    } finally {
      loading = false;
    }
  }

  async function fetchAlerts(filter) {
    loading = true;
    error = '';
    try {
      const response = await fetch(
        `${API_BASE}/api/alerts?filter=${encodeURIComponent(filter ?? 'all')}`
      );
      if (!response.ok) {
        throw new Error(`Alerts service responded with ${response.status}`);
      }
      const data = await response.json();
      alertsData.set(
        prepareAlerts(Array.isArray(data.alerts) ? data.alerts : [], {
          fillWithDemo: filter === 'all'
        })
      );
    } catch (err) {
      console.error('Failed to refresh alerts', err);
      error = 'Could not refresh alerts. Keeping the previous list.';
    } finally {
      loading = false;
    }
  }

  function handleFilterChange(filter) {
    currentFilter.set(filter);
    selectedAlertId = null;
    fetchAlerts(filter);
  }

  function handleAlertClick(event) {
    const alertId = event?.detail?.alertId;
    if (!alertId) return;
    selectedAlertId = alertId;
  }

  function handleDiagnosticComplete(event) {
    diagnosticResult = event.detail?.result ?? '';
    showDiagnosticModal = false;
    showResultsModal = true;
  }

  function closeResultsModal() {
    showResultsModal = false;
    diagnosticResult = '';
  }

</script>

<div class="alerts-page">
  <SideBar AlertsNum={sidebarAlertCount} ActivePage="Alerts" />

  <section class="alerts-shell">
    <!-- NEW TOP BAR - Styled like Home page navigation tabs -->
    <div class="top-navigation-bar">
      <div class="nav-tabs">
        <button 
          class="nav-tab"
          class:active={filterValue === 'all'}
          on:click={() => handleFilterChange('all')}
        >
          All
        </button>
        <button 
          class="nav-tab"
          class:active={filterValue === 'critical'}
          on:click={() => handleFilterChange('critical')}
        >
          Critical
        </button>
        <button 
          class="nav-tab"
          class:active={filterValue === 'error'}
          on:click={() => handleFilterChange('error')}
        >
          Errors
        </button>
        <button 
          class="nav-tab"
          class:active={filterValue === 'warning'}
          on:click={() => handleFilterChange('warning')}
        >
          Warnings
        </button>
      </div>

      <div class="action-buttons">
        <button class="action-btn diagnosis-btn" on:click={() => (showDiagnosticModal = true)}>
          <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/>
          </svg>
          Start AI Diagnosis
        </button>
        <button class="action-btn voice-btn" on:click={() => (showVoiceModal = true)}>
          <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"/>
          </svg>
          Voice Diagnosis
        </button>
      </div>
    </div>

    <div class="summary-row">
      <div class="summary-card">
        <span class="summary-label">Total Alerts</span>
        <span class="summary-value">{sidebarAlertCount}</span>
      </div>
      <div class="summary-card critical">
        <span class="summary-label">Critical</span>
        <span class="summary-value">{criticalCount}</span>
      </div>
      <div class="summary-card warning">
        <span class="summary-label">Warnings</span>
        <span class="summary-value">{warningCount}</span>
      </div>
      <div class="summary-card error">
        <span class="summary-label">Errors</span>
        <span class="summary-value">{errorCount}</span>
      </div>
    </div>

    <div class="content-region">
      {#if loading}
        <div class="state-card">
          <div class="spinner"></div>
          <p>Loading alerts...</p>
        </div>
      {:else if error}
        <div class="state-card state-error">
          <p>{error}</p>
          <button class="retry-btn" on:click={() => loadInitialData()}>Retry</button>
        </div>
      {:else if alerts.length === 0}
        <div class="state-card">
          <p>No alerts to show for "{filterValue}".</p>
          <button class="retry-btn" on:click={() => fetchAlerts('all')}>
            Reset Filter
          </button>
        </div>
      {:else}
        <div class="alerts-grid">
          {#each alerts as alert (alert.id ?? alert.code)}
            <AlertCard {alert} on:click={handleAlertClick} />
          {/each}
        </div>
      {/if}
    </div>
  </section>
</div>

{#if selectedAlert}
  <AlertDetailModal alert={selectedAlert} on:close={() => (selectedAlertId = null)} />
{/if}

{#if showDiagnosticModal}
  <DiagnosticModal
    on:close={() => (showDiagnosticModal = false)}
    on:complete={handleDiagnosticComplete}
  />
{/if}

{#if showVoiceModal}
  <VoiceDiagnosticModal on:close={() => (showVoiceModal = false)} />
{/if}

{#if showResultsModal}
  <ResultsModal result={diagnosticResult} on:close={closeResultsModal} />
{/if}

<style>
  .alerts-page {
    width: 100%;
    min-height: 100vh;
    display: flex;
    gap: 32px;
    background: #ebebeb;
    padding-right: 32px;
    box-sizing: border-box;
    overflow-y: auto;
  }

  .alerts-shell {
    flex: 1;
    min-width: 0;
    display: flex;
    flex-direction: column;
    gap: 24px;
    margin-top: 24px;
  }

  /* NEW TOP NAVIGATION BAR - Matches Home page style */
  .top-navigation-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: #ffffff;
    padding: 16px 24px;
    border-radius: 16px;
    margin: 0 24px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    gap: 20px;
    flex-wrap: wrap;
    min-width: 0;
  }

  .nav-tabs {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
  }

  .nav-tab {
    padding: 12px 32px;
    border: none;
    background: transparent;
    color: #757575;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    border-radius: 12px;
    transition: all 0.3s ease;
    position: relative;
    text-transform: capitalize;
  }

  .nav-tab:hover {
    background: rgba(255, 107, 53, 0.08);
    color: #FF6B35;
  }

  .nav-tab.active {
    background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%);
    color: #ffffff;
    box-shadow: 0 4px 12px rgba(255, 107, 53, 0.3);
  }

  .action-buttons {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
  }

  .action-btn {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 12px 20px;
    border: none;
    border-radius: 12px;
    font-size: 0.95rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
  }

  .diagnosis-btn {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
  }

  .diagnosis-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
  }

  .voice-btn {
    background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    color: white;
    box-shadow: 0 4px 12px rgba(17, 153, 142, 0.3);
  }

  .voice-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(17, 153, 142, 0.4);
  }

  .summary-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin: 0 24px;
    min-width: 0;
  }

  .summary-card {
    background: #fff;
    border-radius: 16px;
    padding: 16px 20px;
    display: flex;
    flex-direction: column;
    gap: 4px;
    border: 2px solid transparent;
  }

  .summary-card.critical {
    border-color: #d32f2f;
  }

  .summary-card.warning {
    border-color: #f9a825;
  }

  .summary-card.error {
    border-color: #ff7043;
  }

  .summary-label {
    font-size: 0.95rem;
    color: #757575;
    text-transform: uppercase;
    letter-spacing: 0.08em;
  }

  .summary-value {
    font-size: 2rem;
    font-weight: 700;
    color: #212121;
  }

  .content-region {
    flex: 1;
    margin: 0 24px 32px;
    background: #f7f7f7;
    border-radius: 24px;
    padding: 24px;
  }

  .alerts-grid {
    display: flex;
    flex-direction: column;
    gap: 20px;
  }

  .state-card {
    background: #fff;
    border-radius: 16px;
    padding: 48px 24px;
    text-align: center;
    border: 2px dashed #ccc;
    display: flex;
    flex-direction: column;
    gap: 16px;
    align-items: center;
    justify-content: center;
    min-height: 220px;
  }

  .state-card.state-error {
    border-color: #d32f2f;
    color: #d32f2f;
  }

  .spinner {
    width: 48px;
    height: 48px;
    border-radius: 50%;
    border: 4px solid #e0e0e0;
    border-top-color: #ff5722;
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    from {
      transform: rotate(0deg);
    }
    to {
      transform: rotate(360deg);
    }
  }

  .retry-btn {
    padding: 10px 20px;
    border-radius: 999px;
    border: none;
    background: #ff5722;
    color: #fff;
    font-weight: 600;
    cursor: pointer;
  }

  .retry-btn:hover {
    background: #e64a19;
  }

  @media (max-width: 820px) {
    .alerts-page {
      flex-direction: column;
      padding: 16px;
    }

    .alerts-shell {
      margin-top: 0;
    }

    .content-region {
      margin: 0;
    }

    .top-navigation-bar {
      flex-direction: column;
      align-items: stretch;
    }

    .nav-tabs {
      justify-content: center;
    }

    .action-buttons {
      justify-content: center;
    }
  }

  @media (max-width: 640px) {
    .nav-tab {
      padding: 10px 20px;
      font-size: 0.9rem;
    }

    .action-btn {
      padding: 10px 16px;
      font-size: 0.85rem;
    }
  }
</style>

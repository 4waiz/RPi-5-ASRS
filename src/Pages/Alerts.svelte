<script>
  import { onMount } from 'svelte';
  import { alertsData, diagnosticOptions } from '../stores/alertStore.js';
  import { getComponentImage } from '../lib/componentImageMap.js';
  import SideBar from '../lib/side-bar.svelte';
  import { marked } from 'marked';

  const API_BASE = import.meta.env.VITE_API_BASE ?? 'http://127.0.0.1:8000';

  let currentFilter = 'all';
  let filteredAlerts = [];
  let showDiagnosticModal = false;
  let showResultsModal = false;
  let showAlertDetailModal = false;
  let selectedAlert = null;
  let diagnosisResult = '';
  let severityInfo = null;

  // Sort and filter
  $: sortedAlerts = [...$alertsData].sort((a, b) => {
    const rpnA = a.rpn || 0;
    const rpnB = b.rpn || 0;
    if (rpnB !== rpnA) return rpnB - rpnA;
    return new Date(b.timestamp) - new Date(a.timestamp);
  });

  $: {
    if (currentFilter === 'all') filteredAlerts = sortedAlerts;
    else filteredAlerts = sortedAlerts.filter((a) => a.severity === currentFilter);
  }

  // Counts for sidebar badges
  $: criticalCount = $alertsData.filter((a) => a.severity === 'critical' && a.status !== 'resolved').length;
  $: errorCount    = $alertsData.filter((a) => a.severity === 'error'    && a.status !== 'resolved').length;
  $: warningCount  = $alertsData.filter((a) => a.severity === 'warning'  && a.status !== 'resolved').length;

  $: sidebarAlertCounts = { alerts: criticalCount + errorCount, warnings: warningCount };

  // Helpers
  function getSeverityColor(severity) {
    const colors = { critical: '#D32F2F', error: '#F57C00', warning: '#FFA000' };
    return colors[severity] || '#757575';
  }
  function getRPNLevel(rpn) {
    if (rpn >= 200) return { label: 'Extreme Risk', color: '#B71C1C', description: 'Immediate action required' };
    if (rpn >= 100) return { label: 'High Risk', color: '#D32F2F', description: 'Urgent attention needed' };
    if (rpn >= 50)  return { label: 'Medium Risk', color: '#F57C00', description: 'Schedule maintenance soon' };
    return { label: 'Low Risk', color: '#FFA000', description: 'Monitor and address when convenient' };
  }
  function loadComponentImage(component) {
    return getComponentImage(component) || null;
  }

  // Bootstrap data
  onMount(async () => {
    try {
      const response = await fetch(`${API_BASE}/api/initial-data`);
      const data = await response.json();
      alertsData.set(data.alerts || []);
      diagnosticOptions.set(data.diagnosticOptions || []);
      severityInfo = data.severityInfo;
    } catch (err) {
      console.error('Init error:', err);
    }
  });

  // ===== AI DIAGNOSIS (button + modal) =====
  const steps = ['subsystem', 'component', 'symptom'];
  const stepTitles = ['Select Subsystem', 'Select Component', 'Describe the Symptom'];
  const stepQuestions = [
    'Which part of the machine is affected?',
    'Which specific component is failing?',
    'What is the observable issue?'
  ];
  const symptoms = ['No movement','Incorrect position','Loud noise','Overheating','Failed to read','Low pressure'];

  const subsystemDisplayMap = {
    conveyor: 'Conveyor System',
    elevator: 'Elevator/Lift',
    gantry: 'Gantry/Crane',
    storage: 'Storage Racks',
    safety: 'Safety Systems',
    plc_network: 'PLC/Network',
    qc_vision: 'QC/Vision',
    pneumatics: 'Pneumatics',
    hmi: 'HMI/Interface',
    subsystem: 'General Subsystem'
  };
  const componentMap = {
    conveyor: ['Motor','Belt','Encoder (E1)','Photoeye (PE1)','Rollers','Drive Controller'],
    elevator: ['Motor','Cable','Brake','Position Sensor','Limit Switch'],
    gantry: ['X-Axis Motor','Y-Axis Motor','Z-Axis Motor','Gripper','Cable Chain'],
    storage: ['Rack Structure','Bin Sensor','Location Marker','Access Door'],
    safety: ['Emergency Stop','Light Curtain','Interlock','Safety Relay'],
    plc_network: ['PLC Module','Network Switch','I/O Card','Power Supply'],
    qc_vision: ['Camera','Barcode Scanner','Vision Processor','Lighting'],
    pneumatics: ['Compressor','Valve','Cylinder','Air Line','Pressure Sensor'],
    hmi: ['Touch Panel','Display','Control Board','Ethernet Cable'],
    subsystem: ['Controller','Sensor','Actuator','Power Module']
  };

  let diagCurrentStep = 0;
  let diagSelections = {};
  let diagOptions = [];
  let diagDisplayOptions = [];
  let diagLoading = false;
  let canProceed = false;

  function resetDiagnosticFlow() {
    diagCurrentStep = 0;
    diagSelections = {};
    diagOptions = [];
    diagDisplayOptions = [];
    diagLoading = false;
    canProceed = false;
  }

  $: {
    const diagOpts = $diagnosticOptions || [];
    if (diagCurrentStep === 0) {
      diagOptions = diagOpts;
      diagDisplayOptions = diagOpts.map((s) => subsystemDisplayMap[s] || s);
    } else if (diagCurrentStep === 1) {
      const selectedSubsystem = diagSelections.subsystem;
      if (selectedSubsystem && componentMap[selectedSubsystem]) {
        diagOptions = componentMap[selectedSubsystem];
        diagDisplayOptions = diagOptions;
      } else {
        diagOptions = ['Motor','Sensor','Controller','Actuator'];
        diagDisplayOptions = diagOptions;
      }
    } else {
      diagOptions = symptoms;
      diagDisplayOptions = symptoms;
    }
    canProceed = !!diagSelections[steps[diagCurrentStep]];
  }

  function selectDiagnosticOption(value, displayValue) {
    if (diagCurrentStep === 0) diagSelections = { ...diagSelections, subsystem: value, subsystemDisplay: displayValue };
    else if (diagCurrentStep === 1) diagSelections = { ...diagSelections, component: value };
    else diagSelections = { ...diagSelections, symptom: value };
  }
  function backDiagnosticStep() {
    if (diagCurrentStep > 0) diagCurrentStep -= 1;
    else closeDiagnosticModal();
  }
  async function advanceDiagnosticStep() {
    if (diagCurrentStep < steps.length - 1) { diagCurrentStep += 1; return; }

    const subsystemName =
      diagSelections.subsystemDisplay ||
      subsystemDisplayMap[diagSelections.subsystem] ||
      diagSelections.subsystem ||
      'Unknown Subsystem';

    const query = `Issue with ${subsystemName} - ${diagSelections.component || 'Unknown Component'}. Symptom: ${diagSelections.symptom}.`;

    diagLoading = true;
    try {
      const r = await fetch(`${API_BASE}/api/query`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query })
      });
      const data = await r.json();
      diagLoading = false;
      showDiagnosticModal = false;
      diagnosisResult = data.response || 'No response received.';
      showResultsModal = true;
    } catch (err) {
      console.error('Diagnosis error:', err);
      diagLoading = false;
      showDiagnosticModal = false;
      diagnosisResult = 'Error generating diagnosis. Please try again.';
      showResultsModal = true;
    }
  }
  function openDiagnosticModal(){ resetDiagnosticFlow(); showDiagnosticModal = true; }
  function closeDiagnosticModal(){ resetDiagnosticFlow(); showDiagnosticModal = false; }

  // Results modal
  $: diagnosisHtml = marked.parse(diagnosisResult || '');
  function closeResultsModal(){ diagnosisResult = ''; showResultsModal = false; }

  // Alert card actions
  function openAlertDetail(alertId) {
    const alert = $alertsData.find((item) => item.id === alertId);
    if (alert) { selectedAlert = alert; showAlertDetailModal = true; }
  }
  function closeAlertDetail(){ selectedAlert = null; showAlertDetailModal = false; }
</script>

<div class="alerts-layout">
  <SideBar
    AlertsNum={sidebarAlertCounts.alerts}
    WoriginNum={sidebarAlertCounts.warnings}
    ActivePage={"Alerts"}
  />

  <section class="alerts-main">
    <div class="app-container">
      <div class="main-content">
        <div class="topbar">
          <div class="filter-section">
            <button class={`filter-btn ${currentFilter === 'all' ? 'active' : ''}`} on:click={() => (currentFilter = 'all')}>All</button>
            <button class={`filter-btn critical ${currentFilter === 'critical' ? 'active' : ''}`} on:click={() => (currentFilter = 'critical')}>Critical</button>
            <button class={`filter-btn error ${currentFilter === 'error' ? 'active' : ''}`} on:click={() => (currentFilter = 'error')}>Errors</button>
            <button class={`filter-btn warning ${currentFilter === 'warning' ? 'active' : ''}`} on:click={() => (currentFilter = 'warning')}>Warnings</button>
          </div>

          <div class="action-buttons">
            <button class="diagnosis-btn" on:click={openDiagnosticModal}>
              <svg width="22" height="22" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/>
              </svg>
              Start AI Diagnosis
            </button>
          </div>
        </div>

        <div class="content-area">
          {#if filteredAlerts.length === 0}
            <div class="no-alerts">
              <svg width="80" height="80" fill="none" stroke="#BDBDBD" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
              <p>No alerts to display</p>
              <span class="no-alerts-subtitle">
                {#if currentFilter === 'critical'} No critical alerts at this time
                {:else if currentFilter === 'error'} No error alerts at this time
                {:else if currentFilter === 'warning'} No warning alerts at this time
                {:else} All systems operating normally {/if}
              </span>
            </div>
          {:else}
            <div class="alerts-header">
              <h2>
                {#if currentFilter === 'all'} All Alerts
                {:else if currentFilter === 'critical'} Critical Alerts
                {:else if currentFilter === 'error'} Error Alerts
                {:else} Warning Alerts {/if}
              </h2>
              <div class="alerts-count">
                Showing {filteredAlerts.length} alert{filteredAlerts.length === 1 ? '' : 's'} • Sorted by RPN (Risk Priority Number) - Highest first
              </div>
            </div>

            {#each filteredAlerts as alert (alert.id)}
              {@const rpnLevel = getRPNLevel(alert.rpn || 0)}
              {@const componentImage = loadComponentImage(alert.component)}
              <div
                class={`alert-card ${alert.severity} ${alert.status}`}
                on:click={() => openAlertDetail(alert.id)}
                on:keydown={(e) => e.key === 'Enter' && openAlertDetail(alert.id)}
                role="button" tabindex="0">
                <div class="alert-icon">
                  {#if alert.status === 'resolved'}
                    <svg width="32" height="32" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
                    </svg>
                  {:else if alert.severity === 'critical'}
                    <svg width="32" height="32" fill={getSeverityColor('critical')} viewBox="0 0 24 24">
                      <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
                    </svg>
                  {:else if alert.severity === 'error'}
                    <svg width="32" height="32" fill={getSeverityColor('error')} viewBox="0 0 24 24">
                      <path d="M12 2L1 21h22L12 2zm0 3.5L19.5 19h-15L12 5.5zM11 10v4h2v-4h-2zm0 5v2h2v-2h-2z"/>
                    </svg>
                  {:else}
                    <svg width="32" height="32" fill={getSeverityColor('warning')} viewBox="0 0 24 24">
                      <path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"/>
                    </svg>
                  {/if}
                </div>

                <div class="alert-content">
                  <div class="alert-header">
                    <div class="alert-title">{alert.title}</div>
                    <div class="badges">
                      <span class={`severity-badge ${alert.severity}`}>{alert.severity.toUpperCase()}</span>
                      <span class="rpn-badge" style={`background:${rpnLevel.color};`}>RPN: {alert.rpn}</span>
                    </div>
                  </div>

                  <div class="alert-meta">
                    <span class="meta-item"><strong>Code:</strong> {alert.code}</span>
                    <span class="meta-divider">•</span>
                    <span class="meta-item"><strong>Subsystem:</strong> {alert.subsystem}</span>
                    <span class="meta-divider">•</span>
                    <span class="meta-item"><strong>Component:</strong> {alert.component}</span>
                  </div>

                  <div class="fmea-metrics">
                    <div class="metric"><span class="metric-label">Severity</span><span class="metric-value">{alert.severity_rating}/10</span></div>
                    <div class="metric"><span class="metric-label">Occurrence</span><span class="metric-value">{alert.occurrence_rating}/10</span></div>
                    <div class="metric"><span class="metric-label">Detection</span><span class="metric-value">{alert.detection_rating}/10</span></div>
                    <div class="metric rpn-metric"><span class="metric-label">Risk Level</span><span class="metric-value" style={`color:${rpnLevel.color};`}>{rpnLevel.label}</span></div>
                  </div>

                  <div class="alert-time">
                    {alert.status === 'resolved' ? 'Resolved' : 'Detected'} at {alert.timestamp}
                  </div>
                </div>

                <div class="right-section">
                  {#if alert.status !== 'resolved'}
                    <button class="fix-button" on:click={(e) => { e.stopPropagation(); openAlertDetail(alert.id); }}>
                      How to Fix
                      <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
                      </svg>
                    </button>
                  {/if}

                  {#if componentImage}
                    <div class="component-visual">
                      <img src={componentImage} alt={alert.component} on:error={(e) => (e.target.style.display = 'none')}/>
                      <span class="component-label">{alert.component}</span>
                    </div>
                  {/if}
                </div>
              </div>
            {/each}
          {/if}
        </div>
      </div>

      {#if showDiagnosticModal}
        <div class="modal-overlay" role="dialog" aria-modal="true">
          <div class="diagnostic-modal" on:click|stopPropagation>
            <div class="modal-header">
              <h2>{stepTitles[diagCurrentStep]}</h2>
              <button class="close-button" on:click={closeDiagnosticModal}>
                <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                </svg>
              </button>
            </div>

            <div class="progress-bar">
              {#each steps as step, index}
                <div class={`progress-segment ${diagCurrentStep >= index ? 'active' : ''}`}></div>
              {/each}
            </div>

            <div class="modal-body">
              {#if diagLoading}
                <div class="loading-container">
                  <div class="spinner"></div>
                  <div class="loading-text">Generating AI diagnosis…</div>
                </div>
              {:else}
                <div class="question-title">{stepQuestions[diagCurrentStep]}</div>
                <div class="options-grid">
                  {#each diagOptions as option, i}
                    <div
                      class={`option-button ${diagSelections[steps[diagCurrentStep]] === option ? 'selected' : ''}`}
                      on:click={() => selectDiagnosticOption(option, diagDisplayOptions[i])}
                      on:keydown={(e) => e.key === 'Enter' && selectDiagnosticOption(option, diagDisplayOptions[i])}
                      role="button" tabindex="0">
                      {diagDisplayOptions[i]}
                    </div>
                  {/each}
                </div>
              {/if}
            </div>

            <div class="modal-footer">
              <button class="footer-button back" on:click={backDiagnosticStep}>Back</button>
              <button class="footer-button next" disabled={!canProceed || diagLoading} on:click={advanceDiagnosticStep}>
                {diagCurrentStep === steps.length - 1 ? 'Generate Diagnosis' : 'Next'}
              </button>
            </div>
          </div>
        </div>
      {/if}

      {#if showResultsModal}
        <div class="modal-overlay results-modal" role="dialog" aria-modal="true" on:click={closeResultsModal} on:keydown={(e) => e.key === 'Escape' && closeResultsModal()} tabindex="-1">
          <div class="results-content" on:click|stopPropagation>
            <div class="modal-header">
              <button class="back-button" on:click={closeResultsModal}>
                <svg width="24" height="24" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/>
                </svg>
              </button>
              <div class="modal-title">Diagnostic Report</div>
            </div>
            <div class="modal-body">
              <div class="diagnosis-content">{@html diagnosisHtml}</div>
            </div>
          </div>
        </div>
      {/if}

      {#if showAlertDetailModal && selectedAlert}
        {@const detailRpnLevel = getRPNLevel(selectedAlert.rpn || 0)}
        <div class="modal-overlay detail-modal" role="dialog" aria-modal="true" on:click={closeAlertDetail} on:keydown={(e) => e.key === 'Escape' && closeAlertDetail()} tabindex="-1">
          <div class="modal-content" on:click|stopPropagation>
            <div class="modal-header" style={`border-left:6px solid ${getSeverityColor(selectedAlert.severity)};`}>
              <div class="header-content">
                <div class="header-badges">
                  <span class="severity-badge" style={`background:${getSeverityColor(selectedAlert.severity)};`}>{selectedAlert.severity.toUpperCase()}</span>
                  <span class="rpn-badge" style={`background:${detailRpnLevel.color};`}>RPN: {selectedAlert.rpn} - {detailRpnLevel.label}</span>
                </div>
                <h2>{selectedAlert.title}</h2>
                <div class="header-meta">
                  <span><strong>Code:</strong> {selectedAlert.code}</span><span>•</span>
                  <span><strong>Machine:</strong> {selectedAlert.machine}</span><span>•</span>
                  <span><strong>Detected:</strong> {selectedAlert.timestamp}</span>
                </div>
              </div>
              <button class="close-btn" on:click={closeAlertDetail}>
                <svg width="24" height="24" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                </svg>
              </button>
            </div>

            <div class="modal-body">
              <section class="section fmea-section">
                <h3>
                  <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
                  </svg>
                  FMEA Risk Analysis
                </h3>
                <div class="fmea-grid">
                  <div class="fmea-metric">
                    <div class="metric-header"><span class="metric-label">Severity</span><span class="metric-score">{selectedAlert.severity_rating}/10</span></div>
                    <div class="metric-bar"><div class="metric-fill severity" style={`width:${selectedAlert.severity_rating * 10}%;`}></div></div>
                    <p class="metric-description">Impact if failure occurs</p>
                  </div>
                  <div class="fmea-metric">
                    <div class="metric-header"><span class="metric-label">Occurrence</span><span class="metric-score">{selectedAlert.occurrence_rating}/10</span></div>
                    <div class="metric-bar"><div class="metric-fill occurrence" style={`width:${selectedAlert.occurrence_rating * 10}%;`}></div></div>
                    <p class="metric-description">Frequency of failure</p>
                  </div>
                  <div class="fmea-metric">
                    <div class="metric-header"><span class="metric-label">Detection</span><span class="metric-score">{selectedAlert.detection_rating}/10</span></div>
                    <div class="metric-bar"><div class="metric-fill detection" style={`width:${selectedAlert.detection_rating * 10}%;`}></div></div>
                    <p class="metric-description">Difficulty detecting failure</p>
                  </div>
                  <div class="fmea-metric rpn-display">
                    <div class="rpn-score" style={`background:${detailRpnLevel.color};`}>
                      <div class="rpn-value">{selectedAlert.rpn}</div>
                      <div class="rpn-label">Risk Priority Number</div>
                    </div>
                    <p class="rpn-explanation">{detailRpnLevel.description}</p>
                    <div class="rpn-formula">RPN = Severity × Occurrence × Detection</div>
                  </div>
                </div>
              </section>

              <section class="section">
                <h3>
                  <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                  </svg>
                  System Information
                </h3>
                <div class="info-grid">
                  <div class="info-item"><strong>Subsystem:</strong><span>{selectedAlert.subsystem}</span></div>
                  <div class="info-item"><strong>Component:</strong><span>{selectedAlert.component}</span></div>
                  <div class="info-item"><strong>Detection Source:</strong><span>{selectedAlert.detection_source}</span></div>
                </div>
                <div class="message-box">
                  <strong>Issue Description:</strong>
                  <p>{selectedAlert.message}</p>
                </div>
              </section>

              <section class="section">
                <h3>
                  <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                  </svg>
                  Probable Causes
                </h3>
                <ul class="detail-list">
                  {#each selectedAlert.probable_causes.split(',') as cause}
                    <li>{cause.trim()}</li>
                  {/each}
                </ul>
              </section>

              <section class="section">
                <h3>
                  <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"/>
                  </svg>
                  Quick Diagnostic Checks
                </h3>
                <ul class="detail-list checks">
                  {#each selectedAlert.quick_checks.split(',') as check}
                    <li>{check.trim()}</li>
                  {/each}
                </ul>
              </section>

              <section class="section fix-section">
                <h3>
                  <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/>
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                  </svg>
                  Repair Instructions
                </h3>
                <div class="fix-content">{selectedAlert.fix}</div>
              </section>

              <section class="section prevention-section">
                <h3>
                  <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/>
                  </svg>
                  Prevent Recurrence
                </h3>
                <div class="prevention-content">{selectedAlert.prevent_recurrence}</div>
              </section>
            </div>
          </div>
        </div>
      {/if}
    </div>
  </section>
</div>

<style>
  .alerts-layout{display:flex;width:100%;min-height:100vh;height:100vh;gap:0;background:#f5f5f5;padding:0;box-sizing:border-box;align-items:stretch;}
  .alerts-main{flex:1;min-width:0;display:flex;flex-direction:column;background:#f5f5f5;padding:0;}
  .app-container{flex:1;background:#f5f5f5;border-radius:0;padding:32px;box-sizing:border-box;height:100%;}
  .main-content{flex:1;min-height:100%;background:#f5f5f5;}
  .content-area{padding:2.5rem;}
  .alerts-header{margin-bottom:2rem;padding-bottom:1.5rem;border-bottom:3px solid #e0e0e0;}
  .alerts-header h2{font-size:2rem;font-weight:700;color:#212121;margin:0 0 .75rem;}
  .alerts-count{font-size:1.1rem;color:#757575;font-style:italic;}
  .no-alerts{text-align:center;padding:5rem;color:#757575;display:flex;flex-direction:column;align-items:center;gap:1.5rem;}
  .no-alerts p{font-size:1.6rem;font-weight:600;margin:0;}
  .no-alerts-subtitle{font-size:1.2rem;color:#9e9e9e;}

  .topbar{background:#fff;padding:1.75rem 2.5rem;display:flex;justify-content:space-between;align-items:center;border-bottom:2px solid #e0e0e0;}
  .filter-section{display:flex;gap:.75rem;}
  .filter-btn{padding:1rem 1.75rem;border:2px solid #e0e0e0;border-radius:10px;background:#fff;cursor:pointer;font-weight:600;font-size:1.1rem;transition:.2s;white-space:nowrap;}
  .filter-btn:hover{background:#f5f5f5;border-color:#bdbdbd;}
  .filter-btn.active{background:#ff5722;color:#fff;border-color:#ff5722;}
  .filter-btn.critical.active{background:#d32f2f;border-color:#d32f2f;}
  .filter-btn.error.active{background:#fb8c00;border-color:#fb8c00;}
  .filter-btn.warning.active{background:#f9a825;border-color:#f9a825;}

  .action-buttons{display:flex;gap:1rem;}
  .diagnosis-btn{padding:1rem 1.75rem;color:#fff;border:none;border-radius:10px;cursor:pointer;font-weight:600;font-size:1.1rem;display:flex;align-items:center;gap:.75rem;transition:.2s;white-space:nowrap;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);box-shadow:0 3px 10px rgba(102,126,234,.3);}
  .diagnosis-btn:hover{transform:translateY(-1px);box-shadow:0 5px 15px rgba(102,126,234,.4);}

  .alert-card{background:#fff;border-radius:14px;padding:2rem;margin-bottom:1.5rem;display:flex;align-items:flex-start;transition:.2s;cursor:pointer;border:3px solid transparent;position:relative;}
  .alert-card::before{content:'';position:absolute;left:0;top:0;bottom:0;width:8px;border-radius:14px 0 0 14px;}
  .alert-card.critical::before{background:#d32f2f;}
  .alert-card.error::before{background:#f57c00;}
  .alert-card.warning::before{background:#ffa000;}
  .alert-card:hover{box-shadow:0 8px 24px rgba(0,0,0,.12);transform:translateY(-2px);}
  .alert-card.critical{background:#ffebee;border-color:#ef5350;}
  .alert-card.error{background:#fff3e0;border-color:#fb8c00;}
  .alert-card.warning{background:#fffde7;border-color:#fdd835;}
  .alert-card.resolved{background:#f5f5f5;opacity:.7;border-color:#e0e0e0;}
  .alert-card.resolved::before{background:#9e9e9e;}
  .alert-icon{width:50px;height:50px;display:flex;align-items:center;justify-content:center;margin-right:1.5rem;flex-shrink:0;}
  .alert-content{flex:1;min-width:0;}
  .alert-header{display:flex;justify-content:space-between;align-items:flex-start;gap:1.5rem;margin-bottom:1rem;}
  .alert-title{font-weight:600;font-size:1.4rem;line-height:1.3;flex:1;}
  .badges{display:flex;gap:.75rem;flex-shrink:0;}
  .severity-badge{padding:.5rem 1rem;border-radius:8px;font-size:.95rem;font-weight:700;letter-spacing:.5px;color:#fff;}
  .severity-badge.critical{background:#d32f2f;}
  .severity-badge.error{background:#f57c00;}
  .severity-badge.warning{background:#ffa000;}
  .rpn-badge{padding:.5rem 1rem;border-radius:8px;font-size:.95rem;font-weight:700;color:#fff;letter-spacing:.5px;}
  .alert-meta{display:flex;flex-wrap:wrap;gap:.75rem;align-items:center;color:#616161;font-size:1.1rem;margin-bottom:1rem;}
  .meta-divider{color:#bdbdbd;}
  .fmea-metrics{display:grid;grid-template-columns:repeat(4,1fr);gap:1.25rem;padding:1.25rem;background:rgba(255,255,255,.6);border-radius:10px;margin-bottom:1rem;}
  .metric{display:flex;flex-direction:column;align-items:center;text-align:center;}
  .metric-label{font-size:.95rem;color:#757575;text-transform:uppercase;font-weight:600;margin-bottom:.4rem;}
  .metric-value{font-size:1.3rem;font-weight:700;color:#212121;}
  .rpn-metric .metric-value{font-size:1.1rem;}
  .alert-time{font-style:italic;font-size:1rem;color:#757575;}

  .right-section{display:flex;flex-direction:column;align-items:center;gap:1rem;margin-left:1.5rem;flex-shrink:0;}
  .fix-button{padding:1rem 2rem;background:#fff;border:3px solid #e0e0e0;border-radius:10px;display:flex;align-items:center;gap:.75rem;cursor:pointer;font-weight:600;font-size:1.1rem;transition:.2s;white-space:nowrap;}
  .fix-button:hover{background:#f5f5f5;border-color:#bdbdbd;transform:translateX(2px);}
  .component-visual{display:flex;flex-direction:column;align-items:center;background:#fff;border-radius:12px;padding:1rem;border:2px solid #e0e0e0;min-width:180px;transition:.2s;}
  .component-visual:hover{border-color:#bdbdbd;box-shadow:0 4px 12px rgba(0,0,0,.1);}
  .component-visual img{width:150px;height:150px;object-fit:contain;margin-bottom:.75rem;}
  .component-label{font-size:.9rem;color:#424242;font-weight:600;text-align:center;line-height:1.3;}

  /* Generic modal */
  .modal-overlay{position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,.6);z-index:1000;display:flex;align-items:center;justify-content:center;padding:2rem;}
  .modal-header{display:flex;justify-content:space-between;align-items:center;}
  .close-button{background:#fff;border:none;border-radius:8px;width:40px;height:40px;display:flex;align-items:center;justify-content:center;cursor:pointer;transition:.2s;}
  .close-button:hover{background:#f5f5f5;transform:rotate(90deg);}

  /* Diagnostic modal */
  .diagnostic-modal{background:#fff;width:100%;max-width:700px;border-radius:16px;overflow:hidden;display:flex;flex-direction:column;}
  .diagnostic-modal .modal-header{padding:2rem;border-bottom:1px solid #e0e0e0;}
  .diagnostic-modal .modal-header h2{margin:0;font-size:2rem;font-weight:700;}
  .progress-bar{display:flex;gap:.5rem;margin:1.5rem 2rem 0;justify-content:center;}
  .progress-segment{height:4px;width:80px;background:#e0e0e0;border-radius:2px;}
  .progress-segment.active{background:#ff5722;}
  .diagnostic-modal .modal-body{flex:1;overflow-y:auto;padding:2rem;}
  .question-title{font-size:1.75rem;font-weight:600;text-align:center;margin-bottom:2rem;}
  .options-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;}
  .option-button{padding:2rem 1rem;border:1px solid #e0e0e0;border-radius:12px;background:#fff;cursor:pointer;font-weight:500;font-size:1rem;transition:.2s;text-align:center;}
  .option-button:hover{border-color:#ff5722;background:#fff3e0;}
  .option-button.selected{border-color:#ff5722;background:#ff5722;color:#fff;}
  .modal-footer{padding:1.5rem 2rem;border-top:1px solid #e0e0e0;display:flex;gap:1rem;}
  .footer-button{flex:1;padding:1rem;border-radius:8px;font-weight:600;font-size:1rem;cursor:pointer;transition:.2s;}
  .footer-button.back{background:#fff;border:1px solid #e0e0e0;}
  .footer-button.next{background:#424242;color:#fff;border:none;}
  .footer-button.next:hover:not(:disabled){background:#212121;}
  .footer-button:disabled{opacity:.4;cursor:not-allowed;}
  .loading-container{display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:400px;gap:1.5rem;}
  .spinner{width:60px;height:60px;border:4px solid #e0e0e0;border-top:4px solid #ff5722;border-radius:50%;animation:spin 1s linear infinite;}
  @keyframes spin{to{transform:rotate(360deg);}}
  .loading-text{font-size:1.1rem;color:#757575;font-weight:500;}

  /* Results modal */
  .results-modal{align-items:flex-start;}
  .results-content{background:#fff;border-radius:16px;width:90%;max-width:800px;max-height:90vh;overflow:hidden;display:flex;flex-direction:column;}
  .results-content .modal-header{padding:2rem;border-bottom:1px solid #e0e0e0;position:relative;}
  .back-button{position:absolute;top:2rem;left:2rem;width:48px;height:48px;border:1px solid #e0e0e0;border-radius:8px;display:flex;align-items:center;justify-content:center;cursor:pointer;background:#fff;}
  .modal-title{text-align:center;font-size:2rem;font-weight:700;}
  .results-content .modal-body{flex:1;overflow-y:auto;padding:2rem;}
  .diagnosis-content{line-height:1.8;}
  .diagnosis-content :global(h2){color:#ff5722;margin-top:1.5rem;margin-bottom:.75rem;}
  .diagnosis-content :global(h3){color:#ff5722;margin-top:1.25rem;margin-bottom:.5rem;}
  .diagnosis-content :global(strong){color:#ff5722;}
  .diagnosis-content :global(ol), .diagnosis-content :global(ul){margin-left:1.5rem;margin-top:.5rem;}
  .diagnosis-content :global(li){margin-bottom:.5rem;}
  .diagnosis-content :global(p){margin-bottom:1rem;}

  /* Detail modal (How to Fix) */
  .detail-modal .modal-content{background:#fff;border-radius:16px;width:100%;max-width:900px;max-height:90vh;overflow:hidden;display:flex;flex-direction:column;box-shadow:0 20px 60px rgba(0,0,0,.3);}
  .detail-modal .modal-header{padding:2rem;background:linear-gradient(135deg,#f5f7fa 0%,#c3cfe2 100%);display:flex;justify-content:space-between;align-items:flex-start;border-radius:16px 16px 0 0;}
  .header-content{flex:1;}
  .header-badges{display:flex;gap:.5rem;margin-bottom:1rem;}
  .severity-badge, .rpn-badge{padding:.4rem 1rem;border-radius:6px;font-size:.75rem;font-weight:700;color:#fff;letter-spacing:.5px;}
  .detail-modal .modal-header h2{margin:0 0 1rem;font-size:1.5rem;color:#212121;}
  .header-meta{display:flex;gap:.75rem;flex-wrap:wrap;color:#616161;font-size:.9rem;}
  .close-btn{background:#fff;border:none;border-radius:8px;width:40px;height:40px;display:flex;align-items:center;justify-content:center;cursor:pointer;transition:.2s;}
  .close-btn:hover{background:#f5f5f5;transform:rotate(90deg);}
  .detail-modal .modal-body{overflow-y:auto;padding:2rem;}
  .section{margin-bottom:2rem;padding-bottom:2rem;border-bottom:1px solid #e0e0e0;}
  .section:last-child{border-bottom:none;margin-bottom:0;}
  .section h3{display:flex;align-items:center;gap:.5rem;font-size:1.1rem;color:#212121;margin:0 0 1rem;font-weight:700;}
  .fmea-section{background:#f5f7fa;padding:1.5rem;border-radius:12px;border:none;}
  .fmea-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:1.5rem;}
  .fmea-metric{background:#fff;padding:1rem;border-radius:8px;}
  .metric-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:.5rem;}
  .metric-score{font-weight:700;font-size:1.2rem;color:#212121;}
  .metric-bar{height:8px;background:#e0e0e0;border-radius:4px;overflow:hidden;margin-bottom:.5rem;}
  .metric-fill{height:100%;border-radius:4px;transition:width .3s ease;}
  .metric-fill.severity{background:linear-gradient(90deg,#ffa000 0%,#d32f2f 100%);}
  .metric-fill.occurrence{background:linear-gradient(90deg,#42a5f5 0%,#1976d2 100%);}
  .metric-fill.detection{background:linear-gradient(90deg,#66bb6a 0%,#388e3c 100%);}
  .metric-description{font-size:.8rem;color:#757575;margin:0;}
  .rpn-display{grid-column:1 / -1;display:flex;flex-direction:column;align-items:center;padding:1.5rem;}
  .rpn-score{padding:2rem;border-radius:12px;text-align:center;color:#fff;margin-bottom:1rem;}
  .rpn-value{font-size:3rem;font-weight:900;line-height:1;}
  .rpn-label{font-size:.9rem;font-weight:600;margin-top:.5rem;letter-spacing:1px;}
  .rpn-explanation{font-size:1rem;color:#424242;text-align:center;margin:0 0 .5rem;font-weight:600;}
  .rpn-formula{font-size:.85rem;color:#757575;font-style:italic;}
  .info-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;margin-bottom:1rem;}
  .info-item{display:flex;flex-direction:column;gap:.25rem;}
  .info-item strong{font-size:.85rem;color:#757575;text-transform:uppercase;letter-spacing:.5px;}
  .info-item span{font-size:1rem;color:#212121;}
  .message-box{background:#fffbf0;border-left:4px solid #ffa000;padding:1rem;border-radius:8px;}
  .message-box strong{display:block;margin-bottom:.5rem;color:#424242;}
  .message-box p{margin:0;color:#616161;line-height:1.6;}
  .detail-list{list-style:none;padding:0;margin:0;}
  .detail-list li{padding:.75rem 1rem;background:#f5f5f5;margin-bottom:.5rem;border-radius:8px;border-left:3px solid #ff5722;}
  .detail-list.checks li{border-left-color:#2196f3;}
  .fix-section{background:#e3f2fd;padding:1.5rem;border-radius:12px;}
  .fix-content{background:#fff;padding:1.5rem;border-radius:8px;border-left:4px solid #2196f3;line-height:1.8;color:#424242;}
  .prevention-section{background:#e8f5e9;padding:1.5rem;border-radius:12px;}
  .prevention-content{background:#fff;padding:1.5rem;border-radius:8px;border-left:4px solid #4caf50;line-height:1.8;color:#424242;}

  @media (max-width:1024px){
    .topbar{flex-direction:column;gap:1rem;align-items:stretch;}
    .filter-section{width:100%;justify-content:center;}
    .action-buttons{width:100%;flex-direction:column;}
    .diagnosis-btn{width:100%;justify-content:center;}
  }
  @media (max-width:768px){
    .content-area{padding:1.5rem;}
    .fmea-metrics{grid-template-columns:repeat(2,1fr);}
    .alert-card{flex-direction:column;}
    .right-section{margin-left:0;margin-top:1rem;width:100%;}
    .fix-button{width:100%;justify-content:center;}
    .component-visual{width:100%;}
    .diagnostic-modal .modal-body{padding:1.5rem;}
    .options-grid{grid-template-columns:repeat(2,1fr);}
    .results-content .modal-body{padding:1.5rem;}
  }
</style>

<script>
  import { createEventDispatcher } from 'svelte';

  export let alert;

  const dispatch = createEventDispatcher();

  function close() {
    dispatch('close');
  }

  function getSeverityColor(severity) {
    const colors = {
      'critical': '#D32F2F',
      'error': '#FB8C00',
      'warning': '#F9A825'
    };
    return colors[severity] || '#757575';
  }

  function getRPNLevel(rpn) {
    if (rpn >= 200) return { label: 'Extreme Risk', color: '#B71C1C', description: 'Immediate action required' };
    if (rpn >= 100) return { label: 'High Risk', color: '#D32F2F', description: 'Urgent attention needed' };
    if (rpn >= 50) return { label: 'Medium Risk', color: '#FB8C00', description: 'Schedule maintenance soon' };
    return { label: 'Low Risk', color: '#F9A825', description: 'Monitor and address when convenient' };
  }

  // Generate placeholder image paths based on component/subsystem
  function getComponentImage(component, subsystem) {
    const cleanName = component.toLowerCase().replace(/\s+/g, '-');
    return `/images/components/${subsystem}-${cleanName}.jpg`;
  }

  function getProcedureImage(subsystem, component) {
    const cleanName = component.toLowerCase().replace(/\s+/g, '-');
    return `/images/procedures/fix-${subsystem}-${cleanName}.jpg`;
  }

  // Handle image loading errors - show placeholder
  function handleImageError(event) {
    event.target.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="400" height="300" viewBox="0 0 400 300"%3E%3Crect fill="%23f5f5f5" width="400" height="300"/%3E%3Ctext x="50%25" y="50%25" dominant-baseline="middle" text-anchor="middle" font-family="Arial" font-size="18" fill="%23999"%3EImage placeholder%3C/text%3E%3Ctext x="50%25" y="60%25" dominant-baseline="middle" text-anchor="middle" font-family="Arial" font-size="12" fill="%23bbb"%3EAdd image to /public/images/%3C/text%3E%3C/svg%3E';
  }

  $: rpnLevel = getRPNLevel(alert.rpn || 0);
  $: componentImagePath = getComponentImage(alert.component, alert.subsystem);
  $: procedureImagePath = getProcedureImage(alert.subsystem, alert.component);
</script>

<div class="modal-overlay" on:click={close}>
  <div class="modal-content" on:click|stopPropagation>
    <div class="modal-header" style="border-left: 6px solid {getSeverityColor(alert.severity)};">
      <div class="header-content">
        <div class="header-badges">
          <span class="severity-badge" style="background: {getSeverityColor(alert.severity)};">
            {alert.severity.toUpperCase()}
          </span>
          <span class="rpn-badge" style="background: {rpnLevel.color};">
            RPN: {alert.rpn} - {rpnLevel.label}
          </span>
        </div>
        <h2>{alert.title}</h2>
        <div class="header-meta">
          <span><strong>Code:</strong> {alert.code}</span>
          <span>•</span>
          <span><strong>Machine:</strong> {alert.machine}</span>
          <span>•</span>
          <span><strong>Detected:</strong> {alert.timestamp}</span>
        </div>
      </div>
      <button class="close-btn" on:click={close}>
        <svg width="24" height="24" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
        </svg>
      </button>
    </div>

    <div class="modal-body">
      <!-- FMEA Risk Analysis -->
      <section class="section fmea-section">
        <h3>
          <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
          </svg>
          FMEA Risk Analysis
        </h3>
        <div class="fmea-grid">
          <div class="fmea-metric">
            <div class="metric-header">
              <span class="metric-label">Severity</span>
              <span class="metric-score">{alert.severity_rating}/10</span>
            </div>
            <div class="metric-bar">
              <div class="metric-fill severity" style="width: {alert.severity_rating * 10}%;"></div>
            </div>
            <p class="metric-description">Impact if failure occurs</p>
          </div>

          <div class="fmea-metric">
            <div class="metric-header">
              <span class="metric-label">Occurrence</span>
              <span class="metric-score">{alert.occurrence_rating}/10</span>
            </div>
            <div class="metric-bar">
              <div class="metric-fill occurrence" style="width: {alert.occurrence_rating * 10}%;"></div>
            </div>
            <p class="metric-description">Frequency of failure</p>
          </div>

          <div class="fmea-metric">
            <div class="metric-header">
              <span class="metric-label">Detection</span>
              <span class="metric-score">{alert.detection_rating}/10</span>
            </div>
            <div class="metric-bar">
              <div class="metric-fill detection" style="width: {alert.detection_rating * 10}%;"></div>
            </div>
            <p class="metric-description">Difficulty detecting failure</p>
          </div>

          <div class="fmea-metric rpn-display">
            <div class="rpn-score" style="background: {rpnLevel.color};">
              <div class="rpn-value">{alert.rpn}</div>
              <div class="rpn-label">Risk Priority Number</div>
            </div>
            <p class="rpn-explanation">{rpnLevel.description}</p>
            <div class="rpn-formula">RPN = Severity × Occurrence × Detection</div>
          </div>
        </div>
      </section>

      <!-- System Information -->
      <section class="section">
        <h3>
          <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
          System Information
        </h3>
        <div class="info-grid">
          <div class="info-item">
            <strong>Subsystem:</strong>
            <span>{alert.subsystem}</span>
          </div>
          <div class="info-item">
            <strong>Component:</strong>
            <span>{alert.component}</span>
          </div>
          <div class="info-item">
            <strong>Detection Source:</strong>
            <span>{alert.detection_source}</span>
          </div>
        </div>
        <div class="message-box">
          <strong>Issue Description:</strong>
          <p>{alert.message}</p>
        </div>
      </section>

      <!-- Probable Causes -->
      <section class="section">
        <h3>
          <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
          Probable Causes
        </h3>
        <ul class="detail-list">
          {#each alert.probable_causes.split(',') as cause}
            <li>{cause.trim()}</li>
          {/each}
        </ul>
      </section>

      <!-- Quick Checks -->
      <section class="section">
        <h3>
          <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"/>
          </svg>
          Quick Diagnostic Checks
        </h3>
        <ul class="detail-list checks">
          {#each alert.quick_checks.split(',') as check}
            <li>{check.trim()}</li>
          {/each}
        </ul>
      </section>

      <!-- Fix Instructions -->
      <section class="section fix-section">
        <h3>
          <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/>
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
          </svg>
          Repair Instructions
        </h3>
        <div class="fix-content">
          {alert.fix}
        </div>
      </section>

      <!-- Prevention -->
      <section class="section prevention-section">
        <h3>
          <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/>
          </svg>
          Prevent Recurrence
        </h3>
        <div class="prevention-content">
          {alert.prevent_recurrence}
        </div>
      </section>
    </div>
  </div>
</div>

<style>
  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.6);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    padding: 2rem;
  }

  .modal-content {
    background: white;
    border-radius: 16px;
    width: 100%;
    max-width: 900px;
    max-height: 90vh;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  }

  .modal-header {
    padding: 2rem;
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    border-radius: 16px 16px 0 0;
  }

  .header-content {
    flex: 1;
  }

  .header-badges {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 1rem;
  }

  .severity-badge, .rpn-badge {
    padding: 0.4rem 1rem;
    border-radius: 6px;
    font-size: 0.75rem;
    font-weight: 700;
    color: white;
    letter-spacing: 0.5px;
  }

  .modal-header h2 {
    margin: 0 0 1rem 0;
    font-size: 1.5rem;
    color: #212121;
  }

  .header-meta {
    display: flex;
    gap: 0.75rem;
    flex-wrap: wrap;
    color: #616161;
    font-size: 0.9rem;
  }

  .close-btn {
    background: white;
    border: none;
    border-radius: 8px;
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.2s;
  }

  .modal-body {
    overflow-y: auto;
    padding: 2rem;
  }

  .section {
    margin-bottom: 2rem;
    padding-bottom: 2rem;
    border-bottom: 1px solid #E0E0E0;
  }

  .section:last-child {
    border-bottom: none;
    margin-bottom: 0;
  }

  .section h3 {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 1.1rem;
    color: #212121;
    margin: 0 0 1rem 0;
    font-weight: 700;
  }

  .fmea-section {
    background: #F5F7FA;
    padding: 1.5rem;
    border-radius: 12px;
    border: none;
  }

  .fmea-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1.5rem;
  }

  .fmea-metric {
    background: white;
    padding: 1rem;
    border-radius: 8px;
  }

  .metric-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
  }

  .metric-label {
    font-weight: 700;
    color: #424242;
    font-size: 0.9rem;
    text-transform: uppercase;
  }

  .metric-score {
    font-weight: 700;
    font-size: 1.2rem;
    color: #212121;
  }

  .metric-bar {
    height: 8px;
    background: #E0E0E0;
    border-radius: 4px;
    overflow: hidden;
    margin-bottom: 0.5rem;
  }

  .metric-fill {
    height: 100%;
    border-radius: 4px;
    transition: width 0.3s ease;
  }

  .metric-fill.severity {
    background: linear-gradient(90deg, #FFA000 0%, #D32F2F 100%);
  }

  .metric-fill.occurrence {
    background: linear-gradient(90deg, #42A5F5 0%, #1976D2 100%);
  }

  .metric-fill.detection {
    background: linear-gradient(90deg, #66BB6A 0%, #388E3C 100%);
  }

  .metric-description {
    font-size: 0.8rem;
    color: #757575;
    margin: 0;
  }

  .rpn-display {
    grid-column: 1 / -1;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 1.5rem;
  }

  .rpn-score {
    padding: 2rem;
    border-radius: 12px;
    text-align: center;
    color: white;
    margin-bottom: 1rem;
  }

  .rpn-value {
    font-size: 3rem;
    font-weight: 900;
    line-height: 1;
  }

  .rpn-label {
    font-size: 0.9rem;
    font-weight: 600;
    margin-top: 0.5rem;
    letter-spacing: 1px;
  }

  .rpn-explanation {
    font-size: 1rem;
    color: #424242;
    text-align: center;
    margin: 0 0 0.5rem 0;
    font-weight: 600;
  }

  .rpn-formula {
    font-size: 0.85rem;
    color: #757575;
    font-style: italic;
  }

  .info-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
    margin-bottom: 1rem;
  }

  .info-item {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }

  .info-item strong {
    font-size: 0.85rem;
    color: #757575;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .info-item span {
    font-size: 1rem;
    color: #212121;
  }

  .message-box {
    background: #FFFBF0;
    border-left: 4px solid #FFA000;
    padding: 1rem;
    border-radius: 8px;
  }

  .message-box strong {
    display: block;
    margin-bottom: 0.5rem;
    color: #424242;
  }

  .message-box p {
    margin: 0;
    color: #616161;
    line-height: 1.6;
  }

  .detail-list {
    list-style: none;
    padding: 0;
    margin: 0;
  }

  .detail-list li {
    padding: 0.75rem 1rem;
    background: #F5F5F5;
    margin-bottom: 0.5rem;
    border-radius: 8px;
    border-left: 3px solid #FF5722;
  }

  .detail-list.checks li {
    border-left-color: #2196F3;
  }

  .fix-section {
    background: #E3F2FD;
    padding: 1.5rem;
    border-radius: 12px;
  }

  .fix-content {
    background: white;
    padding: 1.5rem;
    border-radius: 8px;
    border-left: 4px solid #2196F3;
    line-height: 1.8;
    color: #424242;
  }

  .prevention-section {
    background: #E8F5E9;
    padding: 1.5rem;
    border-radius: 12px;
  }

  .prevention-content {
    background: white;
    padding: 1.5rem;
    border-radius: 8px;
    border-left: 4px solid #4CAF50;
    line-height: 1.8;
    color: #424242;
  }

  @media (max-width: 768px) {
    .fmea-grid {
      grid-template-columns: 1fr;
    }

    .info-grid {
      grid-template-columns: 1fr;
    }

    .modal-overlay {
      padding: 1rem;
    }

    .modal-header {
      padding: 1.5rem;
    }

    .modal-body {
      padding: 1.5rem;
    }
  }
</style>

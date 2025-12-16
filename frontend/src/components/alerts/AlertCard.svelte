<script>
  import { createEventDispatcher } from 'svelte';
  import { getComponentImage } from '../../lib/componentImageMap.js';

  export let alert;

  const dispatch = createEventDispatcher();

  function handleClick() {
    dispatch('click', { alertId: alert.id });
  }

  function handleFixClick(e) {
    e.stopPropagation();
    dispatch('click', { alertId: alert.id });
  }

  // Get severity color
  function getSeverityColor(severity) {
    const colors = {
      'critical': '#D32F2F',
      'error': '#F57C00',
      'warning': '#FFA000'
    };
    return colors[severity] || '#757575';
  }

  // Get RPN risk level
  function getRPNLevel(rpn) {
    if (rpn >= 200) return { label: 'Extreme Risk', color: '#B71C1C' };
    if (rpn >= 100) return { label: 'High Risk', color: '#D32F2F' };
    if (rpn >= 50) return { label: 'Medium Risk', color: '#F57C00' };
    return { label: 'Low Risk', color: '#FFA000' };
  }

  // Get component image dynamically
  function loadComponentImage(component) {
    const imagePath = getComponentImage(component);
    return imagePath ?? null;
  }

  $: rpnLevel = getRPNLevel(alert.rpn || 0);
  $: componentImage = loadComponentImage(alert.component);
  $: hasImage = componentImage !== null;
</script>

<div
  class="alert-card {alert.severity} {alert.status}"
  on:click={handleClick}
  role="button"
  tabindex="0"
  on:keydown={(e) => e.key === 'Enter' && handleClick()}
>
  <div class="alert-icon">
    {#if alert.status === 'resolved'}
      <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
      </svg>
    {:else if alert.severity === 'critical'}
      <svg fill="{getSeverityColor('critical')}" viewBox="0 0 24 24">
        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
      </svg>
    {:else if alert.severity === 'error'}
      <svg fill="{getSeverityColor('error')}" viewBox="0 0 24 24">
        <path d="M12 2L1 21h22L12 2zm0 3.5L19.5 19h-15L12 5.5zM11 10v4h2v-4h-2zm0 5v2h2v-2h-2z"/>
      </svg>
    {:else}
      <svg fill="{getSeverityColor('warning')}" viewBox="0 0 24 24">
        <path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"/>
      </svg>
    {/if}
  </div>

  <div class="alert-content">
    <div class="alert-header">
      <div class="alert-title">{alert.title}</div>
    </div>

    <div class="alert-meta">
      <span class="meta-item">
        <strong>Code:</strong> {alert.code}
      </span>
      <span class="meta-divider">•</span>
      <span class="meta-item">
        <strong>Subsystem:</strong> {alert.subsystem}
      </span>
      <span class="meta-divider">•</span>
      <span class="meta-item">
        <strong>Component:</strong> {alert.component}
      </span>
    </div>

    <div class="fmea-metrics">
      <div class="metric">
        <span class="metric-label">Severity</span>
        <span class="metric-value">{alert.severity_rating}/10</span>
      </div>
      <div class="metric">
        <span class="metric-label">Occurrence</span>
        <span class="metric-value">{alert.occurrence_rating}/10</span>
      </div>
      <div class="metric">
        <span class="metric-label">Detection</span>
        <span class="metric-value">{alert.detection_rating}/10</span>
      </div>
      <div class="metric rpn-metric">
        <span class="metric-label">Risk Level</span>
        <span class="metric-value" style="color: {rpnLevel.color};">{rpnLevel.label}</span>
      </div>
    </div>

    <div class="alert-time">
      {alert.status === 'resolved' ? 'Resolved' : 'Detected'} at {alert.timestamp}
    </div>
  </div>

  <div class="right-section">
    <!-- Badges moved to top of right section -->
    <div class="badges">
      <span class="severity-badge {alert.severity}">
        {alert.severity.toUpperCase()}
      </span>
      <span class="rpn-badge" style="background: {rpnLevel.color};">
        RPN: {alert.rpn}
      </span>
    </div>

    {#if alert.status !== 'resolved'}
      <button class="fix-button" on:click={handleFixClick}>
        How to Fix
        <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
        </svg>
      </button>
    {/if}

    <!-- Component Image Below Button -->
    {#if hasImage}
      <div class="component-visual">
        <img src={componentImage} alt={alert.component} on:error={(e) => e.target.style.display = 'none'} />
        <span class="component-label">{alert.component}</span>
      </div>
    {/if}
  </div>
</div>

<style>
  .alert-card {
    background: white;
    border-radius: 14px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: flex-start;
    gap: 1.5rem;
    transition: all 0.2s;
    cursor: pointer;
    border: 3px solid transparent;
    position: relative;
    overflow: hidden;
  }

  .alert-card::before {
    content: '';
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    width: 8px;
    border-radius: 14px 0 0 14px;
  }

  .alert-card.critical::before {
    background: #D32F2F;
  }

  .alert-card.error::before {
    background: #F57C00;
  }

  .alert-card.warning::before {
    background: #FFA000;
  }

  .alert-card:hover {
    box-shadow: 0 8px 24px rgba(0,0,0,0.12);
    transform: translateY(-2px);
  }

  .alert-card.critical {
    background: #FFEBEE;
    border-color: #EF5350;
  }

  .alert-card.error {
    background: #FFF3E0;
    border-color: #FB8C00;
  }

  .alert-card.warning {
    background: #FFFDE7;
    border-color: #FDD835;
  }

  .alert-card.resolved {
    background: #F5F5F5;
    opacity: 0.7;
    border-color: #E0E0E0;
  }

  .alert-card.resolved::before {
    background: #9E9E9E;
  }

  .alert-icon {
    width: 44px;
    height: 44px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }

  .alert-icon svg {
    width: 36px;
    height: 36px;
  }

  .alert-content {
    flex: 1;
    min-width: 0;
  }

  .alert-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 0.75rem;
  }

  .alert-title {
    font-weight: 600;
    font-size: 1.3rem;
    line-height: 1.3;
    flex: 1;
  }

  .severity-badge {
    padding: 0.65rem 1rem;
    border-radius: 8px;
    font-size: 0.9rem;
    font-weight: 700;
    letter-spacing: 0.5px;
    text-align: center;
    white-space: nowrap;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
  }

  .severity-badge.critical {
    background: #D32F2F;
    color: white;
  }

  .severity-badge.error {
    background: #F57C00;
    color: white;
  }

  .severity-badge.warning {
    background: #FFA000;
    color: white;
  }

  .rpn-badge {
    padding: 0.65rem 1rem;
    border-radius: 8px;
    font-size: 0.9rem;
    font-weight: 700;
    color: white;
    letter-spacing: 0.5px;
    text-align: center;
    white-space: nowrap;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
  }

  .alert-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    align-items: center;
    color: #616161;
    font-size: 1rem;
    margin-bottom: 0.75rem;
  }

  .meta-item {
    display: inline-flex;
    align-items: center;
  }

  .meta-divider {
    color: #BDBDBD;
  }

  .fmea-metrics {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    padding: 1rem 0.75rem;
    background: rgba(255, 255, 255, 0.6);
    border-radius: 10px;
    margin-bottom: 0.75rem;
    overflow: visible;
  }

  .metric {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    min-width: 0;
    padding: 0;
  }

  .metric-label {
    font-size: 0.65rem;
    color: #757575;
    text-transform: uppercase;
    font-weight: 600;
    margin-bottom: 0.5rem;
    line-height: 1.2;
    white-space: nowrap;
    display: block;
  }

  .metric-value {
    font-size: 1.1rem;
    font-weight: 700;
    color: #212121;
    line-height: 1.3;
    white-space: nowrap;
  }

  .rpn-metric .metric-value {
    font-size: 0.75rem;
    line-height: 1.3;
    white-space: normal;
    word-spacing: 9999px;
    max-width: 100%;
  }

  .alert-time {
    font-style: italic;
    font-size: 1rem;
    color: #757575;
  }

  /* Right Section - Badges, Button + Image */
  .right-section {
    display: flex;
    flex-direction: column;
    align-items: stretch;
    justify-content: flex-start;
    gap: 1rem;
    flex-shrink: 0;
    width: 240px;
    min-width: 240px;
    max-width: 240px;
  }

  .right-section .badges {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    align-items: stretch;
    width: 100%;
  }

  .fix-button {
    padding: 0.85rem 1.25rem;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border: none;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    cursor: pointer;
    font-weight: 600;
    font-size: 0.95rem;
    color: white;
    transition: all 0.2s;
    white-space: nowrap;
    width: 100%;
    box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
  }

  .fix-button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
  }

  /* Component Visual - Larger Image */
  .component-visual {
    display: flex;
    flex-direction: column;
    align-items: center;
    background: white;
    border-radius: 12px;
    padding: 1rem;
    border: 2px solid #E0E0E0;
    width: 100%;
    transition: all 0.2s;
    box-sizing: border-box;
  }

  .component-visual:hover {
    border-color: #BDBDBD;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  }

  .component-visual img {
    width: 140px;
    height: 140px;
    object-fit: contain;
    margin-bottom: 0.75rem;
  }

  .component-label {
    font-size: 0.9rem;
    color: #424242;
    font-weight: 600;
    text-align: center;
    line-height: 1.3;
    word-break: break-word;
    width: 100%;
  }

  @media (max-width: 768px) {
    .fmea-metrics {
      grid-template-columns: repeat(2, 1fr);
    }
    
    .alert-card {
      flex-direction: column;
    }

    .right-section {
      margin-left: 0;
      margin-top: 1rem;
      width: 100%;
    }
    
    .fix-button {
      width: 100%;
      justify-content: center;
    }

    .component-visual {
      width: 100%;
    }
  }
</style>

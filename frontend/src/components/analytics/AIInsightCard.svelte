<script>
  let { type, severity, title, message, confidence, action } = $props();

  const severityConfig = {
    warning: {
      color: '#F7931E',
      bg: '#fff5eb',
      icon: '!'
    },
    info: {
      color: '#FF6B35',
      bg: '#fff0eb',
      icon: 'i'
    },
    success: {
      color: '#FF6B35',
      bg: '#fff5eb',
      icon: '✓'
    },
    error: {
      color: '#e85a30',
      bg: '#fff0eb',
      icon: '✕'
    }
  };

  const config = severityConfig[severity] || severityConfig.info;
</script>

<div class="insight-card" style="--severity-color: {config.color}; --severity-bg: {config.bg}">
  <div class="card-header">
    <div class="icon-badge">
      <span>{config.icon}</span>
    </div>
    <div class="header-content">
      <div class="type-badge">{type}</div>
      <div class="confidence-bar">
        <span class="confidence-label">AI Confidence</span>
        <div class="confidence-track">
          <div class="confidence-fill" style="width: {confidence}%"></div>
        </div>
        <span class="confidence-value">{confidence}%</span>
      </div>
    </div>
  </div>

  <div class="card-body">
    <h4>{title}</h4>
    <p class="message">{message}</p>
  </div>

  <div class="card-footer">
    <button class="action-btn">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
      </svg>
      {action}
    </button>
  </div>
</div>

<style>
  .insight-card {
    background: white;
    border-radius: 12px;
    padding: 18px;
    border-left: 4px solid var(--severity-color);
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.06);
    transition: all 0.3s ease;
  }

  .insight-card:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    transform: translateX(4px);
  }

  .card-header {
    display: flex;
    gap: 12px;
    margin-bottom: 14px;
    align-items: flex-start;
  }

  .icon-badge {
    width: 40px;
    height: 40px;
    border-radius: 10px;
    background: var(--severity-bg);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    flex-shrink: 0;
  }

  .header-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .type-badge {
    display: inline-block;
    padding: 4px 10px;
    background: var(--severity-bg);
    color: var(--severity-color);
    border-radius: 6px;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    width: fit-content;
  }

  .confidence-bar {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .confidence-label {
    font-size: 11px;
    color: #6b7280;
    font-weight: 500;
  }

  .confidence-track {
    flex: 1;
    height: 4px;
    background: #e5e7eb;
    border-radius: 2px;
    overflow: hidden;
  }

  .confidence-fill {
    height: 100%;
    background: var(--severity-color);
    border-radius: 2px;
    transition: width 0.6s ease;
  }

  .confidence-value {
    font-size: 12px;
    font-weight: 600;
    color: var(--severity-color);
    min-width: 35px;
    text-align: right;
  }

  .card-body h4 {
    font-size: 15px;
    font-weight: 600;
    color: #1f2937;
    margin: 0 0 8px 0;
    line-height: 1.4;
  }

  .message {
    font-size: 13px;
    color: #6b7280;
    line-height: 1.6;
    margin: 0;
  }

  .card-footer {
    margin-top: 14px;
    padding-top: 14px;
    border-top: 1px solid #f3f4f6;
  }

  .action-btn {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 8px 14px;
    background: var(--severity-color);
    color: white;
    border: none;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .action-btn:hover {
    opacity: 0.9;
    transform: translateY(-1px);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  }

  .action-btn svg {
    width: 14px;
    height: 14px;
  }
</style>

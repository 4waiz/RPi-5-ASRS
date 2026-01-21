<script>
  let { name, shows, concept, color, current, target, trend, unit, history = [] } = $props();

  const isPositiveTrend = trend.startsWith('+');
  const percentage = (current / target) * 100;

  // Create sparkline path from history data
  function createSparkline(data) {
    if (!data || data.length === 0) return '';

    const width = 100;
    const height = 30;
    const max = Math.max(...data);
    const min = Math.min(...data);
    const range = max - min || 1;

    const points = data.map((value, index) => {
      const x = (index / (data.length - 1)) * width;
      const y = height - ((value - min) / range) * height;
      return `${x},${y}`;
    });

    return `M ${points.join(' L ')}`;
  }
</script>

<div class="kpi-card" style="--accent-color: {color}">
  <div class="card-header">
    <div class="trend" class:positive={isPositiveTrend} class:negative={!isPositiveTrend}>
      {trend}
      <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
        {#if isPositiveTrend}
          <path d="M6 2L10 6L8.5 6L8.5 10L3.5 10L3.5 6L2 6L6 2Z" fill="currentColor"/>
        {:else}
          <path d="M6 10L2 6L3.5 6L3.5 2L8.5 2L8.5 6L10 6L6 10Z" fill="currentColor"/>
        {/if}
      </svg>
    </div>
  </div>

  <div class="card-body">
    <h3 class="kpi-name">{name}</h3>
    <div class="value-container">
      <span class="current-value">{current}</span>
      <span class="unit">{unit}</span>
    </div>
    <div class="target-info">
      Target: {target} {unit}
    </div>
  </div>

  <div class="progress-bar">
    <div class="progress-fill" style="width: {Math.min(percentage, 100)}%"></div>
  </div>

  <div class="card-footer">
    <div class="info-row">
      <span class="label">Shows:</span>
      <span class="value">{shows}</span>
    </div>
    <div class="info-row concept">
      <span class="label">4.0 Concept:</span>
      <span class="value">{concept}</span>
    </div>
  </div>

  {#if history && history.length > 0}
    <div class="sparkline-container">
      <svg width="100" height="30" viewBox="0 0 100 30" preserveAspectRatio="none">
        <path
          d={createSparkline(history)}
          fill="none"
          stroke="var(--accent-color)"
          stroke-width="2"
          opacity="0.6"
        />
      </svg>
    </div>
  {/if}
</div>

<style>
  .kpi-card {
    background: white;
    border-radius: 16px;
    padding: 20px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
    border: 1px solid rgba(0, 0, 0, 0.06);
  }

  .kpi-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: var(--accent-color);
    opacity: 0.8;
  }

  .kpi-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.12);
  }

  .card-header {
    display: flex;
    justify-content: flex-end;
    align-items: flex-start;
    margin-bottom: 12px;
  }

  .trend {
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: 14px;
    font-weight: 600;
    padding: 6px 12px;
    border-radius: 8px;
  }

  .trend.positive {
    color: #F7931E;
    background: rgba(247, 147, 30, 0.1);
  }

  .trend.negative {
    color: #ef4444;
    background: #fee2e220;
  }

  .card-body {
    margin-bottom: 16px;
  }

  .kpi-name {
    font-size: 16px;
    font-weight: 600;
    color: #1f2937;
    margin: 0 0 12px 0;
  }

  .value-container {
    display: flex;
    align-items: baseline;
    gap: 6px;
    margin-bottom: 8px;
  }

  .current-value {
    font-size: 36px;
    font-weight: 700;
    color: var(--accent-color);
    line-height: 1;
  }

  .unit {
    font-size: 16px;
    font-weight: 500;
    color: #6b7280;
  }

  .target-info {
    font-size: 13px;
    color: #9ca3af;
    font-weight: 500;
  }

  .progress-bar {
    height: 6px;
    background: #f3f4f6;
    border-radius: 3px;
    overflow: hidden;
    margin-bottom: 16px;
  }

  .progress-fill {
    height: 100%;
    background: linear-gradient(90deg, var(--accent-color), var(--accent-color)CC);
    border-radius: 3px;
    transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
  }

  .card-footer {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .info-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 13px;
  }

  .info-row .label {
    color: #6b7280;
    font-weight: 500;
  }

  .info-row .value {
    color: #374151;
    font-weight: 600;
    text-align: right;
  }

  .info-row.concept .value {
    color: var(--accent-color);
    font-size: 12px;
  }

  .sparkline-container {
    position: absolute;
    bottom: 0;
    right: 0;
    opacity: 0.15;
    pointer-events: none;
  }
</style>
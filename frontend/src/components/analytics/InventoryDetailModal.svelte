<script>
  import { createEventDispatcher } from 'svelte';

  let { component, isOpen = false } = $props();

  const dispatch = createEventDispatcher();

  function close() {
    dispatch('close');
  }

  // Calculate stats
  const avgWeekly = $derived((component.weekly_usage.reduce((a, b) => a + b, 0) / component.weekly_usage.length).toFixed(1));
  const avgPredicted = $derived((component.predicted_usage.reduce((a, b) => a + b, 0) / component.predicted_usage.length).toFixed(1));

  // Chart setup
  const chartWidth = 600;
  const chartHeight = 200;
  const padding = { top: 20, right: 20, bottom: 40, left: 50 };
  const plotWidth = chartWidth - padding.left - padding.right;
  const plotHeight = chartHeight - padding.top - padding.bottom;

  const allData = $derived([...component.weekly_usage, ...component.predicted_usage]);
  const maxVal = $derived(Math.max(...allData) * 1.15);
  const minVal = $derived(Math.min(...allData) * 0.85);

  function getX(idx, total) {
    return padding.left + (idx / (total - 1)) * plotWidth;
  }

  function getY(val) {
    const range = maxVal - minVal || 1;
    return padding.top + plotHeight - ((val - minVal) / range) * plotHeight;
  }

  function createPath(data, startIdx = 0) {
    if (!data || data.length < 2) return '';
    const total = allData.length;
    let d = `M ${getX(startIdx, total)},${getY(data[0])}`;
    for (let i = 1; i < data.length; i++) {
      d += ` L ${getX(startIdx + i, total)},${getY(data[i])}`;
    }
    return d;
  }

  // View mode
  let viewMode = $state('both');

  // Urgency helpers
  const urgencyConfig = $derived({
    critical: { bg: '#FEE2E2', border: '#EF4444', text: '#991B1B', label: 'Order Now' },
    soon: { bg: '#FEF3C7', border: '#F59E0B', text: '#92400E', label: 'Order Soon' },
    ok: { bg: '#D1FAE5', border: '#10B981', text: '#065F46', label: 'Stock OK' }
  }[component.order_urgency || 'ok']);
</script>

{#if isOpen}
  <div class="overlay" onclick={close}>
    <div class="modal" onclick={(e) => e.stopPropagation()}>

      <!-- Header with car color indicator -->
      <div class="header" style="--car-color: {component.color}">
        <div class="header-left">
          <div class="car-dot" style="background: {component.color}"></div>
          <div>
            <h2>{component.name}</h2>
            <p class="subtitle">Chassis + 4 Wheels + Body</p>
          </div>
        </div>
        <button class="close-btn" onclick={close}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M18 6L6 18M6 6l12 12"/>
          </svg>
        </button>
      </div>

      <!-- Main Status Banner - Very Prominent -->
      <div class="status-banner" style="background: {urgencyConfig.bg}; border-color: {urgencyConfig.border}">
        <div class="status-left">
          <span class="status-label" style="color: {urgencyConfig.text}">{urgencyConfig.label}</span>
          <span class="status-stock">{component.current_stock} kits in stock</span>
        </div>
        <div class="status-right">
          <span class="status-weeks">{component.weeks_of_stock} weeks</span>
          <span class="status-sublabel">of inventory</span>
        </div>
      </div>

      <!-- AI Recommendation - Large and Clear -->
      <div class="recommendation-box">
        <div class="rec-header">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#FF6B35" stroke-width="2">
            <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
          </svg>
          <span>AI Recommendation</span>
        </div>

        <div class="rec-main">
          {#if component.order_urgency === 'critical'}
            <p class="rec-text urgent">
              Stock is critically low. Order <strong>{component.recommended_order} kits</strong> immediately to avoid stockout.
            </p>
          {:else if component.order_urgency === 'soon'}
            <p class="rec-text warning">
              Stock running low. Place order for <strong>{component.recommended_order} kits</strong> by <strong>{component.order_by_date}</strong>.
            </p>
          {:else}
            <p class="rec-text ok">
              Stock levels healthy. Next order of <strong>{component.recommended_order} kits</strong> recommended around <strong>{component.order_by_date}</strong>.
            </p>
          {/if}
        </div>

        <div class="rec-details">
          <div class="rec-detail">
            <span class="detail-label">Order Quantity</span>
            <span class="detail-value">{component.recommended_order} kits</span>
          </div>
          <div class="rec-detail">
            <span class="detail-label">Lead Time</span>
            <span class="detail-value">{component.lead_time_days} days</span>
          </div>
          <div class="rec-detail">
            <span class="detail-label">Est. Cost</span>
            <span class="detail-value">{(component.recommended_order * (component.unit_cost || 45)).toFixed(0)} د.إ</span>
          </div>
          <div class="rec-detail">
            <span class="detail-label">Order By</span>
            <span class="detail-value highlight">{component.order_by_date}</span>
          </div>
        </div>
      </div>

      <!-- Usage Chart -->
      <div class="chart-section">
        <div class="chart-header">
          <h3>Usage Trend</h3>
          <div class="view-toggle">
            <button class:active={viewMode === 'hist'} onclick={() => viewMode = 'hist'}>History</button>
            <button class:active={viewMode === 'pred'} onclick={() => viewMode = 'pred'}>Forecast</button>
            <button class:active={viewMode === 'both'} onclick={() => viewMode = 'both'}>Both</button>
          </div>
        </div>

        <div class="chart-container">
          <svg viewBox="0 0 {chartWidth} {chartHeight}">
            <!-- Y-axis labels -->
            {#each [0, 0.5, 1] as ratio}
              {@const val = minVal + (maxVal - minVal) * (1 - ratio)}
              <text x={padding.left - 10} y={padding.top + plotHeight * ratio}
                    text-anchor="end" dominant-baseline="middle" class="axis-label">
                {Math.round(val)}
              </text>
              <line x1={padding.left} y1={padding.top + plotHeight * ratio}
                    x2={chartWidth - padding.right} y2={padding.top + plotHeight * ratio}
                    class="grid-line"/>
            {/each}

            <!-- X-axis labels -->
            {#each allData as _, idx}
              {#if idx < component.weekly_usage.length}
                <text x={getX(idx, allData.length)} y={chartHeight - 10}
                      text-anchor="middle" class="axis-label">W{idx + 1}</text>
              {:else}
                <text x={getX(idx, allData.length)} y={chartHeight - 10}
                      text-anchor="middle" class="axis-label pred-label">P{idx - component.weekly_usage.length + 1}</text>
              {/if}
            {/each}

            <!-- Historical line -->
            {#if viewMode === 'hist' || viewMode === 'both'}
              <path d={createPath(component.weekly_usage, 0)} class="line hist"/>
              {#each component.weekly_usage as val, idx}
                <circle cx={getX(idx, allData.length)} cy={getY(val)} r="4" class="point hist"/>
              {/each}
            {/if}

            <!-- Predicted line -->
            {#if viewMode === 'pred' || viewMode === 'both'}
              <path d={createPath(component.predicted_usage, component.weekly_usage.length)} class="line pred"/>
              {#each component.predicted_usage as val, idx}
                <circle cx={getX(component.weekly_usage.length + idx, allData.length)} cy={getY(val)} r="4" class="point pred"/>
              {/each}
            {/if}

            <!-- Divider -->
            {#if viewMode === 'both'}
              {@const divX = getX(component.weekly_usage.length - 0.5, allData.length)}
              <line x1={divX} y1={padding.top} x2={divX} y2={padding.top + plotHeight} class="divider"/>
              <text x={divX} y={padding.top - 5} text-anchor="middle" class="divider-label">Today</text>
            {/if}
          </svg>
        </div>

        <div class="chart-legend">
          <span class="legend-item"><span class="dot hist"></span> Historical ({avgWeekly}/week)</span>
          <span class="legend-item"><span class="dot pred"></span> Predicted ({avgPredicted}/week)</span>
          <span class="legend-item confidence">Model Confidence: {Math.round((component.confidence_score || 0.8) * 100)}%</span>
        </div>
      </div>

      <!-- Quick Stats -->
      <div class="stats-row">
        <div class="stat">
          <span class="stat-value">{component.current_stock}</span>
          <span class="stat-label">Current Stock</span>
        </div>
        <div class="stat">
          <span class="stat-value">{component.reorder_point}</span>
          <span class="stat-label">Reorder Point</span>
        </div>
        <div class="stat">
          <span class="stat-value">{component.total_predicted_usage || Math.round(component.predicted_usage.reduce((a,b)=>a+b,0))}</span>
          <span class="stat-label">5-Week Demand</span>
        </div>
        <div class="stat">
          <span class="stat-value trend" class:up={component.trend_percentage > 0} class:down={component.trend_percentage < 0}>
            {component.trend_percentage > 0 ? '+' : ''}{component.trend_percentage}%
          </span>
          <span class="stat-label">Usage Trend</span>
        </div>
      </div>

    </div>
  </div>
{/if}

<style>
  .overlay {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.5);
    backdrop-filter: blur(4px);
    z-index: 1000;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 20px;
    animation: fadeIn 0.2s ease;
  }

  @keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
  }

  .modal {
    background: white;
    border-radius: 20px;
    width: 100%;
    max-width: 700px;
    max-height: 90vh;
    overflow-y: auto;
    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
    animation: slideUp 0.3s ease;
  }

  @keyframes slideUp {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
  }

  /* Hide scrollbar */
  .modal::-webkit-scrollbar { width: 0; }
  .modal { scrollbar-width: none; }

  /* Header */
  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20px 24px;
    border-bottom: 1px solid #f0f0f0;
  }

  .header-left {
    display: flex;
    align-items: center;
    gap: 14px;
  }

  .car-dot {
    width: 40px;
    height: 40px;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  }

  .header h2 {
    margin: 0;
    font-size: 22px;
    font-weight: 700;
    color: #111;
  }

  .subtitle {
    margin: 2px 0 0;
    font-size: 13px;
    color: #666;
  }

  .close-btn {
    width: 36px;
    height: 36px;
    border-radius: 10px;
    border: 1px solid #e5e5e5;
    background: white;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.2s;
  }

  .close-btn:hover {
    background: #f5f5f5;
    border-color: #ddd;
  }

  /* Status Banner */
  .status-banner {
    margin: 16px 20px;
    padding: 16px 20px;
    border-radius: 14px;
    border: 2px solid;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .status-left {
    display: flex;
    flex-direction: column;
    gap: 2px;
  }

  .status-label {
    font-size: 14px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .status-stock {
    font-size: 15px;
    color: #374151;
    font-weight: 500;
  }

  .status-right {
    text-align: right;
  }

  .status-weeks {
    font-size: 28px;
    font-weight: 800;
    color: #111;
    display: block;
  }

  .status-sublabel {
    font-size: 12px;
    color: #666;
  }

  /* Recommendation Box */
  .recommendation-box {
    margin: 0 20px 16px;
    padding: 20px;
    background: linear-gradient(135deg, #FFF7ED 0%, #FFEDD5 100%);
    border-radius: 14px;
    border: 1px solid #FDBA74;
  }

  .rec-header {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 15px;
    font-weight: 700;
    color: #9A3412;
    margin-bottom: 12px;
  }

  .rec-main {
    margin-bottom: 16px;
  }

  .rec-text {
    font-size: 16px;
    line-height: 1.5;
    margin: 0;
    color: #374151;
  }

  .rec-text strong {
    color: #111;
  }

  .rec-text.urgent strong {
    color: #DC2626;
  }

  .rec-text.warning strong {
    color: #D97706;
  }

  .rec-details {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
  }

  .rec-detail {
    background: white;
    padding: 12px;
    border-radius: 10px;
    text-align: center;
  }

  .detail-label {
    display: block;
    font-size: 11px;
    color: #666;
    text-transform: uppercase;
    letter-spacing: 0.3px;
    margin-bottom: 4px;
  }

  .detail-value {
    font-size: 15px;
    font-weight: 700;
    color: #111;
  }

  .detail-value.highlight {
    color: #EA580C;
  }

  /* Chart Section */
  .chart-section {
    margin: 0 20px 16px;
    padding: 16px;
    background: #FAFAFA;
    border-radius: 14px;
    border: 1px solid #E5E5E5;
  }

  .chart-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
  }

  .chart-header h3 {
    margin: 0;
    font-size: 15px;
    font-weight: 600;
    color: #111;
  }

  .view-toggle {
    display: flex;
    gap: 4px;
    background: #E5E5E5;
    padding: 3px;
    border-radius: 8px;
  }

  .view-toggle button {
    padding: 6px 12px;
    border: none;
    background: transparent;
    font-size: 12px;
    font-weight: 600;
    color: #666;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.2s;
  }

  .view-toggle button.active {
    background: white;
    color: #111;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  }

  .chart-container {
    background: white;
    border-radius: 10px;
    padding: 8px;
  }

  .chart-container svg {
    width: 100%;
    height: 180px;
    display: block;
  }

  .grid-line {
    stroke: #f0f0f0;
    stroke-width: 1;
  }

  .axis-label {
    font-size: 10px;
    fill: #999;
  }

  .pred-label {
    fill: #F97316;
  }

  .line {
    fill: none;
    stroke-width: 2.5;
    stroke-linecap: round;
    stroke-linejoin: round;
  }

  .line.hist {
    stroke: #374151;
  }

  .line.pred {
    stroke: #F97316;
    stroke-dasharray: 6, 4;
  }

  .point {
    stroke-width: 2;
  }

  .point.hist {
    fill: white;
    stroke: #374151;
  }

  .point.pred {
    fill: white;
    stroke: #F97316;
  }

  .divider {
    stroke: #F97316;
    stroke-width: 1.5;
    stroke-dasharray: 4, 3;
    opacity: 0.5;
  }

  .divider-label {
    font-size: 10px;
    fill: #F97316;
    font-weight: 600;
  }

  .chart-legend {
    display: flex;
    justify-content: center;
    gap: 20px;
    margin-top: 12px;
    font-size: 12px;
    color: #666;
  }

  .legend-item {
    display: flex;
    align-items: center;
    gap: 6px;
  }

  .dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
  }

  .dot.hist {
    background: #374151;
  }

  .dot.pred {
    background: #F97316;
  }

  .confidence {
    color: #999;
    font-style: italic;
  }

  /* Stats Row */
  .stats-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    padding: 16px 20px 20px;
  }

  .stat {
    text-align: center;
    padding: 12px;
    background: #F9FAFB;
    border-radius: 10px;
  }

  .stat-value {
    display: block;
    font-size: 22px;
    font-weight: 800;
    color: #111;
  }

  .stat-value.trend.up {
    color: #059669;
  }

  .stat-value.trend.down {
    color: #DC2626;
  }

  .stat-label {
    font-size: 11px;
    color: #666;
    text-transform: uppercase;
    letter-spacing: 0.3px;
  }

  /* Responsive */
  @media (max-width: 600px) {
    .rec-details {
      grid-template-columns: repeat(2, 1fr);
    }

    .stats-row {
      grid-template-columns: repeat(2, 1fr);
    }
  }
</style>
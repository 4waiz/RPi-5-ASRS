<script>
  import InventoryDetailModal from './InventoryDetailModal.svelte';

  let { component } = $props();
  let showDetailModal = $state(false);

  function openDetail() {
    showDetailModal = true;
  }

  function closeDetail() {
    showDetailModal = false;
  }

  // Get urgency styling
  const urgencyConfig = $derived({
    critical: { bg: '#FEE2E2', border: '#EF4444', text: '#991B1B', label: 'ORDER NOW' },
    soon: { bg: '#FEF3C7', border: '#F59E0B', text: '#92400E', label: 'ORDER SOON' },
    ok: { bg: '#D1FAE5', border: '#10B981', text: '#065F46', label: 'STOCK OK' }
  }[component.order_urgency || 'ok']);

  // Simple sparkline
  const allData = [...component.weekly_usage, ...component.predicted_usage];
  const max = Math.max(...allData);
  const min = Math.min(...allData);

  function createSparkline(data, startIdx = 0) {
    if (!data || data.length < 2) return '';
    const w = 120;
    const h = 40;
    const range = max - min || 1;
    let d = '';
    data.forEach((val, i) => {
      const x = ((startIdx + i) / (allData.length - 1)) * w;
      const y = h - ((val - min) / range) * h;
      d += (i === 0 ? 'M ' : ' L ') + x + ',' + y;
    });
    return d;
  }
</script>

<div
  class="card"
  onclick={openDetail}
  onkeydown={(e) => e.key === 'Enter' && openDetail()}
  role="button"
  tabindex="0"
>
  <!-- Color indicator and name -->
  <div class="card-top">
    <div class="car-color" style="background: {component.color}"></div>
    <div class="card-title">
      <h3>{component.name}</h3>
      <span class="subtitle">Chassis + Wheels + Body</span>
    </div>
  </div>

  <!-- Status badge -->
  <div class="status-badge" style="background: {urgencyConfig.bg}; border-color: {urgencyConfig.border}; color: {urgencyConfig.text}">
    {urgencyConfig.label}
  </div>

  <!-- Main stats -->
  <div class="main-stats">
    <div class="stat-big">
      <span class="value">{component.current_stock}</span>
      <span class="label">in stock</span>
    </div>
    <div class="stat-big">
      <span class="value">{component.weeks_of_stock || '?'}</span>
      <span class="label">weeks left</span>
    </div>
  </div>

  <!-- Sparkline chart -->
  <div class="sparkline-container">
    <svg viewBox="0 0 120 40" preserveAspectRatio="none">
      <path d={createSparkline(component.weekly_usage, 0)} class="line hist"/>
      <path d={createSparkline(component.predicted_usage, component.weekly_usage.length)} class="line pred"/>
    </svg>
    <div class="sparkline-legend">
      <span><span class="dot hist"></span> Past</span>
      <span><span class="dot pred"></span> Forecast</span>
    </div>
  </div>

  <!-- Quick recommendation -->
  <div class="quick-rec">
    {#if component.order_urgency === 'critical'}
      <span class="rec-urgent">Order {component.recommended_order} kits now</span>
    {:else if component.order_urgency === 'soon'}
      <span class="rec-warning">Order {component.recommended_order} by {component.order_by_date}</span>
    {:else}
      <span class="rec-ok">Next order: ~{component.order_by_date}</span>
    {/if}
  </div>

  <!-- Hover hint -->
  <div class="hover-hint">
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
      <path d="M9 18l6-6-6-6"/>
    </svg>
    View Details
  </div>
</div>

<InventoryDetailModal {component} isOpen={showDetailModal} on:close={closeDetail} />

<style>
  .card {
    background: white;
    border-radius: 16px;
    padding: 20px;
    border: 2px solid #e5e7eb;
    cursor: pointer;
    transition: all 0.25s ease;
    position: relative;
  }

  .card:hover {
    border-color: #FF6B35;
    box-shadow: 0 8px 24px rgba(255, 107, 53, 0.15);
    transform: translateY(-2px);
  }

  .card:hover .hover-hint {
    opacity: 1;
  }

  .card-top {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 12px;
  }

  .car-color {
    width: 36px;
    height: 36px;
    border-radius: 10px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.15);
    flex-shrink: 0;
  }

  .card-title h3 {
    margin: 0;
    font-size: 17px;
    font-weight: 700;
    color: #111;
  }

  .subtitle {
    font-size: 12px;
    color: #888;
  }

  .status-badge {
    display: inline-block;
    padding: 5px 10px;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.5px;
    border: 1.5px solid;
    margin-bottom: 16px;
  }

  .main-stats {
    display: flex;
    gap: 20px;
    margin-bottom: 16px;
  }

  .stat-big {
    display: flex;
    flex-direction: column;
  }

  .stat-big .value {
    font-size: 28px;
    font-weight: 800;
    color: #111;
    line-height: 1;
  }

  .stat-big .label {
    font-size: 12px;
    color: #666;
    margin-top: 2px;
  }

  .sparkline-container {
    margin-bottom: 14px;
  }

  .sparkline-container svg {
    width: 100%;
    height: 50px;
    display: block;
  }

  .line {
    fill: none;
    stroke-width: 2;
    stroke-linecap: round;
    stroke-linejoin: round;
  }

  .line.hist {
    stroke: #374151;
  }

  .line.pred {
    stroke: #F97316;
    stroke-dasharray: 4, 3;
  }

  .sparkline-legend {
    display: flex;
    gap: 14px;
    font-size: 11px;
    color: #888;
    margin-top: 6px;
  }

  .sparkline-legend span {
    display: flex;
    align-items: center;
    gap: 4px;
  }

  .dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
  }

  .dot.hist {
    background: #374151;
  }

  .dot.pred {
    background: #F97316;
  }

  .quick-rec {
    font-size: 13px;
    padding: 10px 12px;
    background: #F9FAFB;
    border-radius: 8px;
    margin-bottom: 8px;
  }

  .rec-urgent {
    color: #DC2626;
    font-weight: 600;
  }

  .rec-warning {
    color: #D97706;
    font-weight: 600;
  }

  .rec-ok {
    color: #059669;
  }

  .hover-hint {
    position: absolute;
    bottom: 12px;
    right: 14px;
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: 12px;
    color: #FF6B35;
    font-weight: 600;
    opacity: 0;
    transition: opacity 0.2s ease;
  }
</style>

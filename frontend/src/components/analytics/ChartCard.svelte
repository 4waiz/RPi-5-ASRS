<script>
  let { title, type = 'line', data = [], color = '#FF6B35' } = $props();

  function createChartPath(chartData, chartType) {
    if (!chartData || chartData.length === 0) return '';

    const width = 100;
    const height = 100;
    const max = Math.max(...chartData);
    const min = Math.min(...chartData);
    const range = max - min || 1;

    if (chartType === 'line' || chartType === 'area') {
      const points = chartData.map((value, index) => {
        const x = (index / (chartData.length - 1)) * width;
        const y = height - ((value - min) / range) * height;
        return `${x},${y}`;
      });

      if (chartType === 'area') {
        return `M 0,${height} L ${points.join(' L ')} L ${width},${height} Z`;
      }
      return `M ${points.join(' L ')}`;
    }

    return '';
  }

  function createBars(chartData) {
    if (!chartData || chartData.length === 0) return [];

    const max = Math.max(...chartData);
    const barWidth = 100 / chartData.length;
    const padding = barWidth * 0.2;

    return chartData.map((value, index) => ({
      x: index * barWidth + padding,
      y: 100 - (value / max) * 100,
      width: barWidth - padding * 2,
      height: (value / max) * 100
    }));
  }

  function formatNum(num) {
    if (num >= 100) return Math.round(num);
    if (num >= 10) return Math.round(num * 10) / 10;
    return Math.round(num * 100) / 100;
  }

  const stats = {
    max: formatNum(Math.max(...data)),
    min: formatNum(Math.min(...data)),
    avg: formatNum(data.reduce((a, b) => a + b, 0) / data.length),
    latest: formatNum(data[data.length - 1])
  };
</script>

<div class="chart-card">
  <div class="chart-header">
    <h3>{title}</h3>
    <div class="stats">
      <div class="stat">
        <span class="stat-label">Current</span>
        <span class="stat-value" style="color: {color}">{stats.latest}</span>
      </div>
    </div>
  </div>

  <div class="chart-container">
    <svg viewBox="0 0 100 100" preserveAspectRatio="none">
      {#if type === 'bar'}
        {#each createBars(data) as bar}
          <rect
            x="{bar.x}%"
            y="{bar.y}%"
            width="{bar.width}%"
            height="{bar.height}%"
            fill={color}
            opacity="0.8"
            rx="1"
          />
        {/each}
      {:else if type === 'area'}
        <path
          d={createChartPath(data, 'area')}
          fill={color}
          opacity="0.2"
        />
        <path
          d={createChartPath(data, 'line')}
          fill="none"
          stroke={color}
          stroke-width="0.5"
        />
      {:else}
        <path
          d={createChartPath(data, 'line')}
          fill="none"
          stroke={color}
          stroke-width="0.8"
          stroke-linecap="round"
          stroke-linejoin="round"
        />
      {/if}
    </svg>
  </div>

  <div class="chart-footer">
    <div class="footer-stat">
      <span class="label">Max</span>
      <span class="value">{stats.max}</span>
    </div>
    <div class="footer-stat">
      <span class="label">Avg</span>
      <span class="value">{stats.avg}</span>
    </div>
    <div class="footer-stat">
      <span class="label">Min</span>
      <span class="value">{stats.min}</span>
    </div>
  </div>
</div>

<style>
  .chart-card {
    background: white;
    border-radius: 12px;
    padding: 20px;
    border: 1px solid #e5e7eb;
    transition: all 0.3s ease;
  }

  .chart-card:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }

  .chart-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
  }

  .chart-header h3 {
    font-size: 16px;
    font-weight: 600;
    color: #1f2937;
    margin: 0;
  }

  .stats {
    display: flex;
    gap: 16px;
  }

  .stat {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
  }

  .stat-label {
    font-size: 11px;
    color: #9ca3af;
    font-weight: 500;
  }

  .stat-value {
    font-size: 18px;
    font-weight: 700;
  }

  .chart-container {
    width: 100%;
    height: 150px;
    margin-bottom: 16px;
  }

  .chart-container svg {
    width: 100%;
    height: 100%;
  }

  .chart-footer {
    display: flex;
    justify-content: space-around;
    padding-top: 12px;
    border-top: 1px solid #f3f4f6;
  }

  .footer-stat {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
  }

  .footer-stat .label {
    font-size: 11px;
    color: #9ca3af;
    font-weight: 500;
    text-transform: uppercase;
  }

  .footer-stat .value {
    font-size: 16px;
    font-weight: 600;
    color: #374151;
  }
</style>
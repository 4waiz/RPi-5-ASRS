<script>
  import SideBar from "../components/shared/Sidebar.svelte";
  import KPICard from "../components/analytics/KPICard.svelte";
  import ChartCard from "../components/analytics/ChartCard.svelte";
  import AIInsightCard from "../components/analytics/AIInsightCard.svelte";
  import InventoryForecastCard from "../components/analytics/InventoryForecastCard.svelte";
  import { onMount } from 'svelte';

  const totalErrors = 5;
  let analyticsData = $state(null);
  let loading = $state(true);
  let selectedTimeRange = $state('24h');
  let modelInfo = $state(null);

  const timeRanges = ['1h', '24h', '7d', '30d'];

  const sections = [
    { id: 'kpis', label: 'KPIs' },
    { id: 'charts', label: 'Charts' },
    { id: 'insights', label: 'AI Insights' },
    { id: 'inventory', label: 'Inventory' }
  ];

  let clickedSection = $state(null);

  function scrollToSection(sectionId) {
    // Show brief highlight
    clickedSection = sectionId;
    setTimeout(() => {
      clickedSection = null;
    }, 300);

    const element = document.getElementById(sectionId);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }
  const API_BASE = import.meta.env?.VITE_ANALYTICS_API_BASE ?? "http://192.168.208.146:8002";

  // KPI definitions - using consistent orange/neutral color scheme
  const kpiDefinitions = [
    {
      id: 'throughput',
      name: 'Throughput',
      shows: 'Productivity',
      concept: 'IoT real-time monitoring',
      unit: 'items/hr',
      color: '#FF6B35'
    },
    {
      id: 'availability',
      name: 'Availability',
      shows: 'System readiness',
      concept: 'Predictive maintenance',
      unit: '%',
      color: '#FF6B35'
    },
    {
      id: 'inventory_accuracy',
      name: 'Inventory Accuracy',
      shows: 'Digital correctness',
      concept: 'Digital twin + MES',
      unit: '%',
      color: '#F7931E'
    },
    {
      id: 'cycle_time',
      name: 'Cycle Time',
      shows: 'Efficiency',
      concept: 'Optimization + automation',
      unit: 'sec',
      color: '#FF6B35'
    },
    {
      id: 'picking_accuracy',
      name: 'Picking Accuracy',
      shows: 'Quality',
      concept: 'Zero-defect processes',
      unit: '%',
      color: '#F7931E'
    },
    {
      id: 'energy_per_cycle',
      name: 'Energy/Cycle',
      shows: 'Sustainability',
      concept: 'Smart energy systems',
      unit: 'kWh',
      color: '#FF6B35'
    },
    {
      id: 'error_rate',
      name: 'Alerts/Error Rate',
      shows: 'System reliability',
      concept: 'Smart diagnostics',
      unit: 'errors/hr',
      color: '#F7931E'
    }
  ];

  async function fetchAnalytics() {
    loading = true;
    try {
      const response = await fetch(`${API_BASE}/api/analytics?time_range=${selectedTimeRange}`);

      if (!response.ok) {
        throw new Error(`Analytics API responded with ${response.status}`);
      }

      const data = await response.json();

      // Transform API response to match our format
      analyticsData = {
        kpis: data.kpis,
        aiInsights: data.aiInsights,
        inventoryForecast: data.inventoryForecast
      };

      modelInfo = data.model_info;

      console.log('Loaded analytics from ML backend:', modelInfo);
    } catch (err) {
      console.error('Failed to load analytics from API, using demo data:', err);
      // Fallback to demo data if API fails
      analyticsData = generateDemoData();
      modelInfo = null;
    } finally {
      loading = false;
    }
  }

  function generateDemoData() {
    return {
      kpis: {
        throughput: { current: 245, target: 300, trend: '+12%', history: Array(24).fill(0).map((_, i) => 200 + Math.random() * 100) },
        availability: { current: 94.5, target: 95, trend: '+2.1%', history: Array(24).fill(0).map((_, i) => 90 + Math.random() * 8) },
        inventory_accuracy: { current: 98.2, target: 99, trend: '+0.5%', history: Array(24).fill(0).map((_, i) => 96 + Math.random() * 3) },
        cycle_time: { current: 12.3, target: 10, trend: '-8%', history: Array(24).fill(0).map((_, i) => 10 + Math.random() * 5) },
        picking_accuracy: { current: 99.1, target: 99.5, trend: '+0.3%', history: Array(24).fill(0).map((_, i) => 98 + Math.random() * 2) },
        energy_per_cycle: { current: 2.4, target: 2.0, trend: '-5%', history: Array(24).fill(0).map((_, i) => 2 + Math.random() * 1) },
        error_rate: { current: 3.2, target: 2, trend: '-15%', history: Array(24).fill(0).map((_, i) => 2 + Math.random() * 3) }
      },
      aiInsights: [
        {
          type: 'prediction',
          severity: 'warning',
          title: 'Predicted Maintenance Required',
          message: 'Conveyor belt motor showing early signs of degradation. Predicted failure in 72 hours.',
          confidence: 87,
          action: 'Schedule preventive maintenance'
        },
        {
          type: 'optimization',
          severity: 'info',
          title: 'Energy Optimization Opportunity',
          message: 'Peak energy usage detected during off-hours. Adjusting schedule could save 12% energy.',
          confidence: 92,
          action: 'Apply recommended schedule'
        },
        {
          type: 'anomaly',
          severity: 'success',
          title: 'Performance Improvement Detected',
          message: 'Throughput increased by 15% after recent optimization changes.',
          confidence: 95,
          action: 'Document best practices'
        }
      ],
      inventoryForecast: {
        components: [
          {
            name: 'Chassis Units',
            current_stock: 45,
            weekly_usage: [8, 12, 10, 15, 9, 11, 13],
            predicted_usage: [14, 16, 15, 18, 17],
            recommended_order: 22,
            reorder_point: 30,
            lead_time_days: 7
          },
          {
            name: 'Wheel Sets',
            current_stock: 120,
            weekly_usage: [20, 25, 22, 28, 24, 26, 23],
            predicted_usage: [27, 30, 28, 32, 29],
            recommended_order: 45,
            reorder_point: 80,
            lead_time_days: 5
          },
          {
            name: 'Card Bodies (Red)',
            current_stock: 88,
            weekly_usage: [15, 18, 16, 20, 17, 19, 18],
            predicted_usage: [21, 23, 22, 24, 25],
            recommended_order: 35,
            reorder_point: 60,
            lead_time_days: 3
          },
          {
            name: 'Card Bodies (Green)',
            current_stock: 72,
            weekly_usage: [12, 14, 13, 16, 15, 14, 13],
            predicted_usage: [17, 18, 16, 19, 20],
            recommended_order: 28,
            reorder_point: 50,
            lead_time_days: 3
          },
          {
            name: 'Card Bodies (Blue)',
            current_stock: 65,
            weekly_usage: [10, 12, 11, 14, 13, 12, 11],
            predicted_usage: [15, 16, 14, 17, 18],
            recommended_order: 25,
            reorder_point: 45,
            lead_time_days: 3
          },
          {
            name: 'Motor Controllers',
            current_stock: 32,
            weekly_usage: [4, 5, 6, 7, 5, 6, 5],
            predicted_usage: [7, 8, 7, 9, 8],
            recommended_order: 12,
            reorder_point: 20,
            lead_time_days: 10
          }
        ]
      }
    };
  }

  onMount(() => {
    fetchAnalytics();
    const interval = setInterval(fetchAnalytics, 3600000); // Refresh every hour
    return () => clearInterval(interval);
  });

  function handleTimeRangeChange(range) {
    selectedTimeRange = range;
    fetchAnalytics();
  }
</script>

<div class="main">
  <SideBar AlertsNum={totalErrors} ActivePage="Analytics" />

  <section class="content">
    <div class="header">
      <div class="header-top">
        <div class="header-title">
          <h1>Advanced Analytics</h1>
          <span class="header-subtitle">Real-time Insights & ML Forecasting</span>
        </div>
        <div class="header-controls">
          <div class="time-selector">
            {#each timeRanges as range}
              <button
                class="time-btn"
                class:active={selectedTimeRange === range}
                onclick={() => handleTimeRangeChange(range)}
              >
                {range}
              </button>
            {/each}
          </div>
          <button class="refresh-btn" onclick={fetchAnalytics} aria-label="Refresh">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </button>
        </div>
      </div>
      <div class="section-nav">
        {#each sections as section}
          <button
            class="section-btn"
            class:active={clickedSection === section.id}
            onclick={() => scrollToSection(section.id)}
          >
            {section.label}
          </button>
        {/each}
      </div>
    </div>

    {#if loading}
      <div class="loading">
        <div class="spinner"></div>
        <p>Loading analytics data...</p>
      </div>
    {:else if analyticsData}
      <!-- KPI Cards Grid -->
      <div id="kpis" class="kpi-grid">
        {#each kpiDefinitions as kpi}
          <KPICard
            name={kpi.name}
            shows={kpi.shows}
            concept={kpi.concept}
            color={kpi.color}
            current={analyticsData.kpis[kpi.id].current}
            target={analyticsData.kpis[kpi.id].target}
            trend={analyticsData.kpis[kpi.id].trend}
            unit={kpi.unit}
            history={analyticsData.kpis[kpi.id].history}
          />
        {/each}
      </div>

      <!-- Charts Section -->
      <div id="charts" class="charts-section">
        <h2 class="section-title">Detailed Analytics</h2>
        <div class="charts-grid">
          <ChartCard
            title="Throughput Trends"
            type="line"
            data={analyticsData.kpis.throughput.history}
            color="#FF6B35"
          />
          <ChartCard
            title="System Availability"
            type="area"
            data={analyticsData.kpis.availability.history}
            color="#F7931E"
          />
          <ChartCard
            title="Energy Consumption"
            type="bar"
            data={analyticsData.kpis.energy_per_cycle.history}
            color="#FF6B35"
          />
          <ChartCard
            title="Quality Metrics"
            type="line"
            data={analyticsData.kpis.picking_accuracy.history}
            color="#F7931E"
          />
        </div>
      </div>

      <!-- AI Insights Section -->
      <div id="insights" class="insights-section">
        <h2 class="section-title">AI-Powered Insights</h2>
        <div class="insights-grid">
          {#each analyticsData.aiInsights as insight}
            <AIInsightCard {...insight} />
          {/each}
        </div>
      </div>

      <!-- Inventory Forecast Section (Regression Model) -->
      <div id="inventory" class="forecast-section">
        <div class="section-header">
          <div>
            <h2 class="section-title">Predictive Inventory Analytics</h2>
            <p class="section-subtitle">
              {#if modelInfo}
                {modelInfo.forecasting_model} • {modelInfo.data_points_analyzed} data points analyzed
              {:else}
                Linear regression forecast based on historical usage patterns
              {/if}
            </p>
          </div>
          <div class="model-badge">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            {modelInfo ? 'ML Model Active' : 'Demo Mode'}
          </div>
        </div>
        <div class="forecast-grid">
          {#each analyticsData.inventoryForecast.components as component}
            <InventoryForecastCard {component} />
          {/each}
        </div>
      </div>
    {/if}
  </section>
</div>

<style>
  /* Disable blue highlight on tap/click */
  :global(*) {
    -webkit-tap-highlight-color: transparent;
    -webkit-touch-callout: none;
  }

  :global(button), :global(a), :global(.kpi-card), :global(.chart-card), :global(.section-btn), :global(.time-btn) {
    -webkit-user-select: none;
    user-select: none;
    outline: none;
  }

  .main {
    width: 100%;
    height: 100vh;
    display: flex;
    gap: 16px;
    background: #ebebeb;
    box-sizing: border-box;
    padding-right: 16px;
    overflow: hidden;
  }

  .content {
    flex: 1;
    height: 100%;
    overflow-y: auto;
    padding: 12px;
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .header {
    background: white;
    padding: 10px 16px;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .header-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .header-title {
    display: flex;
    align-items: baseline;
    gap: 10px;
  }

  .header-title h1 {
    margin: 0;
    font-size: 18px;
    font-weight: 700;
    background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }

  .header-subtitle {
    font-size: 11px;
    color: #9ca3af;
    font-weight: 500;
  }

  .header-controls {
    display: flex;
    gap: 8px;
    align-items: center;
  }

  .time-selector {
    display: flex;
    gap: 2px;
    background: #f3f4f6;
    padding: 3px;
    border-radius: 8px;
  }

  .time-btn {
    padding: 5px 10px;
    border: none;
    background: transparent;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 500;
    color: #6b7280;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .time-btn:hover {
    background: #e5e7eb;
  }

  .time-btn:active {
    transform: scale(0.95);
  }

  .time-btn.active {
    background: white;
    color: #FF6B35;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  }

  .refresh-btn {
    padding: 6px;
    border: none;
    background: #f3f4f6;
    border-radius: 6px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s ease;
  }

  .refresh-btn:hover {
    background: #e5e7eb;
    transform: rotate(90deg);
  }

  .refresh-btn:active {
    transform: scale(0.9);
    background: #FF6B35;
  }

  .refresh-btn:active svg {
    color: white;
  }

  .refresh-btn svg {
    color: #FF6B35;
  }

  /* Section Navigation */
  .section-nav {
    display: flex;
    gap: 6px;
  }

  .section-btn {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    padding: 8px 12px;
    border: none;
    background: #f3f4f6;
    border-radius: 8px;
    font-size: 12px;
    font-weight: 500;
    color: #6b7280;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .section-btn:hover {
    background: #e5e7eb;
  }

  .section-btn:active {
    transform: scale(0.97);
    background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%);
    color: white;
  }

  .section-btn.active {
    background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%);
    color: white;
    box-shadow: 0 2px 8px rgba(255, 107, 53, 0.3);
  }

  .loading {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 40px;
    gap: 12px;
    background: white;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  }

  .spinner {
    width: 36px;
    height: 36px;
    border: 3px solid #f3f4f6;
    border-top: 3px solid #FF6B35;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }

  .kpi-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 12px;
    scroll-margin-top: 12px;
  }

  .section-title {
    font-size: 16px;
    font-weight: 600;
    color: #1f2937;
    margin: 0 0 10px 0;
  }

  .charts-section {
    background: white;
    padding: 14px;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    scroll-margin-top: 12px;
  }

  .charts-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
    gap: 12px;
  }

  .insights-section {
    background: white;
    padding: 14px;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    scroll-margin-top: 12px;
  }

  .insights-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 10px;
  }

  .forecast-section {
    background: white;
    padding: 14px;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    scroll-margin-top: 12px;
  }

  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
  }

  .section-subtitle {
    margin: 2px 0 0 0;
    font-size: 11px;
    color: #6b7280;
    font-weight: 500;
  }

  .model-badge {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 5px 10px;
    background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%);
    color: white;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 600;
    box-shadow: 0 2px 8px rgba(255, 107, 53, 0.3);
  }

  .model-badge svg {
    width: 12px;
    height: 12px;
  }

  .forecast-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 12px;
  }

  /* Scrollbar styling - thin and subtle */
  .content::-webkit-scrollbar {
    width: 4px;
  }

  .content::-webkit-scrollbar-track {
    background: transparent;
  }

  .content::-webkit-scrollbar-thumb {
    background: #cbd5e1;
    border-radius: 2px;
  }

  .content::-webkit-scrollbar-thumb:hover {
    background: #94a3b8;
  }

  /* Smooth scroll behavior */
  .content {
    scroll-behavior: smooth;
  }
</style>
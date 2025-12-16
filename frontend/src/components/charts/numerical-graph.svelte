<script>
    // Optional: make values props
    export let value = 120;
    export let unit = "Milliseconds";
    export let label = "CPU overload";
    export let ghraphDirection = "increase"; // "increase" or "decrease"
    let graphColor = "#222222";

    if (ghraphDirection === "decrease") {
        graphColor = "rgba(15, 153, 11, 0.30)";
    } else if (ghraphDirection === "increase") {
        graphColor = "rgba(255, 0, 0, 0.30)";
    }
</script>

<div class="card">
    <div class="content">
        <div class="metric-row">
            <span class="number">{value}</span>
            <span class="unit">{unit}</span>
        </div>
        <div class="label">{label}</div>
    </div>

    <div class="graph-area">
        <svg class="chart-svg" viewBox="0 0 320 65" preserveAspectRatio="none">
            <path
                class="line-path"
                style="stroke: {graphColor}; {ghraphDirection === 'decrease'
                    ? 'transform: scaleX(-1);'
                    : ''}"
                d="
                    M 30,55 
                    L 40,52 
                    L 80,45 
                    L 120,48 
                    L 160,35 
                    L 200,30 
                    L 240,32 
                    L 280,30 
                    L 300,20
                "
            />
        </svg>
    </div>
</div>

<style>
    /* Card Container */
    .card {
        width: 249.6px;
        height: 120px;
        border-radius: 20px;
        border: 1px solid #a6a6a6;
        position: relative;
        overflow: hidden;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        margin-left: 16px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }

    /* Text Content */
    .content {
        padding: 18px 0 0 18px;
        z-index: 2;
    }

    .metric-row {
        display: flex;
        align-items: baseline;
        gap: 8px;
    }

    .number {
        font-size: 24px;
        font-weight: 700;
        color: #000;
        line-height: 1;
        letter-spacing: -1px;
    }

    .unit {
        font-size: 17px;
        font-weight: 400;
        color: #555;
    }

    .label {
        font-size: 18px;
        font-weight: 400;
        color: #000;
        margin-top: 2px;
    }

    /* Graph Section Background */
    .graph-area {
        position: absolute;
        bottom: 0;
        left: 0;
        width: 100%;
        height: 65px;
        display: flex;
        align-items: flex-end;
    }

    /* SVG Chart */
    .chart-svg {
        width: 100%;
        height: 100%;
        display: block;
    }

    /* Line Style */
    .line-path {
        fill: none;
        stroke-width: 3;
        stroke-linecap: round;
        stroke-linejoin: round;
        transform-origin: center;
    }
</style>

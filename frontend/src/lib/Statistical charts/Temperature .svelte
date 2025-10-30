<script>
    // Props
    let { Temperature = 104, max = 160, steps = 3  } = $props();

    // Clamp and normalize fill %
    const pct = $derived(Math.max(0, Math.min(100, (Temperature / max) * 100)));

    // Generate scale labels dynamically
    function a() {
        const step = max / steps;
        const arr = [];
        for (let i = 0; i <= steps; i++) {
            arr.push(Math.round(max - step * i));
        }
        return arr;
    }


    // CSS vars
    const vars = $derived(`--level:${pct}%;`);
</script>

<div class="thermo-container" style={vars}>
    <div class="thermo">
        <div class="tube">
            <div class="fill"></div>
            <div class="pointer"></div>
        </div>

        <div class="labels">
            {#each a() as t}
                <div>{t}</div>
            {/each}
        </div>

        <div class="circle"></div>
    </div>

    <div class="readout">
        <div class="value">{Math.round(Temperature)}°C</div>
        <div class="label">Temperature</div>
    </div>
</div>
<style>
.thermo-container {
    --level: 50%;
    display: flex;
    flex-direction: column;
    align-items: center;
    width: fit-content;
    height: auto;
    font-family: system-ui, sans-serif;
    color: #000;
}

.thermo {
    display: flex;
    align-items: flex-end;
    gap: 6px;
    height: 95px;
    position: relative;
    margin: 0 -20px 8px 0;
}

.tube {
    position: relative;
    width: 11px;
    height: 85px;
    background: #c8c8c8;
    border: 2px solid #c8c8c8;
    border-radius: 10px;
    overflow: hidden;
}

.fill {
    position: absolute;
    bottom: 0;
    width: 100%;
    height: var(--level);
    background: #e11d48;
    transition: height 0.5s ease;
}

.circle {
    position: absolute;
    bottom: -12px;
    right: 16.5px;
    width: 20px;
    height: 20px;
    background: #e11d48;
    border: 2px solid #c8c8c8;
    border-radius: 50%;
    transition: height 0.5s ease;
}

.pointer {
    position: absolute;
    left: -8px;
    bottom: var(--level);
    width: 0;
    height: 0;
    border-top: 6px solid transparent;
    border-bottom: 6px solid transparent;
    border-left: 8px solid #000;
    transform: translateY(50%);
    transition: bottom 0.5s ease;
}

.labels {
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    height: 95px;
    font-size: 14px;
}

.readout {
    margin-top: 12px;
    text-align: center;
}

.value {
    font-size: 19px;
    font-weight: 700;
}

.label {
    font-size: 19px;
}
</style>

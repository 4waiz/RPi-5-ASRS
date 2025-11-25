<script>
    // Props
    let { Temperature = 104, max = 160, steps = 3, label = "Temperature" } = $props();

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
</script>

<div class="thermo-container">
    <div class="thermo">
        <div class="tube">
            <div class="fill" style:height="{pct}%"></div>
        </div>

        <div class="labels">
            {#each a() as t}
                <div>{t}</div>
            {/each}
        </div>
    </div>

    <div class="readout">
        <div class="value">{Math.round(Temperature)}°C</div>
        <div class="label">{label}</div>
    </div>
</div>
<style>
.thermo-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: fit-content;
    height: auto;
    font-family: system-ui, sans-serif;
    color: var(--primary, #000);
}

.thermo {
    display: flex;
    align-items: flex-end;
    gap: 10px;
    height: 110px;
    position: relative;
    margin: 0 0 12px 0;
}

.tube {
    position: relative;
    width: 18px;
    height: 100px;
    background: linear-gradient(to bottom, #f0f0f0 0%, #e0e0e0 100%);
    border: 2.5px solid #b0b0b0;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1);
}

:global(html.dark-mode) .tube {
    background: linear-gradient(to bottom, var(--gray-gradient-light) 0%, var(--gray-gradient-mid) 100%);
    border-color: var(--gray-gradient-dark);
}

.fill {
    position: absolute;
    bottom: 0;
    width: 100%;
    background: linear-gradient(to top, #e11d48 0%, #ff6b9d 100%);
    transition: height 0.6s ease-in-out;
    box-shadow: 0 -2px 8px rgba(225, 29, 72, 0.4);
}

.labels {
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    height: 110px;
    font-size: 13px;
    font-weight: 500;
    color: var(--secondary, #444);
}

.readout {
    margin-top: 14px;
    text-align: center;
    max-width: 120px;
}

.value {
    font-size: 19px;
    font-weight: 700;
    line-height: 20px;
    margin-bottom: 2px;
    color: var(--primary, #000);
}

.label {
    font-size: 15px;
    font-weight: 400;
    line-height: 1.3;
    word-wrap: break-word;
    color: var(--primary, #000);
}
</style>

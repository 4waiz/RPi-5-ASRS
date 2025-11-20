<script>
    let { value = 100, unit = "km/h", label = "Label" } = $props();
</script>

<div class="compinent-conternar">
    <div class="value-conternrt">
        <p class="value">
            {value}
            <samp class="unit">{unit}</samp>
        </p>
    </div>
    <p class="label">{label}</p>
</div>

<style>
.compinent-conternar {
    display: flex;
    flex-direction: column;
    gap: 4px;
    width: max-content;
    height: auto;
}

.value-conternrt {
    display: flex;
    align-items: baseline;
    gap: 4;
}

.value {
    margin: 0;
    color: var(--primary, #000);
    font-size: 25px;
    font-weight: 700;
    line-height: 1;
    white-space: nowrap;
}

.unit {
    margin-left: 0px;
    color: var(--secondary, rgba(0, 0, 0, 0.68));
    font-size: 14px;
    font-weight: 400;
    line-height: 1;
}

.label {
    margin: 0;
    color: var(--primary, #000);
    font-size: 18px;
    font-weight: 400;
    line-height: 1.2;
    opacity: 0.9;
}
</style>
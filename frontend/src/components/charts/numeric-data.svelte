<script>
    let { value = 100, unit = "km/h", label = "Label" } = $props();
</script>

<div class="component-container">
    <div class="value-container">
        <p class="value">
            {value}
            <samp class="unit">{unit}</samp>
        </p>
    </div>
    <p class="label">{label}</p>
</div>

<style>
.component-container {
    display: flex;
    flex-direction: column;
    gap: 4px;
    width: max-content;
    height: auto;
}

.value-container {
    display: flex;
    align-items: baseline;
    gap: 4;
}

.value {
    margin: 0;
    color: #000;
    font-size: 25px;
    font-weight: 700;
    line-height: 1;
    white-space: nowrap;
}

.unit {
    margin-left: 0px;
    color: rgba(0, 0, 0, 0.68);
    font-size: 14px;
    font-weight: 400;
    line-height: 1;
}

.label {
    margin: 0;
    color: #000;
    font-size: 18px;
    font-weight: 400;
    line-height: 1.2;
    opacity: 0.9;
    width: 112px;
      white-space: normal;
}
</style>
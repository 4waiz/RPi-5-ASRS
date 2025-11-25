<script>
    import alertRed from '../../assets/Icons/alert-red.svg?url';
    import alertYellow from '../../assets/Icons/alert-yallow.svg?url';

    let { Massage, Type, Time } = $props();
    let iconPath = $state(Type === "Alert" ? alertRed : alertYellow);
</script>

<div class="alert-container" class:alert-type={Type === "Alert"} class:warning-type={Type !== "Alert"}>
    <div class="alert-content">
        <img src={iconPath} alt="My icon" class="alert-icon" />
        <p class="alert-message">
            {Massage}
        </p>
    </div>
    <span class="alert-timestamp">
        {Time}
    </span>
</div>
<style>
.alert-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 12px;
    height: 32px;
    border: 1px solid var(--border);
    border-radius: 8px;
    align-self: stretch;
    transition: all 0.3s ease;
}

.alert-container.alert-type {
    background-color: var(--surface-critical);
    border-color: var(--danger);
}

.alert-container.warning-type {
    background-color: var(--surface-warning);
    border-color: var(--warning);
}

.alert-content {
    display: flex;
    align-items: center;
    gap: 8px;
}

.alert-message {
    color: var(--primary);
    font-size: 16px;
    font-weight: 400;
}

.alert-timestamp {
    color: var(--primary);
    font-size: 12px;
    font-style: italic;
}

.alert-icon {
    color: red;
    width: 19px;
    height: 19px;
}
</style>

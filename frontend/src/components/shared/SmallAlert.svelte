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
    border: 1px solid var(--border, rgba(0, 0, 0, 0.08));
    border-radius: 8px;
    align-self: stretch;
    transition: all 0.3s ease;
}

.alert-container.alert-type {
    background-color: #EDD1D1;
}

.alert-container.warning-type {
    background-color: #EDEBD1;
}

:global(html.dark-mode) .alert-container.alert-type {
    background-color: rgba(239, 68, 68, 0.2);
    border-color: rgba(239, 68, 68, 0.4);
}

:global(html.dark-mode) .alert-container.warning-type {
    background-color: rgba(251, 191, 36, 0.2);
    border-color: rgba(251, 191, 36, 0.4);
}

.alert-content {
    display: flex;
    align-items: center;
    gap: 8px;
}

.alert-message {
    color: var(--primary, rgba(0, 0, 0, 0.87));
    font-size: 16px;
    font-weight: 400;
}

.alert-timestamp {
    color: var(--primary, #000);
    font-size: 12px;
    font-style: italic;
}

.alert-icon {
    color: red;
    width: 19px;
    height: 19px;
}

:global(html.dark-mode) .alert-container {
    border-color: #2D3748;
}
</style>

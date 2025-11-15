<script>
    import alertRed from '../../assets/Icons/alert-red.svg?url';
    import alertYellow from '../../assets/Icons/alert-yallow.svg?url';

    let { Massage, Type, Time } = $props();
    let iconPath = $state(Type === "Alert" ? alertRed : alertYellow);
    let color = $state(Type === "Alert" ? "#EDD1D1" : "#EDEBD1");
</script>

<div class="alert-container" style="background-color: {color};">
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
    border: 1px solid rgba(0, 0, 0, 0.08);
    border-radius: 8px;
    align-self: stretch;
}

.alert-content {
    display: flex;
    align-items: center;
    gap: 8px;
}

.alert-message {
    color: rgba(0, 0, 0, 0.87);
    font-size: 16px;
    font-weight: 400;
}

.alert-timestamp {
    color: #000;
    font-size: 12px;
    font-style: italic;
}

.alert-icon {
    color: red;
    width: 19px;
    height: 19px;
}
</style>

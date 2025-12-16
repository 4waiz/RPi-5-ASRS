<script>
    let { value = 30 } = $props();
    import temperatureImage from "../../assets/Temp/Temperature scale.svg";
    import Arrow from "../../assets/Temp/temp arrow.svg";
</script>

<div class="component-container">
    <img class="scaler" src={temperatureImage} alt="Temperature Scale" />
    <img
        class="Arrow"
        src={Arrow}
        alt="Temperature Arrow"
        style="rotate: {(value - 30) * 3.186}deg"
    />
    <div class="text-container">
        <b>{value + "°c"}</b>
        <b class="title">{"Temperature"}</b>
    </div>
</div>

<style>
    .component-container {
        height: 161px; 
    }
    .scaler {
        position: relative;
        left: 2px;
    }
    .Arrow {
        position: relative;
        top: -90px;
        left: 22px;
    }
    .text-container {
        position: relative;
        bottom: 30px;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: -2px;
        margin-top: -60px;
    }
    .title{
        font-weight: 400;
        font-size: 19px;
    }
</style>

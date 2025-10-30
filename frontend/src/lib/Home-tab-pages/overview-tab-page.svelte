<script>
    import CircularProgressBar from "../Statistical charts/Circular-Progress-Bar.svelte";
    import Temperature from "../Statistical charts/Temperature .svelte";
    import NumericData from "../Statistical charts/numeric-data.svelte";
    import AbustractInvontory from "../abustract-invontory.svelte";
    let Cl = [80, 20];
    let Present = 20;
    let slots = [
        "full",
        "full",
        "full",
        "full",
        "full",
        "full",
        "full",
        "empty",
        "empty",
        "partial",
        "partial",
        "partial",
        "partial",
        "partial",
        "partial",
        "partial",
        "partial",
        "partial",
        "partial",
        "partial",
        "partial",
        "partial",
        "partial",
        "partial",
    ];
</script>

<div class="row">
    <div class="column1">
        <CircularProgressBar Name="Pick/Put Accuracy" {Present} />
        <div class="hd"></div>
        <CircularProgressBar Name="Pick/Put Accuracy" {Present} />
    </div>

    <div class="vd"></div>

    <div class="column1">
        <Temperature Temperature={66} max={99} />
        <div class="hd"></div>
        <CircularProgressBar Name="Pick/Put Accuracy" {Present} />
    </div>

    <div class="vd"></div>

    <div class="column2">
        <NumericData />
        <div class="hd"></div>
        <NumericData />
        <div class="hd"></div>
        <NumericData />
    </div>
    <AbustractInvontory {slots} />
</div>

<style>
    .column1 {
        display: flex;
        width: 112.78px;
        flex-direction: column;
        align-items: flex-end;
        gap: 20px;
    }
    .hd {
        height: 1.5px;
        width: 100%;
        background-color: rgba(0, 0, 0, 0.08);
    }
    .column2 {
        display: flex;
        width: 112.78px;
        flex-direction: column;
        align-items: flex-end;
        gap: 40px;
    }
    .row {
        display: flex;
        align-items: flex-start;
        gap: 40.513px;
    }
    .vd {
        flex: 0 0 1.5px; /* fixed 2px width, no growth */
        background-color: #000000; /* your color */
        opacity: 0.08; /* optional: softer line */
        align-self: stretch; /* if you keep flex-start on the row, add this */
        /* no height needed */
    }
</style>

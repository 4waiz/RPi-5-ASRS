<script>
  // props in runes mode
  let { Name, Present, ColorLimes=[80,20], HigherIsBetter=true } = $props(); // e.g. Present = 75

  const radius = 90;
  const circumference = 2 * Math.PI * radius;

  // reactive/computed values
  const dashOffset = $derived(circumference - (Present / 100) * circumference);

  let higherIsBetter = true;
  higherIsBetter = HigherIsBetter;
  
  // optional: dynamic color
  const strokeColor = Present >= ColorLimes[0] ? '#22c55e' : Present >= ColorLimes[1] ? '#facc15' : '#ef4444'
  
  // optional: dynamic color
  const strokeColor2 = Present > ColorLimes[0] ? '#ef4444' : Present > ColorLimes[1] ? '#facc15' : '#22c55e'
</script>

<div class="accuracy-container">
    <div class="circle-wrapper">
        <svg viewBox="0 0 200 200">
            <circle cx="100" cy="100" r={radius} class="circle-bg-track" />
            <circle
                cx="100"
                cy="100"
                r={radius}
                class="circle-progress"
                stroke={HigherIsBetter? strokeColor: strokeColor2}
                stroke-dasharray={circumference}
                stroke-dashoffset={dashOffset}
            />
        </svg>
        <div class="percentage">{Present}%</div>
    </div>
    <div class="label">{Name}</div>
</div>

<style>
    .accuracy-container {
        width:fit-content;
        text-align: center;
    }
    .circle-wrapper {
        position: relative;
        width: 112px;
        height: 112px;
        margin: 0 auto 12px;
    }
    svg {
        position: absolute;
        inset: 0;
        width: 100%;
        height: 100%;
        transform: rotate(-90deg);
    }
    .circle-bg-track {
        fill: none;
        stroke: #C8C8C8;
        stroke-width: 20;
    }
    .circle-progress {
        fill: none;
        stroke-width: 20;
        stroke-linecap: round;
        transition: stroke-dashoffset 0.8s ease-out;
    }
    .percentage {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        font-size: 19px;
        font-weight: bold;
    }
    .label {
        width: 112px;
        font-size: 16px;
        font-weight: 600;
 
    }
</style>

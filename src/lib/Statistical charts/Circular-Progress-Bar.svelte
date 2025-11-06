<script>
  // props in runes mode
  let { Name, Present, ColorLimes = [80, 20], HigherIsBetter = true } = $props();

  const radius = 90;
  const circumference = 2 * Math.PI * radius;

  // progress
  const dashOffset = $derived(circumference - (Present / 100) * circumference);

  // dynamic colors (derived so they recompute when inputs change)
  const upColor = $derived(
    Present >= ColorLimes[0] ? '#22c55e' : Present >= ColorLimes[1] ? '#facc15' : '#ef4444'
  );

  const downColor = $derived(
    Present > ColorLimes[0] ? '#ef4444' : Present > ColorLimes[1] ? '#facc15' : '#22c55e'
  );

  // pick which rule to use
  const strokeColor = $derived(HigherIsBetter ? upColor : downColor);
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
        stroke={strokeColor}
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
    width: fit-content;
    text-align: center;
  }
  .circle-wrapper {
    position: relative;
    width: 101px;
    height: 101px;
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
    stroke: #c8c8c8;
    stroke-width: 20;
  }
  .circle-progress {
    fill: none;
    stroke-width: 20;
    stroke-linecap: round;
    transition: stroke-dashoffset 0.8s ease-out, stroke 0.25s ease; /* smooth color change too */
  }
  .percentage {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    font-size: 18px;
    font-weight: bold;
  }
  .label {
    width: 112px;
    font-size: 16px;
    font-weight: 600;
  }
</style>

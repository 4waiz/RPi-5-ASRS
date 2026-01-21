<script>
  import { t } from "../../lib/i18n";
  let {
    unit,
    active = false,
    hideCount = false,
    hideArrow = false,
    onOpen = () => {},
  } = $props();
</script>

<button class="unit-card" class:active onclick={() => onOpen()}>
  <div class="thumb">
    <img src={unit.image} alt="" loading="lazy" decoding="async" />
  </div>

  <div class="meta">
    <div class="name">{unit.translatedName || unit.name}</div>
    <div class="id">( ID: {unit.id} )</div>
  </div>

  <div class="right">
    <span class="subcount" class:hidden={active || hideCount}>
      {unit.subcomponents.length}
      {$t("components.subcomponents")}
    </span>
    <svg
      class="chev"
      class:hidden={hideArrow}
      width="22"
      height="22"
      viewBox="0 0 24 24"
      aria-hidden="true"
    >
      <path
        d="M9 6l6 6-6 6"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      />
    </svg>
  </div>
</button>

<style>
  .unit-card {
    width: 100%;
    display: grid;
    grid-template-columns: 64px 1fr auto;
    align-items: center;
    gap: 12px;
    padding: 17px 34px 17px 26px;
    border-radius: 17px;
    border: none;
    text-align: left;
    cursor: pointer;
    transition: all 0.3s ease;
    touch-action: manipulation;
    -webkit-tap-highlight-color: var(--shadow-light);
    user-select: none;
    caret-color: transparent;
    border: rgba(255, 255, 255, 1) 2px solid;
    margin-bottom: 18px;
    background: rgba(255, 255, 255, 0.50);
  }

  .unit-card:active {
    transform: scale(0.995);
  }

  .unit-card.active {
    border: 2px solid var(--brand, #ff5622);
    background: #ff562218;
    border-radius: 17px;
  }

  .thumb {
    width: 64px;
    height: 64px;
    border-radius: 12px;
    background: #CAD6E6;
    display: grid;
    place-items: center;
    overflow: hidden;
    transition: background D0.3s ease;
  }

  .thumb img {
    max-width: 56px;
    max-height: 56px;
    object-fit: contain;
  }

  .meta .name {
    font-size: 0.95rem;
    font-weight: 650;
    color: var(--primary, #222);
    caret-color: transparent;
    min-width: 200px;
  }

  .meta .id {
    margin-top: 1px;
    font-size: 0.8rem;
    color: var(--secondary, #717171);
    caret-color: transparent;
  }

  .right {
    display: flex;
    align-items: center;
    gap: 6px;
    color: var(--secondary, #6d6d6d);
    justify-self: end;
    caret-color: transparent;
    font-size: 0.8rem;
  }

  .subcount {
    white-space: nowrap;
    display: inline-block;
    min-width: 10ch;
    text-align: right;
    caret-color: transparent;
  }

  .subcount.hidden {
    visibility: hidden;
  }

  .chev {
    opacity: 0.7;
  }

  .chev.hidden {
    visibility: hidden;
  }
</style>

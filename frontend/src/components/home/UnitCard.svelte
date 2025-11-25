<script>
  import { t } from "../../lib/i18n";
  let { unit, active = false, hideCount = false, hideArrow = false, onOpen = () => {} } = $props();
</script>

<button
  class="unit-card"
  class:active={active}
  onclick={() => onOpen()}
>
  <div class="thumb"><img src={unit.image} alt="" loading="lazy" decoding="async" /></div>

  <div class="meta">
    <div class="name">{unit.translatedName || unit.name}</div>
    <div class="id">( ID: {unit.id} )</div>
  </div>

  <div class="right">
    <span class="subcount" class:hidden={active || hideCount}>
      {unit.subcomponents.length} {$t('components.subcomponents')}
    </span>
    <svg class="chev" class:hidden={hideArrow} width="22" height="22" viewBox="0 0 24 24" aria-hidden="true">
      <path d="M9 6l6 6-6 6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
  </div>
</button>

<style>
  .unit-card {
    width: 100%;
    display: grid;
    grid-template-columns: 92px 1fr auto;
    align-items: center;
    gap: 18px;
    padding: 22px 32px 22px 22px;
    border-radius: 18px;
    background: var(--bg-card, #fff);
    border: 1px solid var(--border, #ececec);
    box-shadow: 0 2px 1px var(--shadow-light), 0 16px 24px var(--shadow-light);
    text-align: left;
    cursor: pointer;
    transition: all 0.3s ease;
    touch-action: manipulation;
    -webkit-tap-highlight-color: var(--shadow-light);
    user-select: none;
    caret-color: transparent;
  }

  .unit-card:active {
    transform: scale(0.995);
  }

  .unit-card.active {
    border: 2px solid var(--brand, #ff5b2e);
    box-shadow: 0 0 0 2px var(--focus-ring);
  }

  .thumb {
    width: 92px;
    height: 92px;
    border-radius: 16px;
    background: var(--bg-page, #f4f4f4);
    display: grid;
    place-items: center;
    overflow: hidden;
    transition: background 0.3s ease;
  }

  .thumb img {
    max-width: 80px;
    max-height: 80px;
    object-fit: contain;
  }

  .meta .name {
    font-size: 1.1rem;
    font-weight: 650;
    color: var(--primary, #222);
    caret-color: transparent;
  }

  .meta .id {
    margin-top: 2px;
    font-size: 0.92rem;
    color: var(--secondary, #717171);
    caret-color: transparent;
  }

  .right {
    display: flex;
    align-items: center;
    gap: 8px;
    color: var(--secondary, #6d6d6d);
    justify-self: end;
    caret-color: transparent;
  }

  .subcount {
    white-space: nowrap;
    display: inline-block;
    min-width: 12ch;
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

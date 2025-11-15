<script>
  let { unit, active = false, hideCount = false, hideArrow = false, onOpen = () => {} } = $props();
</script>

<button
  class="unit-card"
  class:active={active}
  onclick={onOpen}
>
  <div class="thumb"><img src={unit.image} alt="" loading="lazy" decoding="async" /></div>

  <div class="meta">
    <div class="name">{unit.name}</div>
    <div class="id">( ID: {unit.id} )</div>
  </div>

  <div class="right">
    <span class="subcount" class:hidden={active || hideCount}>
      {unit.subcomponents.length} subcomponent{unit.subcomponents.length === 1 ? '' : 's'}
    </span>
    <svg class="chev" class:hidden={hideArrow} width="22" height="22" viewBox="0 0 24 24" aria-hidden="true">
      <path d="M9 6l6 6-6 6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
  </div>
</button>

<style>
  .unit-card{width:100%;display:grid;grid-template-columns:92px 1fr auto;align-items:center;gap:18px;
    padding:22px 32px 22px 22px;border-radius:18px;background:#fff;border:1px solid #ececec;
    box-shadow:0 2px 1px rgba(0,0,0,.04),0 16px 24px rgba(0,0,0,.05);text-align:left;cursor:pointer;
    transition:border 160ms ease, box-shadow 160ms ease, transform 120ms ease;
    touch-action:manipulation;-webkit-tap-highlight-color:rgba(0,0,0,0.08);user-select:none;caret-color:transparent}
  .unit-card:hover{border-color:#e5e5e5}
  .unit-card:active{transform:scale(.995)}
  .unit-card.active{border:2px solid #ff5b2e;box-shadow:0 0 0 2px rgba(255,91,46,0.18)}
  .thumb{width:92px;height:92px;border-radius:16px;background:#f4f4f4;display:grid;place-items:center;overflow:hidden}
  .thumb img{max-width:80px;max-height:80px;object-fit:contain}
  .meta .name{font-size:1.1rem;font-weight:650;color:#222;caret-color:transparent}
  .meta .id{margin-top:2px;font-size:.92rem;color:#717171;caret-color:transparent}
  .right{display:flex;align-items:center;gap:8px;color:#6d6d6d;justify-self:end;caret-color:transparent}
  .subcount{white-space:nowrap;display:inline-block;min-width:12ch;text-align:right;caret-color:transparent}
  .subcount.hidden{visibility:hidden}
  .chev{opacity:.7}
  .chev.hidden{visibility:hidden}
</style>

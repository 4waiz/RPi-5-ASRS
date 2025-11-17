<script>
    let { Names, Pages, Icons = [], activeIndex = $bindable(0) } = $props();
    let selectedPage = $derived(Pages[activeIndex]);

    function handleClick(n) {
        activeIndex = n;
    }
</script>

<div class="tab-container">
    <div class="tab-bar">
        {#each Names as name, i}
            <button class={activeIndex === i ? "tab-active" : "tab"} onclick={() => handleClick(i)}>
                <img class="tab-icon" src={(activeIndex===i ? Icons[i]?.active : Icons[i]?.inactive) || ""} alt="" />
                <span class="tab-text">{Names[i]}</span>
            </button>
        {/each}
    </div>
    <div class="devider"></div>

    <slot name="alerts" />

    <div class="content-area">
        <div id="content">
            <svelte:component this={selectedPage} />
        </div>
    </div>
</div>

<style>
.tab-container {
    width: 100%;
    margin: 24px 24px 0 0;
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    height: 100%;
}

.tab-bar {
    height: 48px;
    display: flex;
    padding: 0 24px;
    align-items: flex-end;
    gap: 24px;
}

.tab,
.tab-active {
    display: flex;
    align-items: center;
    gap: 10px;
    width: 155px;
    height: 48px;
    padding: 12px 16px;
    border-radius: 12px 12px 0 0;
    justify-content: center;
    align-items: center;
    font-size: 16px;
    background-color: #ebebeb;
    border: 0;
    text-align: center;
    color: #525252;
    user-select: none;
    caret-color: transparent;
    white-space: nowrap;
    cursor: pointer;
    transition: all 0.2s ease;
}

.tab:hover {
    background-color: #e0e0e0;
}

.tab-active {
    border-top: 2px solid #000;
    border-right: 2px solid #000;
    border-left: 2px solid #000;
    border-bottom: 2px solid #ebebeb;
    color: #e54817;
    font-weight: 600;
    z-index: 2;
}

.tab-icon {
    width: 22px;
    height: 22px;
    display: block;
    flex-shrink: 0;
    transition: transform 0.2s ease;
}

.tab:hover .tab-icon {
    transform: scale(1.1);
}

.tab-active .tab-icon {
    transform: scale(1.05);
}

.tab-text {
    font-weight: 500;
    letter-spacing: 0.02em;
}

.tab-active .tab-text {
    font-weight: 600;
}

.devider {
    background-color: #000;
    width: 100%;
    height: 2px;
    position: relative;
    bottom: 2px;
    z-index: 1;
}

.content-area {
    flex: 1;
    width: 100%;
    margin-top: 30px;
    box-sizing: border-box;
}
</style>
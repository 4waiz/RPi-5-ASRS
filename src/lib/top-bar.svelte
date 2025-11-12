<script>
    let { Names, Pages, Icons = [], activeIndex = $bindable(0) } = $props();
    let classes = $state([]);
    let selectedPage = $state(Pages[activeIndex]);
    
    for (let i = 0; i < Names.length; i++) {
        if (i === activeIndex) {
            classes[i] = "tab-active";
        } else {
            classes[i] = "tab";
        }
    }
    function handleClick(n) {
        for (let i = 0; i < Names.length; i++) {
            if (i == n) {
                classes[i] = "tab-active";
                selectedPage = Pages[i];
                activeIndex = i;
            } else {
                classes[i] = "tab";
            }
        }
    }
</script>

<div class="tab-container">
    <div class="tab-bar">
        {#each Names as name, i}
            <button class={classes[i]} on:click={() => handleClick(i)}>
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
    gap: 8px;
    width: 155px;
    height: 48px;
    padding: 12px 8px;
    border-radius: 12px 12px 0 0;
    justify-content: center;
    align-items: center;
    font-size: 18px;
    background-color: #ebebeb;
    border: 0;
    text-align: center;
    color: #525252;
    user-select: none;
    caret-color: transparent;
    white-space: nowrap;
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
}
</style>
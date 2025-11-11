<script>
    let { Names, Pages } = $props();
    let classes = $state([]);
    let slectedPabge = $state(Pages[0]);
    for (let i = 0; i < Names.length; i++) {
        if (i === 0) {
            classes[i] = "tab-active";
        } else {
            classes[i] = "tab";
        }
    }
    function handleClick(n) {
        for (let i = 0; i < Names.length; i++) {
            if (i == n) {
                classes[i] = "tab-active";
                slectedPabge = Pages[i];
            } else {
                classes[i] = "tab";
            }
        }
    }
</script>

<div class="tab-container">
    <div class="tab-bar">
        {#each Names as name, i}
            <button class={classes[i]} onclick={() => handleClick(i)}>
                <span class="tab-text">{Names[i]}</span>
            </button>
        {/each}
    </div>
    <div class="devider"></div>

    <div class="content-area">
        <div id="content">
            <svelte:component this={slectedPabge} />
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
    width: 140px;
    height: 48px;
    padding: 12px;
    gap: 6.544px;
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
    margin-top: 32px;
}
</style>

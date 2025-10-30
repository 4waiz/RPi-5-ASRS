<script>
    let { Names, Pages } = $props();
    let classes = $state([]);
    let slectedPabge = $state(Pages[0]);

    const clearSelection = () => {
        if (typeof window === "undefined") return;
        const selection = window.getSelection?.();
        selection?.removeAllRanges?.();
    };

    const releaseFocus = (element) => {
        element?.blur?.();
        clearSelection();
    };

    const handleKeydown = (event) => {
        const blockedKeys = ["ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown", "Home", "End"];
        if (blockedKeys.includes(event.key)) {
            event.preventDefault();
            releaseFocus(event.currentTarget);
        }
    };

    for (let i = 0; i < Names.length; i++) {
        if (i === 0) {
            classes[i] = "tab-active";
        } else {
            classes[i] = "tab";
        }
    }
    function handleClick(event, n) {
        for (let i = 0; i < Names.length; i++) {
            if (i == n) {
                classes[i] = "tab-active";
                slectedPabge = Pages[i];
            } else {
                classes[i] = "tab";
            }
        }
        releaseFocus(event?.currentTarget);
    }
</script>

<div class="tab-container">
    <div class="tab-bar">
        {#each Names as name, i}
            <button
                class={classes[i]}
                onmousedown={(event) => event.preventDefault()}
                onclick={(event) => handleClick(event, i)}
                onfocus={(event) => releaseFocus(event.currentTarget)}
                onkeydown={handleKeydown}
            >
                <span class="tab-text">{Names[i]}</span>
            </button>
        {/each}
    </div>
    <div class="devider"></div>

    <div class="content-area">
        <div id="content">
            {#if slectedPabge}
                {@const ActivePage = slectedPabge}
                <ActivePage />
            {/if}
        </div>
    </div>
</div>

<style>
.tab-container {
    width: 100%;
    margin: 32px 32px 0 0;
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    height: 100%;
}

.tab-bar {
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
    font-size: 20px;
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
    height: 1.5px;
    position: relative;
    bottom: 1.5px;
    z-index: 1;
}

.tab:focus,
.tab:focus-visible,
.tab-active:focus,
.tab-active:focus-visible {
    outline: none;
    box-shadow: none;
}

.content-area {
    flex: 1;
    width: 100%;
    margin-top: 32px;
}
</style>

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

.tab-active {
    border-top: 2px solid #000;
    border-right: 2px solid #000;
    border-left: 2px solid #000;
    border-bottom: 2px solid #ebebeb;
    color: #e54817;
    font-weight: 600;
    z-index: 2;
    animation: tabActivate 0.3s ease-out;
}

@keyframes tabActivate {
    0% {
        background-color: #e0e0e0;
        transform: translateY(3px);
    }
    100% {
        background-color: #ebebeb;
        transform: translateY(0);
    }
}

.tab-icon {
    width: 22px;
    height: 22px;
    display: block;
    flex-shrink: 0;
    transition: transform 0.2s ease;
}

/* Overview tab - Slide up animation */
.tab-active:nth-child(1) .tab-icon {
    animation: slideUp 0.5s ease-out;
}

@keyframes slideUp {
    0% {
        opacity: 0;
        transform: translateY(10px);
    }
    100% {
        opacity: 1;
        transform: translateY(0);
    }
}

/* Inventory tab - Rotate bounce animation */
.tab-active:nth-child(2) .tab-icon {
    animation: rotateBounce 0.6s ease-out;
}

@keyframes rotateBounce {
    0% {
        transform: rotate(0deg) scale(0.5);
        opacity: 0;
    }
    50% {
        transform: rotate(180deg) scale(1.2);
    }
    100% {
        transform: rotate(360deg) scale(1);
        opacity: 1;
    }
}

/* Digital Twin tab - Box assembly animation */
.tab-active:nth-child(3) .tab-icon {
    animation: boxAssembly 0.8s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

@keyframes boxAssembly {
    0% {
        opacity: 0;
        transform: scale(0) rotate(-180deg);
        filter: blur(4px);
    }
    30% {
        transform: scale(0.5) rotate(-90deg);
        filter: blur(2px);
    }
    60% {
        opacity: 1;
        transform: scale(1.3) rotate(10deg);
        filter: blur(0px);
    }
    80% {
        transform: scale(0.9) rotate(-5deg);
    }
    100% {
        opacity: 1;
        transform: scale(1) rotate(0deg);
        filter: blur(0px);
    }
}

/* Components tab - Circuit power-up animation */
.tab-active:nth-child(4) .tab-icon {
    animation: powerUp 0.8s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes powerUp {
    0% {
        opacity: 0;
        transform: scale(0.7);
        filter: brightness(0.3) saturate(0);
    }
    25% {
        opacity: 0.5;
        transform: scale(0.85);
        filter: brightness(0.6) saturate(0.5);
    }
    50% {
        opacity: 1;
        transform: scale(1.15);
        filter: brightness(2) saturate(1.5);
    }
    65% {
        transform: scale(0.95);
        filter: brightness(1.3) saturate(1.2);
    }
    80% {
        transform: scale(1.05);
        filter: brightness(1.1) saturate(1.1);
    }
    100% {
        opacity: 1;
        transform: scale(1);
        filter: brightness(1) saturate(1);
    }
}

.tab-text {
    font-weight: 500;
    letter-spacing: 0.02em;
    transition: all 0.3s ease;
}

.tab-active .tab-text {
    font-weight: 600;
    animation: fadeIn 0.4s ease-out;
}

@keyframes fadeIn {
    0% {
        opacity: 0;
        transform: translateX(-5px);
    }
    100% {
        opacity: 1;
        transform: translateX(0);
    }
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

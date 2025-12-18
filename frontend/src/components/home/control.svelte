<script>
    import hhori from "../../assets/inventory/hhori.png";
    import hverti from "../../assets/inventory/hverti.png";
    import hbasecon from "../../assets/inventory/hbasecon.png";
    import innerConvImg from "../../assets/inventory/inner_conv.png";
    import outconvImg from "../../assets/inventory/outterconv.png";

    // ============ ARM CONTROL ============
    const ORANGE_SRC = hhori;
    const BLUE_SRC = hverti;
    const RED_SRC = hbasecon;

    const orange = { x: 442, y: 14, w: 857 };
    const blueHome = { x: 722, y: 31, w: 315 };
    const redHome = { x: 40, y: 246, w: 231 };

    const BLUE_MIN = -222,
        BLUE_MAX = 132;
    const RED_MIN = -144,
        RED_MAX = 282;

    let blueX = 0,
        redY = 0;
    const STEP = 6,
        TICK = 25;
    let timer = null;
    let pressed = { up: false, down: false, left: false, right: false };

    const clamp = (v, min, max) => Math.max(min, Math.min(max, v));

    function move() {
        let dx = 0,
            dy = 0;
        if (pressed.left) dx -= STEP;
        if (pressed.right) dx += STEP;
        if (pressed.up) dy -= STEP;
        if (pressed.down) dy += STEP;
        if (dx !== 0 || dy !== 0) {
            blueX = clamp(blueX + dx, BLUE_MIN, BLUE_MAX);
            redY = clamp(redY + dy, RED_MIN, RED_MAX);
        }
    }

    function startTimer() {
        if (!timer) {
            move();
            timer = setInterval(move, TICK);
        }
    }

    function stopTimer() {
        if (!pressed.up && !pressed.down && !pressed.left && !pressed.right) {
            if (timer) clearInterval(timer);
            timer = null;
        }
    }

    function pressDir(dir) {
        pressed[dir] = true;
        startTimer();
    }
    function releaseDir(dir) {
        pressed[dir] = false;
        stopTimer();
    }

    let keysPressed = {};
    function onKeyDown(e) {
        if (keysPressed[e.key]) return;
        keysPressed[e.key] = true;
        if (e.key === "ArrowLeft") pressDir("left");
        if (e.key === "ArrowRight") pressDir("right");
        if (e.key === "ArrowUp") pressDir("up");
        if (e.key === "ArrowDown") pressDir("down");
    }
    function onKeyUp(e) {
        keysPressed[e.key] = false;
        if (e.key === "ArrowLeft") releaseDir("left");
        if (e.key === "ArrowRight") releaseDir("right");
        if (e.key === "ArrowUp") releaseDir("up");
        if (e.key === "ArrowDown") releaseDir("down");
    }

    $: horizontalPercent = ((blueX - BLUE_MIN) / (BLUE_MAX - BLUE_MIN)) * 100;
    $: verticalPercent = ((redY - RED_MIN) / (RED_MAX - RED_MIN)) * 100;

    // ============ CONVEYOR CONTROL ============
    let innerDirection = null;
    let outerConveyorType = "output";
    let outerDirection = null;
    const rotation = 225;

    // Third belt (side conveyor) direction - controlled by dedicated left/right buttons
    let thirdBeltDirection = null;

    const innerUpperBelt = [
        { x: 37.4, y: 17.4 },
        { x: 48.5, y: 25.7 },
        { x: 57.2, y: 32.2 },
        { x: 66.4, y: 38.2 },
        { x: 75.3, y: 44.9 },
        { x: 85.7, y: 52.1 },
    ];
    const innerLowerBelt = [
        { x: 17.4, y: 33.3 },
        { x: 27.5, y: 40.9 },
        { x: 35.8, y: 47.2 },
        { x: 43.8, y: 52.5 },
        { x: 52.1, y: 58.1 },
        { x: 59.0, y: 63.5 },
        { x: 66.9, y: 68.6 },
    ];
    const innerThirdBelt = [
        { x: 24.3, y: 46.4 },
        { x: 31.8, y: 52.6 },
        { x: 39.0, y: 58.0 },
        { x: 47.2, y: 63.6 },
    ];
    const thirdBeltRotation = 219;

    const outerLeftBelt = [
        { x: 59.2, y: 82.6 },
        { x: 49.7, y: 74.5 },
        { x: 44.9, y: 70.3 },
        { x: 37.1, y: 63.2 },
        { x: 30.8, y: 58.3 },
        { x: 19.5, y: 48.8 },
    ];
    const outerRightBelt = [
        { x: 83.6, y: 60.8 },
        { x: 76.7, y: 54.2 },
        { x: 70.1, y: 47.6 },
        { x: 63.4, y: 42.4 },
        { x: 56.8, y: 36.3 },
        { x: 50.2, y: 30.2 },
        { x: 43.9, y: 24.8 },
    ];
</script>

<svelte:window on:keydown={onKeyDown} on:keyup={onKeyUp} />

<div class="manual-control">
    <!-- LEFT COLUMN: Arm -->
    <div class="left-col">
        <div class="column-header">
            <div class="header-icon arm">
                <svg
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                >
                    <path
                        d="M12 2v6m0 12v2M4.93 4.93l4.24 4.24m5.66 5.66l4.24 4.24M2 12h6m12 0h2"
                    />
                </svg>
            </div>
            <span class="header-title">Arm Control</span>
            <span class="header-status"
                >H: {Math.round(horizontalPercent)}% | V: {Math.round(
                    verticalPercent,
                )}%</span
            >
        </div>

        <div class="arm-body">
            <div class="arm-visual">
                <div class="machine">
                    <img
                        class="layer orange"
                        src={ORANGE_SRC}
                        alt="Horizontal rail"
                        style="left:{orange.x}px; top:{orange.y}px; width:{orange.w}px;"
                        draggable="false"
                    />
                    <div
                        class="layer blue"
                        style="left:{blueHome.x}px; top:{blueHome.y}px; width:{blueHome.w}px; transform: translateX({blueX}px);"
                    >
                        <img
                            src={BLUE_SRC}
                            alt="Vertical rail"
                            draggable="false"
                        />
                        <img
                            class="red"
                            src={RED_SRC}
                            alt="Gripper"
                            style="left:{redHome.x}px; top:{redHome.y}px; width:{redHome.w}px; transform: translateY({redY}px);"
                            draggable="false"
                        />
                    </div>
                </div>
            </div>

            <!-- RECTANGULAR BOTTOM CONTROL BAR -->
            <div class="arm-dpad">
                <div class="dpad">
                    <button
                        class="dpad-btn left"
                        class:active={pressed.left}
                        on:mousedown={() => pressDir("left")}
                        on:mouseup={() => releaseDir("left")}
                        on:mouseleave={() => releaseDir("left")}
                        on:touchstart|preventDefault={() => pressDir("left")}
                        on:touchend={() => releaseDir("left")}
                    >
                        <svg
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            stroke-width="2.5"
                            ><path d="M19 12H5M12 5l-7 7 7 7" /></svg
                        >
                    </button>

                    <button
                        class="dpad-btn up"
                        class:active={pressed.up}
                        on:mousedown={() => pressDir("up")}
                        on:mouseup={() => releaseDir("up")}
                        on:mouseleave={() => releaseDir("up")}
                        on:touchstart|preventDefault={() => pressDir("up")}
                        on:touchend={() => releaseDir("up")}
                    >
                        <svg
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            stroke-width="2.5"
                            ><path d="M12 19V5M5 12l7-7 7 7" /></svg
                        >
                    </button>

                    <button
                        class="dpad-btn down"
                        class:active={pressed.down}
                        on:mousedown={() => pressDir("down")}
                        on:mouseup={() => releaseDir("down")}
                        on:mouseleave={() => releaseDir("down")}
                        on:touchstart|preventDefault={() => pressDir("down")}
                        on:touchend={() => releaseDir("down")}
                    >
                        <svg
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            stroke-width="2.5"
                            ><path d="M12 5v14M5 12l7 7 7-7" /></svg
                        >
                    </button>

                    <button
                        class="dpad-btn right"
                        class:active={pressed.right}
                        on:mousedown={() => pressDir("right")}
                        on:mouseup={() => releaseDir("right")}
                        on:mouseleave={() => releaseDir("right")}
                        on:touchstart|preventDefault={() => pressDir("right")}
                        on:touchend={() => releaseDir("right")}
                    >
                        <svg
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            stroke-width="2.5"
                            ><path d="M5 12h14M12 5l7 7-7 7" /></svg
                        >
                    </button>
                </div>
            </div>
        </div>
    </div>

    <!-- RIGHT COLUMN: Conveyors stacked (no scroll) -->
    <div class="right-col">
        <!-- Inner Conveyor -->
        <div class="column-header">
            <div class="header-icon inner">
                <svg
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                >
                    <rect x="2" y="8" width="20" height="8" rx="1" />
                    <circle cx="6" cy="16" r="2" />
                    <circle cx="18" cy="16" r="2" />
                </svg>
            </div>
            <span class="header-title">Inner Conveyor</span>
            <span class="header-status" class:active={innerDirection}
                >{innerDirection ? `Moving ${innerDirection}` : "Idle"}</span
            >
        </div>

        <div class="conv-body">
            <div class="conv-img">
                <div class="image-wrapper">
                    <img src={innerConvImg} alt="Inner Conveyor" />
                    {#if innerDirection}
                        {#each innerUpperBelt as arrow, i}
                            <svg
                                class="arrow"
                                style="top:{arrow.y}%; left:{arrow.x}%;
                  transform:rotate({innerDirection === 'outward'
                                    ? rotation + 180
                                    : rotation}deg);
                  animation-delay:{innerDirection === 'outward'
                                    ? i * 0.15
                                    : (innerUpperBelt.length - 1 - i) * 0.15}s;"
                                viewBox="0 0 24 24"
                                width="12"
                                height="12"
                            >
                                <path
                                    d="M2 12 L18 12 L13 5 M18 12 L13 19"
                                    stroke="#ef4444"
                                    stroke-width="3"
                                    fill="none"
                                    stroke-linecap="round"
                                    stroke-linejoin="round"
                                />
                            </svg>
                        {/each}
                        {#each innerLowerBelt as arrow, i}
                            <svg
                                class="arrow"
                                style="top:{arrow.y}%; left:{arrow.x}%;
                  transform:rotate({innerDirection === 'outward'
                                    ? rotation + 180
                                    : rotation}deg);
                  animation-delay:{innerDirection === 'outward'
                                    ? i * 0.15
                                    : (innerLowerBelt.length - 1 - i) * 0.15}s;"
                                viewBox="0 0 24 24"
                                width="12"
                                height="12"
                            >
                                <path
                                    d="M2 12 L18 12 L13 5 M18 12 L13 19"
                                    stroke="#ef4444"
                                    stroke-width="3"
                                    fill="none"
                                    stroke-linecap="round"
                                    stroke-linejoin="round"
                                />
                            </svg>
                        {/each}
                    {/if}

                    {#if thirdBeltDirection === "left"}
                        {#each innerThirdBelt as arrow, i}
                            <svg
                                class="arrow"
                                style="top:{arrow.y}%; left:{arrow.x}%;
                  transform:rotate({thirdBeltRotation}deg);
                  animation-delay:{(innerThirdBelt.length - 1 - i) * 0.15}s;"
                                viewBox="0 0 24 24"
                                width="12"
                                height="12"
                            >
                                <path
                                    d="M2 12 L18 12 L13 5 M18 12 L13 19"
                                    stroke="#ef4444"
                                    stroke-width="3"
                                    fill="none"
                                    stroke-linecap="round"
                                    stroke-linejoin="round"
                                />
                            </svg>
                        {/each}
                    {:else if thirdBeltDirection === "right"}
                        {#each innerThirdBelt as arrow, i}
                            <svg
                                class="arrow"
                                style="top:{arrow.y}%; left:{arrow.x}%;
                  transform:rotate({thirdBeltRotation + 180}deg);
                  animation-delay:{i * 0.15}s;"
                                viewBox="0 0 24 24"
                                width="12"
                                height="12"
                            >
                                <path
                                    d="M2 12 L18 12 L13 5 M18 12 L13 19"
                                    stroke="#ef4444"
                                    stroke-width="3"
                                    fill="none"
                                    stroke-linecap="round"
                                    stroke-linejoin="round"
                                />
                            </svg>
                        {/each}
                    {/if}
                </div>
            </div>

            <div class="conv-controls">
                <button
                    class="ctrl-btn"
                    class:active={innerDirection === "inward"}
                    on:pointerdown={() => (innerDirection = "inward")}
                    on:pointerup={() => (innerDirection = null)}
                    on:pointerleave={() => (innerDirection = null)}
                >
                    <svg
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="2"
                    >
                        <path d="M19 12H5M12 5l-7 7 7 7" />
                    </svg>
                    In
                </button>

                <button
                    class="ctrl-btn"
                    class:active={innerDirection === "outward"}
                    on:pointerdown={() => (innerDirection = "outward")}
                    on:pointerup={() => (innerDirection = null)}
                    on:pointerleave={() => (innerDirection = null)}
                >
                    <svg
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="2"
                    >
                        <path d="M5 12h14M12 5l7 7-7 7" />
                    </svg>
                    Out
                </button>
            </div>

            <div class="conv-controls">
                <button
                    class="ctrl-btn"
                    class:active={thirdBeltDirection === "left"}
                    on:pointerdown={() => (thirdBeltDirection = "left")}
                    on:pointerup={() => (thirdBeltDirection = null)}
                    on:pointerleave={() => (thirdBeltDirection = null)}
                >
                    <svg
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="2"
                    >
                        <path d="M19 12H5M12 5l-7 7 7 7" />
                    </svg>
                    Left
                </button>

                <button
                    class="ctrl-btn"
                    class:active={thirdBeltDirection === "right"}
                    on:pointerdown={() => (thirdBeltDirection = "right")}
                    on:pointerup={() => (thirdBeltDirection = null)}
                    on:pointerleave={() => (thirdBeltDirection = null)}
                >
                    <svg
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="2"
                    >
                        <path d="M5 12h14M12 5l7 7-7 7" />
                    </svg>
                    Right
                </button>
            </div>
        </div>

        <!-- Outer Conveyor -->
        <div class="column-header">
            <div class="header-icon outer">
                <svg
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                >
                    <rect x="2" y="8" width="20" height="8" rx="1" />
                    <circle cx="6" cy="16" r="2" />
                    <circle cx="18" cy="16" r="2" />
                </svg>
            </div>
            <span class="header-title">Outer Conveyor</span>
            <div class="toggle-group">
                <button
                    class="toggle-btn"
                    class:active={outerConveyorType === "output"}
                    on:click={() => (outerConveyorType = "output")}>OUT</button
                >
                <button
                    class="toggle-btn"
                    class:active={outerConveyorType === "input"}
                    on:click={() => (outerConveyorType = "input")}>IN</button
                >
            </div>
        </div>

        <div class="conv-body">
            <div class="conv-img">
                <div class="image-wrapper">
                    <img src={outconvImg} alt="Outer Conveyor" />
                    {#if outerDirection}
                        {#each outerLeftBelt as arrow, i}
                            <svg
                                class="arrow"
                                style="top:{arrow.y}%; left:{arrow.x}%;
                  transform:rotate({outerDirection === 'outward'
                                    ? rotation + 180
                                    : rotation}deg);
                  animation-delay:{outerDirection === 'outward'
                                    ? (outerLeftBelt.length - 1 - i) * 0.15
                                    : i * 0.15}s;"
                                viewBox="0 0 24 24"
                                width="12"
                                height="12"
                            >
                                <path
                                    d="M2 12 L18 12 L13 5 M18 12 L13 19"
                                    stroke="#ef4444"
                                    stroke-width="3"
                                    fill="none"
                                    stroke-linecap="round"
                                    stroke-linejoin="round"
                                />
                            </svg>
                        {/each}
                        {#each outerRightBelt as arrow, i}
                            <svg
                                class="arrow"
                                style="top:{arrow.y}%; left:{arrow.x}%;
                  transform:rotate({outerDirection === 'outward'
                                    ? rotation + 180
                                    : rotation}deg);
                  animation-delay:{outerDirection === 'outward'
                                    ? (outerRightBelt.length - 1 - i) * 0.15
                                    : i * 0.15}s;"
                                viewBox="0 0 24 24"
                                width="12"
                                height="12"
                            >
                                <path
                                    d="M2 12 L18 12 L13 5 M18 12 L13 19"
                                    stroke="#ef4444"
                                    stroke-width="3"
                                    fill="none"
                                    stroke-linecap="round"
                                    stroke-linejoin="round"
                                />
                            </svg>
                        {/each}
                    {/if}
                </div>
            </div>

            <div class="conv-controls">
                <button
                    class="ctrl-btn"
                    class:active={outerDirection === "inward"}
                    on:pointerdown={() => (outerDirection = "inward")}
                    on:pointerup={() => (outerDirection = null)}
                    on:pointerleave={() => (outerDirection = null)}
                >
                    <svg
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="2"
                    >
                        <path d="M19 12H5M12 5l-7 7 7 7" />
                    </svg>
                    In
                </button>

                <button
                    class="ctrl-btn"
                    class:active={outerDirection === "outward"}
                    on:pointerdown={() => (outerDirection = "outward")}
                    on:pointerup={() => (outerDirection = null)}
                    on:pointerleave={() => (outerDirection = null)}
                >
                    <svg
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="2"
                    >
                        <path d="M5 12h14M12 5l7 7-7 7" />
                    </svg>
                    Out
                </button>
            </div>
        </div>
    </div>
</div>

<style>
    :global(body) {
        margin: 0;
    }

    /* ====== 772x496 HMI AREA ====== */
    .manual-control {
        width: 772px;
        height: 496px;
        display: flex;
        overflow: hidden;
        box-sizing: border-box;
    }

    /* ====== COLUMNS ====== */
    .left-col {
        flex: 1;
        min-width: 0;
        display: flex;
        flex-direction: column;
    }

    .right-col {
        width: 270px;
        flex-shrink: 0;
        display: flex;
        flex-direction: column;
        border-left: 1px solid #d8e0ea;
        overflow: hidden;
    }

    /* ====== HEADERS ====== */
    .column-header {
        height: 34px;
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 0 10px;
        border-bottom: 1px solid #d8e0ea;
        flex-shrink: 0;
    }

    .header-icon {
        width: 22px;
        height: 22px;
        border-radius: 6px;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
    }
    .header-icon svg {
        width: 12px;
        height: 12px;
    }
    .header-icon.arm {
        background: linear-gradient(135deg, #e0e7ff, #c7d2fe);
        color: #4f46e5;
    }
    .header-icon.inner {
        background: linear-gradient(135deg, #dbeafe, #bfdbfe);
        color: #2563eb;
    }
    .header-icon.outer {
        background: linear-gradient(135deg, #fef3c7, #fde68a);
        color: #d97706;
    }

    .header-title {
        font-size: 12px;
        font-weight: 800;
        color: #0f172a;
        letter-spacing: 0.2px;
    }

    .header-status {
        margin-left: auto;
        font-size: 10px;
        font-weight: 700;
        color: #64748b;
        white-space: nowrap;
    }
    .header-status.active {
        color: #16a34a;
    }

    /* ====== ARM AREA (reserve bottom bar space) ====== */
    .arm-body {
        flex: 1;
        min-height: 0;
        position: relative;
        padding-bottom: 96px; /* space for the bottom bar */
    }

    .arm-visual {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 96px; /* arm stops above controls */
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
    }

    .machine {
        position: relative;
        width: 1300px;
        height: 600px;
        transform: scale(0.5);
        transform-origin: center;
        margin-left: -407px;
        margin-top: -59px;
    }

    .layer {
        position: absolute;
        pointer-events: none;
        user-select: none;
    }
    .layer.blue img {
        width: 100%;
        display: block;
    }
    .red {
        position: absolute;
        pointer-events: none;
        user-select: none;
    }

    /* ====== RECTANGULAR BOTTOM CONTROL BAR ====== */
    .arm-dpad {
        position: absolute;
        left: 0;
        right: 0;
        bottom: 0;
        height: 96px;
        padding: 12px 20px;

        display: flex;
        align-items: center;
        justify-content: center;

        border-top: 1px solid #d1d9e6;
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.65);
    }

    .dpad {
        display: grid;
        grid-template-columns: 64px 64px 64px 64px;
        gap: 14px;
        align-items: center;
    }

    .dpad-btn {
        width: 64px;
        height: 56px;
        display: flex;
        align-items: center;
        justify-content: center;

        border-radius: 8px;
        border: 1px solid #cbd5e1;

        background: linear-gradient(180deg, #ffffff 0%, #e5eaf1 100%);
        color: #1e293b;
        cursor: pointer;

        box-shadow:
            0 1px 0 rgba(0, 0, 0, 0.06),
            inset 0 1px 0 rgba(255, 255, 255, 0.9);

        transition:
            background 0.12s,
            transform 0.05s;
    }

    .dpad-btn:hover {
        background: #e2e8f0;
    }

    .dpad-btn:active,
    .dpad-btn.active {
        background: linear-gradient(180deg, #2563eb 0%, #1d4ed8 100%);
        color: #fff;
        transform: translateY(1px);
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.25);
    }

    .dpad-btn svg {
        width: 22px;
        height: 22px;
    }

    /* horizontal layout order */
    .dpad-btn.left {
        grid-column: 1;
    }
    .dpad-btn.up {
        grid-column: 2;
    }
    .dpad-btn.down {
        grid-column: 3;
    }
    .dpad-btn.right {
        grid-column: 4;
    }

    /* ====== RIGHT COLUMN PANELS: 2 fixed halves ====== */
    .right-col > .conv-body:nth-of-type(2),
    .right-col > .conv-body:nth-of-type(4) {
        height: calc((496px - (34px * 2)) / 2);
        border-bottom: 1px solid #d8e0ea;
        overflow: hidden;
    }
    .right-col > .conv-body:nth-of-type(4) {
        border-bottom: none;
    }

    /* ====== CONVEYOR BODY ====== */
    .conv-body {
        display: flex;
        flex-direction: column;
        padding: 8px;
        gap: 6px;
        min-height: 0;
    }

    .conv-img {
        flex: 1;
        min-height: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
    }

    .image-wrapper {
        position: relative;
        display: inline-block;
    }
    .image-wrapper img {
        max-height: 128px;
        width: auto;
        display: block;
    }

    .arrow {
        position: absolute;
        translate: -50% -50%;
        filter: drop-shadow(0 2px 3px rgba(0, 0, 0, 0.18));
        animation: chase 1.8s infinite;
    }
    @keyframes chase {
        0%,
        100% {
            opacity: 0.25;
        }
        20%,
        30% {
            opacity: 1;
        }
    }

    .conv-controls {
        display: flex;
        gap: 6px;
        flex-shrink: 0;
    }

    .ctrl-btn {
        flex: 1;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 6px;
        padding: 8px 6px;
        border: none;
        border-radius: 10px;
        background: #f8fafc;
        color: #334155;
        font-size: 11px;
        font-weight: 800;
        cursor: pointer;
        box-shadow:
            0 1px 0 rgba(15, 23, 42, 0.06),
            inset 0 0 0 1px rgba(15, 23, 42, 0.06);
        transition:
            transform 0.06s,
            background 0.12s;
    }
    .ctrl-btn:active {
        transform: translateY(1px);
    }
    .ctrl-btn.active {
        background: linear-gradient(135deg, #3b82f6, #2563eb);
        color: #fff;
        box-shadow: 0 8px 18px rgba(37, 99, 235, 0.22);
    }
    .ctrl-btn svg {
        width: 14px;
        height: 14px;
    }

    .toggle-group {
        display: flex;
        gap: 2px;
        background: #e2e8f0;
        padding: 2px;
        border-radius: 10px;
        margin-left: auto;
    }
    .toggle-btn {
        padding: 4px 9px;
        border: none;
        border-radius: 8px;
        background: transparent;
        color: #64748b;
        font-size: 10px;
        font-weight: 900;
        cursor: pointer;
    }
    .toggle-btn.active {
        background: #0f172a;
        color: #fff;
    }
</style>

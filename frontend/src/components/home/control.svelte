<script>
    import { onMount, onDestroy } from "svelte";
    import { get } from "svelte/store";
    import { USER_TOKEN } from "../../stores/AppStore.js";
    import hhori from "../../assets/inventory/hhori.png";
    import hverti from "../../assets/inventory/hverti.png";
    import hbasecon from "../../assets/inventory/hbasecon.png";
    import innerConvImg from "../../assets/inventory/inner_conv.png";
    import outconvImg from "../../assets/inventory/outterconv.png";

    // ============================================================================
    // CONFIGURATION
    // ============================================================================
    const RPI_WS_URL = "ws://192.168.208.160:8000";

    // ============================================================================
    // WEBSOCKET STATE
    // ============================================================================
    let ws = null;
    let wsConnected = false;

    // Connect to RPi WebSocket
    function connectWebSocket() {
        if (ws && ws.readyState === WebSocket.OPEN) return;

        ws = new WebSocket(RPI_WS_URL);

        ws.onopen = () => {
            console.log("Connected to RPi WebSocket");
            wsConnected = true;
        };

        ws.onclose = () => {
            console.log("Disconnected from RPi WebSocket");
            wsConnected = false;
            // Reconnect after 3 seconds
            setTimeout(connectWebSocket, 3000);
        };

        ws.onerror = (error) => {
            console.error("WebSocket error:", error);
        };

        ws.onmessage = (event) => {
            console.log("RPi response:", event.data);
        };
    }

    // Send command to RPi via WebSocket
    function sendCommand(command) {
        const token = get(USER_TOKEN);

        if (!token) {
            console.error("No auth token - please login first");
            return;
        }

        if (!ws || ws.readyState !== WebSocket.OPEN) {
            console.error("WebSocket not connected");
            return;
        }

        const message = JSON.stringify({
            command: command,
            token: token
        });

        ws.send(message);
        console.log("Sent command:", command);
    }

    // Stop command (when button released)
    function sendStopCommand(command) {
        const token = get(USER_TOKEN);

        if (!token || !ws || ws.readyState !== WebSocket.OPEN) return;

        const message = JSON.stringify({
            command: `${command}_stop`,
            token: token
        });

        ws.send(message);
        console.log("Sent stop command:", `${command}_stop`);
    }

    onMount(() => {
        connectWebSocket();
    });

    onDestroy(() => {
        if (ws) {
            ws.close();
        }
    });

    // ============================================================================
    // ARM CONTROL
    // ============================================================================
    // Arm positions
    const orange = { x: 442, y: 14, w: 857 };
    const blueHome = { x: 722, y: 31, w: 315 };
    const redHome = { x: 40, y: 246, w: 231 };

    const BLUE_MIN = -222, BLUE_MAX = 132;
    const RED_MIN = -144, RED_MAX = 282;
    const STEP = 6, TICK = 25;

    let blueX = 0, redY = 0;
    let timer = null;
    let pressed = { up: false, down: false, left: false, right: false };

    function move() {
        if (pressed.left) blueX = Math.max(BLUE_MIN, blueX - STEP);
        if (pressed.right) blueX = Math.min(BLUE_MAX, blueX + STEP);
        if (pressed.up) redY = Math.max(RED_MIN, redY - STEP);
        if (pressed.down) redY = Math.min(RED_MAX, redY + STEP);
    }

    function pressDir(dir) {
        pressed[dir] = true;
        if (!timer) { move(); timer = setInterval(move, TICK); }
    }

    function releaseDir(dir) {
        pressed[dir] = false;
        if (!pressed.up && !pressed.down && !pressed.left && !pressed.right) {
            clearInterval(timer);
            timer = null;
        }
    }

    $: horizontalPercent = Math.round(((blueX - BLUE_MIN) / (BLUE_MAX - BLUE_MIN)) * 100);
    $: verticalPercent = Math.round(((redY - RED_MIN) / (RED_MAX - RED_MIN)) * 100);

    // Conveyor state
    let innerDirection = null;
    let thirdBeltDirection = null;
    let outerConveyorType = "output";
    let outerDirection = null;

    // Arrow positions (percentage based)
    const innerArrows = [
        { x: 37, y: 17 }, { x: 57, y: 32 }, { x: 75, y: 45 },
        { x: 17, y: 33 }, { x: 36, y: 47 }, { x: 52, y: 58 }, { x: 67, y: 69 }
    ];
    const thirdBeltArrows = [{ x: 24, y: 46 }, { x: 39, y: 58 }];
    const outerArrows = [
        { x: 50, y: 75 }, { x: 37, y: 63 }, { x: 20, y: 49 },
        { x: 77, y: 54 }, { x: 63, y: 42 }, { x: 50, y: 30 }
    ];
    const ROT = 225;
    const ROT3 = 219;
</script>

<div class="control">
    <!-- ARM PANEL -->
    <section class="panel arm-panel">
        <div class="header">
            <span class="title">Arm Control</span>
            <span class="status">H: {horizontalPercent}% | V: {verticalPercent}%</span>
        </div>

        <div class="arm-visual">
            <div class="machine">
                <img class="layer" src={hhori} alt="Horizontal" style="left:{orange.x}px; top:{orange.y}px; width:{orange.w}px;" />
                <div class="layer blue" style="left:{blueHome.x}px; top:{blueHome.y}px; width:{blueHome.w}px; transform:translateX({blueX}px);">
                    <img src={hverti} alt="Vertical" />
                    <img class="red" src={hbasecon} alt="Gripper" style="left:{redHome.x}px; top:{redHome.y}px; width:{redHome.w}px; transform:translateY({redY}px);" />
                </div>
            </div>
        </div>

        <div class="dpad">
            <button class:active={pressed.left} on:pointerdown={() => pressDir("left")} on:pointerup={() => releaseDir("left")} on:pointerleave={() => releaseDir("left")}>&#9664;</button>
            <button class:active={pressed.up} on:pointerdown={() => pressDir("up")} on:pointerup={() => releaseDir("up")} on:pointerleave={() => releaseDir("up")}>&#9650;</button>
            <button class:active={pressed.down} on:pointerdown={() => pressDir("down")} on:pointerup={() => releaseDir("down")} on:pointerleave={() => releaseDir("down")}>&#9660;</button>
            <button class:active={pressed.right} on:pointerdown={() => pressDir("right")} on:pointerup={() => releaseDir("right")} on:pointerleave={() => releaseDir("right")}>&#9654;</button>
        </div>
    </section>

    <!-- INNER CONVEYOR PANEL -->
    <section class="panel">
        <div class="header">
            <span class="title">Inner Conveyor</span>
            <span class="status" class:active={innerDirection || thirdBeltDirection}>{innerDirection || thirdBeltDirection || "Idle"}</span>
        </div>

        <div class="conv-img">
            <div class="img-wrapper">
                <img src={innerConvImg} alt="Inner Conveyor" />
                {#if innerDirection}
                    {#each innerArrows as a}
                        <span class="arrow" style="top:{a.y}%; left:{a.x}%; transform:rotate({innerDirection === 'outward' ? ROT + 180 : ROT}deg);">&#10148;</span>
                    {/each}
                {/if}
                {#if thirdBeltDirection}
                    {#each thirdBeltArrows as a}
                        <span class="arrow" style="top:{a.y}%; left:{a.x}%; transform:rotate({thirdBeltDirection === 'right' ? ROT3 + 180 : ROT3}deg);">&#10148;</span>
                    {/each}
                {/if}
            </div>
        </div>

        <div class="controls">
            <button class:active={innerDirection === "inward"} on:pointerdown={() => { innerDirection = "inward"; sendCommand("inner_conveyor_in"); }} on:pointerup={() => { innerDirection = null; sendStopCommand("inner_conveyor_in"); }} on:pointerleave={() => { innerDirection = null; sendStopCommand("inner_conveyor_in"); }}>In</button>
            <button class:active={innerDirection === "outward"} on:pointerdown={() => { innerDirection = "outward"; sendCommand("inner_conveyor_out"); }} on:pointerup={() => { innerDirection = null; sendStopCommand("inner_conveyor_out"); }} on:pointerleave={() => { innerDirection = null; sendStopCommand("inner_conveyor_out"); }}>Out</button>
        </div>

        <div class="controls">
            <button class:active={thirdBeltDirection === "left"} on:pointerdown={() => { thirdBeltDirection = "left"; sendCommand("inner_conveyor_left"); }} on:pointerup={() => { thirdBeltDirection = null; sendStopCommand("inner_conveyor_left"); }} on:pointerleave={() => { thirdBeltDirection = null; sendStopCommand("inner_conveyor_left"); }}>Left</button>
            <button class:active={thirdBeltDirection === "right"} on:pointerdown={() => { thirdBeltDirection = "right"; sendCommand("inner_conveyor_right"); }} on:pointerup={() => { thirdBeltDirection = null; sendStopCommand("inner_conveyor_right"); }} on:pointerleave={() => { thirdBeltDirection = null; sendStopCommand("inner_conveyor_right"); }}>Right</button>
        </div>
    </section>

    <!-- OUTER CONVEYOR PANEL -->
    <section class="panel outer-panel">
        <div class="header">
            <span class="title">Outer Conveyor</span>
            <div class="toggle">
                <button class:active={outerConveyorType === "output"} on:click={() => outerConveyorType = "output"}>OUT</button>
                <button class:active={outerConveyorType === "input"} on:click={() => outerConveyorType = "input"}>IN</button>
            </div>
        </div>

        <div class="conv-img">
            <div class="img-wrapper">
                <img src={outconvImg} alt="Outer Conveyor" />
                {#if outerDirection}
                    {#each outerArrows as a}
                        <span class="arrow" style="top:{a.y}%; left:{a.x}%; transform:rotate({outerDirection === 'outward' ? ROT + 180 : ROT}deg);">&#10148;</span>
                    {/each}
                {/if}
            </div>
        </div>

        <div class="controls">
            <button class:active={outerDirection === "inward"} on:pointerdown={() => { outerDirection = "inward"; sendCommand("outer_conveyor_in"); }} on:pointerup={() => { outerDirection = null; sendStopCommand("outer_conveyor_in"); }} on:pointerleave={() => { outerDirection = null; sendStopCommand("outer_conveyor_in"); }}>In</button>
            <button class:active={outerDirection === "outward"} on:pointerdown={() => { outerDirection = "outward"; sendCommand("outer_conveyor_out"); }} on:pointerup={() => { outerDirection = null; sendStopCommand("outer_conveyor_out"); }} on:pointerleave={() => { outerDirection = null; sendStopCommand("outer_conveyor_out"); }}>Out</button>
        </div>
    </section>
</div>

<style>
    .control {
        width: calc(100% + 64px);
        height: 380px;
        display: flex;
        gap: 10px;
        overflow-x: auto;
        position: relative;
        left: -32px;
    }

    .panel {
        flex: 0 0 40%;
        display: flex;
        flex-direction: column;
        border: 2px solid rgba(0,0,0,0.15);
        border-radius: 8px;
        overflow: hidden;
    }

    .arm-panel {
        flex-basis: 48%;
        margin-left: 32px;
    }

    .outer-panel {
        margin-right: 32px;
    }

    .header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 8px 12px;
        border-bottom: 1px solid #ddd;
    }

    .title { font-weight: 700; font-size: 13px; }
    .status { font-size: 11px; color: #666; }
    .status.active { color: #16a34a; }

    .arm-visual {
        flex: 1;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
        margin-right: 48px;
    }

    .machine {
        position: relative;
        width: 1300px;
        height: 600px;
        transform: scale(0.35);
        margin-left: -330px;
        margin-top: -50px;
    }

    .layer { position: absolute; pointer-events: none; }
    .layer.blue img { width: 100%; }
    .red { position: absolute; }

    .dpad {
        display: flex;
        gap: 8px;
        padding: 10px;
        border-top: 1px solid #ddd;
        justify-content: center;
    }

    .dpad button {
        width: 50px;
        height: 44px;
        border: 1px solid #ccc;
        border-radius: 6px;
        background: #fff;
        font-size: 18px;
    }

    .dpad button.active { background: #2563eb; color: #fff; }

    .conv-img {
        flex: 1;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 10px;
    }

    .conv-img img { max-height: 180px; width: auto; }

    .img-wrapper { position: relative; display: inline-block; }

    .arrow {
        position: absolute;
        font-size: 14px;
        color: #ef4444;
        translate: -50% -50%;
    }

    .controls {
        display: flex;
        gap: 8px;
        padding: 8px 10px;
    }

    .controls button {
        flex: 1;
        padding: 10px;
        border: 1px solid #ccc;
        border-radius: 6px;
        background: #fff;
        font-weight: 600;
        font-size: 12px;
    }

    .controls button.active { background: #2563eb; color: #fff; }

    .toggle {
        display: flex;
        gap: 4px;
    }

    .toggle button {
        padding: 4px 10px;
        border: none;
        border-radius: 4px;
        background: #e5e7eb;
        font-size: 10px;
        font-weight: 700;
    }

    .toggle button.active { background: #0f172a; color: #fff; }
</style>

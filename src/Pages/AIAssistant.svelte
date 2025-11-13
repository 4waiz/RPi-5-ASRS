<!-- src/Pages/AIAssistant.svelte -->
<script>
    // --- Imports for the PAGE ---
    import SideBar from "../lib/side-bar.svelte";
    // --- Imports for the CHATBOT ---
    import { onMount } from 'svelte';

    // --- 3D IMPORTS (No .js extension) ---
    import * as THREE from 'three';
    import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
    import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

    // --- START OF FIX: REMOVED all asset imports ---

    // We now use direct string paths to the 'static' folder
    // These paths are relative to the root '/'
    const micIcon = "static/assets/aiassistant/mic.png";
    //const talkingVideoPath = "static/assets/aiassistant/avatar_talking.mp4";
    import talkingVideoPath from "../static/assets/aiassistant/avatar_talking.mp4";
    // 3D Model Paths

    const modelPath = "static/avatar/models/muhammad.glb";
    const neutralAnimPath = "static/avatar/animations/m_neutral.glb";
    const waitingAnimPath = "static/avatar/animations/m_waiting.glb";

    // --- STATE VARIABLES ---

    let messages = [];

    let userInput = "";

    let isRecording = false;

    let sttLang = "ar";

    let isPlayingTTS = false; // This will control which element is visible

    // --- ELEMENT BINDINGS ---
    let chatBoxEl;
    let ttsPlayerEl;
    let canvasContainer; // The <div> for the 3D idle animation
    let talkingVideoEl;  // The <video> for the talking animation
    // --- 3D VARS ---

    let mixer;
    let idleAction;
    const clock = new THREE.Clock();
    const API_BASE = "http://localhost:8000";

    // --- Standard Chat Functions ---
    function resolveUrl(pathOrUrl) {
        if (!pathOrUrl) return "";
        return /^https?:\/\//i.test(pathOrUrl) ? pathOrUrl : `${API_BASE}${pathOrUrl}`;
    }

    function appendMessage(sender, text) {
        messages = [...messages, { sender, text }];
        setTimeout(() => {
            if (chatBoxEl) chatBoxEl.scrollTop = chatBoxEl.scrollHeight;
        }, 0);
    }

    function playTTS(url) {
        console.log("[TTS] Playing:", url);
        const audio = ttsPlayerEl;
        audio.muted = false;
        audio.autoplay = true;
        audio.src = url;
        audio.load();
        audio.play().catch(err => {
            console.warn("[TTS] Autoplay blocked or error:", err);
            stopTalking(); // Call our new stop function if play fails
        });
    }

    // This function stops the video and shows the 3D model
    function stopTalking() {
        isPlayingTTS = false;
        if (talkingVideoEl) {
            talkingVideoEl.pause();
            talkingVideoEl.currentTime = 0; // Rewind the video
        }
    }

    async function sendTextMessage() {
        const text = userInput.trim();
        if (!text) return;
        appendMessage("user", text);
        userInput = "";
        const formData = new FormData();
        formData.append("message", text);
        formData.append("speak", "true");

        try {
            const res = await fetch(resolveUrl("/api/chat"), { method: "POST", body: formData });
            if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
            const data = await res.json();
            appendMessage("bot", data.reply || "(no reply)");

            if (data.audio_url) {
                playTTS(resolveUrl(data.audio_url));
            }

        } catch (err) {
            console.error("chat error:", err);
            appendMessage("bot", "⚠️ Error connecting to server.");
        }
    }

    let mediaRecorder;
    let audioChunks = [];

    async function handleMicClick() {
        if (isRecording) {
            mediaRecorder.stop();
            isRecording = false;
            return;
        }
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream, { mimeType: "audio/webm;codecs/opus" });
            audioChunks = [];
            mediaRecorder.ondataavailable = e => {
                if (e.data && e.data.size > 0) audioChunks.push(e.data);
            };


            mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
                const formData = new FormData();
                formData.append("audio", audioBlob);
                formData.append("lang", sttLang);

                try {
                    const res = await fetch(resolveUrl("/api/voice"), { method: "POST", body: formData });
                    if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
                    const data = await res.json();

                    appendMessage("user", `🎙️ ${data.text || "(Could not transcribe)"}`);
                    appendMessage("bot", data.reply || "(no reply)");

                    if (data.audio_url) {

                        playTTS(resolveUrl(data.audio_url));
                    }

                } catch (err) {
                    console.error("voice error:", err);
                    appendMessage("bot", "⚠️ Voice request failed.");
                }

            };
            mediaRecorder.start();
            isRecording = true;
        } catch (err) {
            console.error("MIC ERROR DETAILS:", err.name, err.message);
            alert(`Microphone Error: ${err.message}. Please check permissions.`);

        }
    }
   
    // --- ONMOUNT: This is where we build the 3D scene ---
    onMount(() => {
        // --- 3D SCENE SETUP (FOR IDLE) ---
        if (canvasContainer) {
            const scene = new THREE.Scene();
            scene.background = new THREE.Color(0xffffff);
            const camera = new THREE.PerspectiveCamera(30, canvasContainer.clientWidth / canvasContainer.clientHeight, 0.1, 1000);
            camera.position.set(0, 1.2, 1.8);
            const ambientLight = new THREE.AmbientLight(0xffffff, 1.5);
            scene.add(ambientLight);
            const directionalLight = new THREE.DirectionalLight(0xffffff, 2);
            directionalLight.position.set(2, 5, 5);
            scene.add(directionalLight);
            directionalLight.target.position.set(0, 0, 0);
            scene.add(directionalLight.target);

            const renderer = new THREE.WebGLRenderer({ antialias: true });
            renderer.setSize(canvasContainer.clientWidth, canvasContainer.clientHeight);
            renderer.setPixelRatio(window.devicePixelRatio);
            renderer.outputColorSpace = THREE.SRGBColorSpace;
            canvasContainer.appendChild(renderer.domElement);
            // --- JSDoc fix for the type error ---

            const controls = new OrbitControls(camera, /** @type {HTMLElement} */ (renderer.domElement));
            controls.target.set(0, 1, 0);
            controls.enableDamping = true;
            controls.enableZoom = false;
            controls.enablePan = false;

            const loader = new GLTFLoader();
            loader.load(modelPath, (gltf) => {
                console.log("✅ 3D Model Loaded Successfully!");
                const model = gltf.scene;
                model.scale.set(1.1, 1.1, 1.1);
                model.position.y = -1;
                scene.add(model);
                mixer = new THREE.AnimationMixer(model);

                // Load Idle Animation
                loader.load(neutralAnimPath, (anim) => {
                    idleAction = mixer.clipAction(anim.animations[0]);
                    idleAction.play();
                });


            }, undefined, (error) => {
                console.error('Error loading 3D model:', error);
            });


            function animate() {
                requestAnimationFrame(animate);
                const delta = clock.getDelta();
                if (mixer) mixer.update(delta);
                controls.update();
                renderer.render(scene, camera);
            }
            animate();

            const onWindowResize = () => {
                if (!canvasContainer) return;
                camera.aspect = canvasContainer.clientWidth / canvasContainer.clientHeight;
                camera.updateProjectionMatrix();
                renderer.setSize(canvasContainer.clientWidth, canvasContainer.clientHeight);
            }

            window.addEventListener('resize', onWindowResize);
            return () => {
                window.removeEventListener('resize', onWindowResize);
                if(renderer) renderer.dispose();

            };

        }



        // --- TTS EVENT LISTENERS (FOR SWAPPING) ---
        if (ttsPlayerEl) {
            ttsPlayerEl.onplay = () => {
                isPlayingTTS = true;
                if(talkingVideoEl) talkingVideoEl.play();
            };

            ttsPlayerEl.onended = stopTalking;
            ttsPlayerEl.onpause = stopTalking;

        }

    });

</script>


<!-- ===================== -->
<!-- HTML MARKUP (Component) -->
<!-- ===================== -->

<div class="main">
    <div>
        <SideBar AlertsNum={5} ActivePage="AI Assistant" />

    </div>

    <div class="content-area">
        <div class="chat-container">
            <h1>EDGE InventoryBot</h1>
            <!-- --- AVATAR WRAPPER --- -->
            <div class="avatar-wrapper">

                <!-- 3D Canvas (Idle State) -->
                <!-- We use an {#if} block to show/hide it -->
                {#if !isPlayingTTS}
                    <div class="avatar-canvas" bind:this={canvasContainer}></div>
                {/if}

                <!-- 2D Video (Talking State) -->
                <!-- We use an {#if} block to show/hide it -->
                {#if isPlayingTTS}
                    <video
                        class="avatar-video"
                        bind:this={talkingVideoEl}
                        src={talkingVideoPath}
                        muted
                        loop
                        playsinline
                    ></video>
                {/if}
            </div>
            <!-- --- END OF AVATAR WRAPPER --- -->


            <div id="chat-box" class="chat-box" bind:this={chatBoxEl}>
                {#each messages as msg}
                    <div class="message {msg.sender}">
                        {msg.text}
                    </div>
                {/each}
            </div>

            <div class="controls">
                <textarea
                    id="user-input"

                    placeholder="Type your message..."
                    bind:value={userInput}
                    on:keypress={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendTextMessage(); } }}
                ></textarea>

                <button id="send-btn" on:click={sendTextMessage}>Send</button>
            
                <button id="mic-btn" class="icon-btn" on:click={handleMicClick}>
                    {#if isRecording}
                        <img src={micIcon} alt="Microphone" style="opacity: 0.5;" />
                    {:else}
                        <img src={micIcon} alt="Microphone" />
                    {/if}
                </button>
            </div>

        
            <div class="stt-lang">
                <span>Speak in:</span>
                <button
                    class="lang-btn"
                    class:active={sttLang === 'ar'}
                    on:click={() => sttLang = 'ar'}
                >
                    Arabic (العربية)
                </button>
                <button
                    class="lang-btn"
                    class:active={sttLang === 'en'}
                    on:click={() => sttLang = 'en'}
                >
                    English
                </button>
            </div>
        </div>
    </div>
</div>

<audio id="tts-player" controls hidden bind:this={ttsPlayerEl}></audio>


<!-- =================== -->
<!-- SCOPED CSS (Styles) -->
<!-- =================== -->

<style>

    /* This is your main page layout style */

    .main {
        width: 100%;
        height: 100vh;
        display: flex;
        gap: 32px;
        background-color: #ebebeb;
        box-sizing: border-box;
        padding-right: 32px;
    }

    /* This centers the chat container */

    .content-area {
        flex: 1;
        height: 100%;
        display: flex;
        justify-content: center;
        align-items: center;
        overflow: auto;
        padding: 32px 0;
        box-sizing: border-box;
    }

    /* All the styles for the chat component */

    .chat-container {
        background: #ffffff;
        border: 1px solid #d2d2d7;
        border-radius: 16px;
        width: 100%;
        height: 100%;
        max-width: 700px;
        max-height: 90vh;
        display: flex;
        flex-direction: column;
        padding: 1rem;
        box-shadow: 0 0 20px rgba(255, 122, 26, 0.2);
        box-sizing: border-box;
    }

    h1 {
        text-align: center;
        color: #ff7a1a;
        margin-bottom: 0.5rem;
    }
    /* --- AVATAR STYLES (UPDATED) --- */

    .avatar-wrapper {
        width: 200px;
        height: 200px;
        display: block;
        margin-left: auto;
        margin-right: auto;
        margin-bottom: 1rem;
        border-radius: 50%;
        border: 4px solid #ff7a1a;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        overflow: hidden;
        position: relative;
        background-color: #ffffff;
    }

    .avatar-canvas {
        width: 100%;
        height: 100%;
        pointer-events: auto;
    }

    .avatar-video {
        width: 100%;
        height: 100%;
        object-fit: cover;
        pointer-events: none;
    }


    /* --- END OF AVATAR STYLES --- */
    .chat-box {
        flex: 1;
        overflow-y: auto;
        background: #f9f9f9;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }

    .message {
        margin: 0.5rem 0;
        line-height: 1.4;
        max-width: 85%;
        padding: 0.5rem 0.75rem;
        border-radius: 12px;
        white-space: pre-wrap;
        word-wrap: break-word;
    }

    .message.user {
        text-align: right;
        color: #c59c22;
        align-self: flex-end;
        background-color: #f0f0f0;
    }

    .message.bot {
        text-align: left;
        color: #1d1d1f;
        align-self: flex-start;
        background-color: #ebebeb;
    }

    .controls {
        display: flex;
        gap: 0.5rem;
    }

    textarea {
        flex: 1;
        resize: none;
        border: 1px solid #d2d2d7;
        border-radius: 8px;
        padding: 0.5rem;
        background: #f9f9f9;
        color: #1d1d1f;
    }

    button {
        background: #ff7a1a;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        cursor: pointer;
        font-weight: bold;
    }

    button:hover {
        background: #ff923a;
    }

    .icon-btn {
        padding: 0.5rem;
        display: flex;
        justify-content: center;
        align-items: center;
    }

    .icon-btn:hover {
        background: #ff923a;
    }

    .icon-btn img {
        width: 24px;  
        height: 24px;
    }

    .stt-lang {
        font-size: 0.9rem;
        margin-top: 0.5rem;
        color: #555;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .lang-btn {
        background: #f0f0f0;
        color: #555;
        border: 1px solid #d2d2d7;
        border-radius: 6px;
        padding: 0.25rem 0.5rem;
        cursor: pointer;
        font-family: "Poppins", sans-serif;
        font-size: 0.8rem;
        transition: all 0.2s ease-in-out;
    }

    .lang-btn:hover {
        background: #e0e0e0;
    }

    .lang-btn.active {
        background: #ff7a1a;
        color: white;
        border-color: #ff7a1a;

    }
</style>
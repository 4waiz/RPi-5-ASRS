<script>
    // --- Imports for the PAGE ---
    import SideBar from "../lib/side-bar.svelte";
    
    // --- Imports for the CHATBOT ---
    import { onMount } from 'svelte';

    // --- START OF FIX: Corrected relative import paths ---
    import micIcon from "../static/assets/aiassistant/mic.png";
    import greetingPoster from "../static/assets/aiassistant/greeting.png";
    import greetingVideo from "../static/assets/aiassistant/greeting2.mp4";
    // --- END OF FIX ---

    // --- STATE VARIABLES ---
    let messages = [];
    let userInput = "";
    let isRecording = false;
    let sttLang = "ar"; 

    // --- ELEMENT BINDINGS ---
    let chatBoxEl;
    let ttsPlayerEl;
    let botMediaEl;

    // The API base URL points to your Python server
    const API_BASE = "http://localhost:8000";

    function resolveUrl(pathOrUrl) {
    if (!pathOrUrl) return "";
    return /^https?:\/\//i.test(pathOrUrl)
        ? pathOrUrl
        : `${API_BASE}${pathOrUrl}`;
    }


    function appendMessage(sender, text) {
        messages = [...messages, { sender, text }];
        setTimeout(() => {
            if (chatBoxEl) {
                chatBoxEl.scrollTop = chatBoxEl.scrollHeight;
            }
        }, 0);
    }

    function playTTS(url) {
        const audio = ttsPlayerEl;
        audio.muted = false;
        audio.autoplay = true;
        audio.src = url;
        audio.load();

        const p = audio.play();
        if (p && typeof p.catch === "function") {
            p.catch(err => {
                console.warn("[TTS] Autoplay blocked or error:", err);
                if (botMediaEl) {
                    botMediaEl.pause();
                    botMediaEl.load(); 
                }
            });
        }
    }

    async function sendTextMessage() {
        const text = userInput.trim();
        if (!text) return;
        if (botMediaEl) botMediaEl.play(); 
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
            } else if (botMediaEl) {
                botMediaEl.pause();
                botMediaEl.load(); 
            }
        } catch (err) {
            console.error("chat error:", err);
            appendMessage("bot", "⚠️ Error connecting to server.");
            if (botMediaEl) {
                botMediaEl.pause();
                botMediaEl.load(); 
            }
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
                if (botMediaEl) botMediaEl.play(); 
                const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
                const formData = new FormData();
                formData.append("audio", audioBlob);
                formData.append("lang", sttLang); 

                try {
                    const res = await fetch(resolveUrl("/api/voice"), { method: "POST", body: formData });
                    if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
                    const data = await res.json();

                    appendMessage("user", `🎙️ ${data.text || "(Could not transcribe)"}`);
                    appendMessage("bot", data.reply || "(no reply)");

                    if (data.audio_url) {
                        playTTS(resolveUrl(data.audio_url));
                    } else if (botMediaEl) {
                        botMediaEl.pause();
                        botMediaEl.load(); 
                    }
                } catch (err) {
                    console.error("voice error:", err);
                    appendMessage("bot", "⚠️ Voice request failed.");
                    if (botMediaEl) {
                        botMediaEl.pause();
                        botMediaEl.load(); 
                    }
                }
            };
            mediaRecorder.start();
            isRecording = true;
        } catch (err) {
            console.error(err);
            alert("Microphone access denied.");
        }
    }

    onMount(() => {
        if (ttsPlayerEl) {
            ttsPlayerEl.onended = () => {
                if (botMediaEl) {
                    botMediaEl.pause(); 
                    botMediaEl.load(); 
                }
            };
            ttsPlayerEl.onpause = () => {
                if (botMediaEl) {
                    botMediaEl.pause(); 
                    botMediaEl.load(); 
                }
            };
        }
    });
</script>

<div class="main">
    <div>
        <SideBar AlertsNum="5" WoriginNum="2" ActivePage="AI Assistant" />
    </div>

    <div class="content-area">

        <div class="chat-container">
            <h1>EDGE InventoryBot</h1>

            <video 
            id="bot-media"
            bind:this={botMediaEl}
            poster={greetingPoster}
            src={greetingVideo}
            muted
            loop
            playsinline>
            </video>

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
        flex: 1; /* Makes it fill all remaining space */
        height: 100%;
        display: flex;
        justify-content: center;
        align-items: center;
        overflow: auto; 
        padding: 32px 0; /* Adds top/bottom padding */
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
        max-height: 90vh; /* Set a max height */
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

    #bot-media {
        width: 200px;
        height: 200px; 
        display: block;
        margin-left: auto;
        margin-right: auto;
        margin-bottom: 1rem;
        border-radius: 50%;
        border: 4px solid #ff7a1a;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        object-fit: cover;
        transition: all 0.2s ease-in-out;
        pointer-events: none;
    }

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
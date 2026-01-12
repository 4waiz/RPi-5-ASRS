<script>
    // --- Imports for the PAGE ---
    import SideBar from "../components/shared/Sidebar.svelte";
   
    // --- Imports for the CHATBOT ---
    import { onMount } from 'svelte';
    import Avatar3D from "../components/aiassistant/Avatar3D.svelte";
 
    const micIcon = "static/assets/aiassistant/mic.png";
 
    // --- STATE VARIABLES ---
    let messages = []; // Visual messages on screen
    let aiSessionHistory = []; // AI's short-term memory (Resets on refresh)
    let userInput = "";
    let isRecording = false;
    let sttLang = "en";
    let isPlayingTTS = false;
 
    // --- ELEMENT BINDINGS ---
    let chatBoxEl;
    let ttsPlayerEl;
   
    //const API_BASE = "http://localhost:8001"; to connect locally
    const API_BASE = "http://192.168.208.146:8001";
 
    // --- Standard Chat Functions ---
    function resolveUrl(pathOrUrl) {
        if (!pathOrUrl) return "";
        return /^https?:\/\//i.test(pathOrUrl) ? pathOrUrl : `${API_BASE}${pathOrUrl}`;
    }
 
    function appendMessage(sender, text, isLoading = false) {
        const newMessage = {
            id: `${sender}-${Date.now()}-${Math.random()}`,
            sender,
            text,
            isLoading
        };
        messages = [...messages, newMessage];
        setTimeout(() => {
            if (chatBoxEl) chatBoxEl.scrollTop = chatBoxEl.scrollHeight;
        }, 0);
        return newMessage;
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
            stopTalking();
        });
    }
 
    // --- STOP TALKING FUNCTION ---
    function stopTalking() {
        isPlayingTTS = false;
        if (ttsPlayerEl) {
            ttsPlayerEl.pause();
            ttsPlayerEl.currentTime = 0;
        }
    }
 
    // --- SEND TEXT MESSAGE ---
    async function sendTextMessage() {
        const text = userInput.trim();
        if (!text) return;
       
        appendMessage("user", text);
        userInput = "";
       
        const thinkingMsg = appendMessage("bot", "", true);
 
        const formData = new FormData();
        formData.append("message", text);
        formData.append("speak", "true");
       
        // 1. Explicitly set Mode
        formData.append("mode", "text");
       
        // 2. Pass Session History (Context)
        formData.append("history", JSON.stringify(aiSessionHistory));
 
        try {
            const res = await fetch(resolveUrl("/api/chat"), { method: "POST", body: formData });
            if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
           
            const data = await res.json();
           
            messages = messages.filter(m => m.id !== thinkingMsg.id);
            appendMessage("bot", data.reply || "(no reply)");
 
            // 3. Update AI Memory with this new exchange
            aiSessionHistory.push([text, data.reply]);
 
            if (data.audio_url) {
                playTTS(resolveUrl(data.audio_url));
            }
        } catch (err) {
            console.error("chat error:", err);
            messages = messages.filter(m => m.id !== thinkingMsg.id);
            appendMessage("bot", "⚠️ Error connecting to server.");
        }
    }
 
    // --- VOICE HANDLING ---
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
               
                let transcribingMsg = null;
                let thinkingMsg = null;
 
                try {
                    // STEP 1: TRANSCRIBE
                    transcribingMsg = appendMessage("user", "Transcribing... 🎙️", true);
                   
                    const transcribeFormData = new FormData();
                    transcribeFormData.append("audio", audioBlob, "recording.webm");
                    transcribeFormData.append("lang", sttLang);
 
                    const res = await fetch(resolveUrl("/api/transcribe"), { method: "POST", body: transcribeFormData });
                    if (!res.ok) throw new Error(`Transcription failed: ${res.status} ${res.statusText}`);
                   
                    const data = await res.json();
                    const userText = data.text || "(Could not transcribe)";
 
                    messages = messages.filter(m => m.id !== transcribingMsg.id);
                    transcribingMsg = null;
                    appendMessage("user", userText);
 
                    // STEP 2: GET BOT REPLY
                    thinkingMsg = appendMessage("bot", "", true);
                   
                    const chatFormData = new FormData();
                    chatFormData.append("message", userText);
                    chatFormData.append("speak", "true");
                   
                    // 1. Explicitly set Mode
                    chatFormData.append('mode', 'voice');
                   
                    // 2. Pass Session History (Context)
                    chatFormData.append("history", JSON.stringify(aiSessionHistory));
 
                    const chatRes = await fetch(resolveUrl("/api/chat"), { method: "POST", body: chatFormData });
                    if (!chatRes.ok) throw new Error(`Chat failed: ${chatRes.status} ${chatRes.statusText}`);
 
                    const chatData = await chatRes.json();
 
                    messages = messages.filter(m => m.id !== thinkingMsg.id);
                    thinkingMsg = null;
                    appendMessage("bot", chatData.reply || "(no reply)");
 
                    // 3. Update AI Memory
                    aiSessionHistory.push([userText, chatData.reply]);
 
                    if (chatData.audio_url) {
                        playTTS(resolveUrl(chatData.audio_url));
                    }
 
                } catch (err) {
                    console.error("voice error:", err);
                    if (transcribingMsg) messages = messages.filter(m => m.id !== transcribingMsg.id);
                    if (thinkingMsg) messages = messages.filter(m => m.id !== thinkingMsg.id);
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
   
    // --- GREETING & HISTORY ---
    const welcomePhrases = [
        "EDGE assistant, at your service. What's up?",
        "I'm all circuits. What's the query?",
        "Boot sequence complete. Fire away!",
        "Ready for your questions... or your best printer joke.",
        "Bot online. Ready for questions."
    ];
 
    async function sendGreeting() {
        const randomPhrase = welcomePhrases[Math.floor(Math.random() * welcomePhrases.length)];
        const lang = "en";
 
        appendMessage("bot", randomPhrase);
 
        try {
            const formData = new FormData();
            formData.append("text", randomPhrase);
            formData.append("lang", lang);
 
            const res = await fetch(resolveUrl("/api/tts"), { method: "POST", body: formData });
            if (!res.ok) throw new Error("TTS request failed");
            const data = await res.json();
           
            if (data.audio_url) playTTS(resolveUrl(data.audio_url));
 
        } catch (err) {
            console.error("Error getting greeting TTS:", err);
        }
    }
   
    onMount(async () => {
        // 1. Setup Audio Listeners
        if (ttsPlayerEl) {
            ttsPlayerEl.onplay = () => { isPlayingTTS = true; };
            ttsPlayerEl.onended = stopTalking;
            ttsPlayerEl.onpause = stopTalking;
        }
 
        // 2. Fetch Chat History (Visual Only)
        try {
            const res = await fetch(resolveUrl("/api/chat/history"));
            if (res.ok) {
                const historyData = await res.json();
                // Map DB format to UI messages
                const dbMessages = historyData.map((msg, i) => ({
                    id: `history-${i}`,
                    sender: msg.sender,
                    text: msg.text,
                    isLoading: false
                }));
                // Show history on screen, but KEEP 'aiSessionHistory' empty
                // This ensures the AI has "0 memory" of these old chats.
                messages = [...dbMessages];
            }
        } catch (err) {
            console.error("Failed to load history:", err);
        }
 
        // 3. Say Hello (After a short delay)
        setTimeout(sendGreeting, 500);
    });
</script>
 
<div class="main">
    <div>
        <SideBar AlertsNum={5} ActivePage="AIAssistant" />
    </div>
 
    <div class="content-area">
        <div class="chat-container">
            <h1>EDGE InventoryBot</h1>
 
            <div class="avatar-wrapper">
                <Avatar3D isTalking={isPlayingTTS} />
               
                {#if isPlayingTTS}
                    <button class="stop-btn" on:click={stopTalking} title="Stop speaking">
                        <span class="stop-icon">■</span> Stop
                    </button>
                {/if}
            </div>
           
            <div id="chat-box" class="chat-box" bind:this={chatBoxEl}>
                {#each messages as msg (msg.id)}
                    <div
                        class="message {msg.sender}"
                        class:pulse-animation={msg.isLoading && msg.text !== ""}
                    >
                        {#if msg.isLoading && msg.text === ""}
                            <div class="typing-indicator">
                                <span></span><span></span><span></span>
                            </div>
                        {:else}
                            {msg.text}
                        {/if}
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
                    class:active={sttLang === 'en'}
                    on:click={() => sttLang = 'en'}
                >
                    English
                </button>
                <button
                    class="lang-btn"
                    class:active={sttLang === 'ar'}
                    on:click={() => sttLang = 'ar'}
                >
                    Arabic (العربية)
                </button>
            </div>
        </div>
    </div>
</div>
 
<audio id="tts-player" controls hidden bind:this={ttsPlayerEl}></audio>
 
<style>
    .main {
        width: 100%;
        height: 100vh;
        display: flex;
        gap: 48px;
        background-color: #ebebeb;
        box-sizing: border-box;
        padding-right: 32px;
    }
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
 
    /* STOP BUTTON STYLES */
    .stop-btn {
        position: absolute;
        bottom: 15px;
        left: 50%;
        transform: translateX(-50%);
        background: rgba(255, 255, 255, 0.9);
        color: #ff7a1a;
        border: 1px solid #ff7a1a;
        display: flex;
        align-items: center;
        gap: 6px;
        padding: 6px 16px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: bold;
        box-shadow: 0 4px 10px rgba(0,0,0,0.15);
        cursor: pointer;
        transition: all 0.2s ease;
        z-index: 10;
    }
    .stop-btn:hover {
        background: #ff7a1a;
        color: white;
        transform: translateX(-50%) scale(1.05);
    }
    .stop-icon {
        font-size: 10px;
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
 
    @keyframes pulse {
      0% { opacity: 0.5; }
      50% { opacity: 1; }
      100% { opacity: 0.5; }
    }
    .message.pulse-animation {
      animation: pulse 1.5s infinite ease-in-out;
    }
 
    @keyframes bounce {
        0%, 60%, 100% { transform: translateY(0); }
        30% { transform: translateY(-6px); }
    }
    .typing-indicator {
        display: flex;
        align-items: center;
        height: 1.4em;
    }
    .message.user .typing-indicator { justify-content: flex-end; }
    .message.bot .typing-indicator { justify-content: flex-start; }
    .typing-indicator span {
        height: 8px;
        width: 8px;
        border-radius: 50%;
        display: block;
        margin: 0 2px;
        animation: bounce 1.2s infinite ease-in-out;
    }
    .message.bot .typing-indicator span { background-color: #8e8e93; }
    .message.user .typing-indicator span { background-color: #c59c22; }
    .typing-indicator span:nth-of-type(2) { animation-delay: -1.0s; }
    .typing-indicator span:nth-of-type(3) { animation-delay: -0.8s; }
</style>
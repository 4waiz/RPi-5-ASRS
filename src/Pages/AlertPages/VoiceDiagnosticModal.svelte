<script>
  import { createEventDispatcher, onDestroy } from 'svelte';
  import { marked } from 'marked';

  const dispatch = createEventDispatcher();

  let isListening = false;
  let transcript = '';
  let aiResponse = '';
  let isProcessing = false;
  let error = '';
  let recognition = null;
  let isSpeaking = false;
  let speechSynthesis = null;
  let currentUtterance = null;
  let viewMode = 'audio'; // 'audio' or 'text'
  let currentAudio = null;
  let conversationHistory = [];
  let isInterruptible = true;
  let audioContext = null;
  let isAudioUnlocked = false;

  function close() {
    stopListening();
    stopSpeaking();
    dispatch('close');
  }

  function unlockAudio() {
    if (isAudioUnlocked) return;
    
    try {
      // Create audio context if it doesn't exist
      if (!audioContext) {
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
      }
      
      // Resume audio context (required for Safari)
      if (audioContext.state === 'suspended') {
        audioContext.resume();
      }
      
      // Create a silent buffer to unlock audio
      const buffer = audioContext.createBuffer(1, 1, 22050);
      const source = audioContext.createBufferSource();
      source.buffer = buffer;
      source.connect(audioContext.destination);
      source.start(0);
      
      isAudioUnlocked = true;
      console.log('Audio unlocked successfully');
    } catch (e) {
      console.error('Failed to unlock audio:', e);
    }
  }

  function startListening() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (!SpeechRecognition) {
      error = 'Speech recognition is not supported in your browser. Please use Chrome, Edge, or Safari.';
      return;
    }

    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = 'en-US';

    recognition.onstart = () => {
      isListening = true;
      error = '';
      transcript = '';
      console.log('Voice recognition started');
    };

    recognition.onresult = (event) => {
      let interimTranscript = '';
      let finalTranscript = '';

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcriptPiece = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          finalTranscript += transcriptPiece;
        } else {
          interimTranscript += transcriptPiece;
        }
      }

      transcript = finalTranscript || interimTranscript;
    };

    recognition.onerror = (event) => {
      console.error('Speech recognition error:', event.error);
      isListening = false;
      
      if (event.error === 'no-speech') {
        error = 'No speech detected. Please try again.';
      } else if (event.error === 'not-allowed') {
        error = 'Microphone access denied. Please allow microphone access and try again.';
      } else {
        error = `Error: ${event.error}`;
      }
    };

    recognition.onend = () => {
      isListening = false;
      console.log('Voice recognition ended');
      
      if (transcript.trim()) {
        processQuery();
      }
    };

    recognition.start();
  }

  function stopListening() {
    if (recognition) {
      recognition.stop();
      isListening = false;
    }
  }

  async function getInstantAcknowledgment(query) {
    try {
      // Quick API call for instant acknowledgment
      const response = await fetch('http://localhost:8000/api/quick-acknowledge', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: query }),
      });

      if (!response.ok) {
        throw new Error('Acknowledgment failed');
      }

      const data = await response.json();
      return data.acknowledgment || "Got it, let me check that for you";
    } catch (err) {
      console.error('Error getting acknowledgment:', err);
      return "Got it, let me check that for you";
    }
  }

  async function speakInstantAcknowledgment(text) {
    // Use OpenAI TTS for natural voice (same as full response)
    try {
      const response = await fetch('http://localhost:8000/api/synthesize-speech', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text: text }),
      });

      if (!response.ok) {
        throw new Error('Speech synthesis failed');
      }

      const audioBlob = await response.blob();
      const audioUrl = URL.createObjectURL(audioBlob);
      
      const audio = new Audio(audioUrl);
      audio.volume = 1.0;
      
      await audio.play();
      
      audio.onended = () => {
        URL.revokeObjectURL(audioUrl);
      };
    } catch (err) {
      console.error('Error playing acknowledgment:', err);
    }
  }

  async function processQuery() {
    if (!transcript.trim()) {
      error = 'No transcript to process';
      return;
    }

    isProcessing = true;
    error = '';   
    aiResponse = '';

    // INSTANT ACKNOWLEDGMENT - plays immediately
    if (viewMode === 'audio') {
      const acknowledgment = await getInstantAcknowledgment(transcript);
      await speakInstantAcknowledgment(acknowledgment);
    }

    try {
      console.log('Sending query to backend:', transcript);
      const response = await fetch('http://localhost:8000/api/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: transcript }),
      });

      console.log('Response status:', response.status);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log('Received data:', data);
      aiResponse = data.response || 'No response received';
      
      // Small delay before full response
      if (viewMode === 'audio' && aiResponse) {
        setTimeout(() => {
          speakResponse(aiResponse);
        }, 1000);
      }
    } catch (err) {
      console.error('Error querying AI:', err);
      error = `Failed to get AI response: ${err.message}. Please ensure the backend server is running on port 8000.`;
    } finally {
      isProcessing = false;
    }
  }

  async function speakResponse(text) {
    console.log('=== Using OpenAI TTS for natural speech ===');
    
    stopSpeaking();

    try {
      isSpeaking = true;
      
      // Call backend to generate natural speech
      const response = await fetch('http://localhost:8000/api/synthesize-speech', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text: text }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // Get audio blob
      const audioBlob = await response.blob();
      const audioUrl = URL.createObjectURL(audioBlob);
      
      // Play audio
      currentAudio = new Audio(audioUrl);
      currentAudio.volume = 1.0;
      
      currentAudio.onplay = () => {
        console.log('Natural speech started playing');
        isSpeaking = true;
      };
      
      currentAudio.onended = () => {
        console.log('Natural speech ended');
        isSpeaking = false;
        URL.revokeObjectURL(audioUrl);
      };
      
      currentAudio.onerror = (e) => {
        console.error('Audio playback error:', e);
        isSpeaking = false;
        error = 'Failed to play the response. You can switch to text mode to read it.';
      };
      
      await currentAudio.play();
      
    } catch (err) {
      console.error('Error generating/playing speech:', err);
      isSpeaking = false;
      error = `Failed to generate speech: ${err.message}. Falling back to text mode.`;
      viewMode = 'text';
    }
  }

  function stopSpeaking() {
    // Stop OpenAI audio
    if (currentAudio) {
      currentAudio.pause();
      currentAudio.currentTime = 0;
      currentAudio = null;
    }
    
    // Also stop browser speech synthesis as fallback
    if (window.speechSynthesis) {
      window.speechSynthesis.cancel();
    }
    
    isSpeaking = false;
  }

  function interruptAndSpeak() {
    // Stop current speech
    stopSpeaking();
    
    // Start listening immediately for follow-up
    startListening();
  }

  function toggleViewMode() {
    const newMode = viewMode === 'audio' ? 'text' : 'audio';
    viewMode = newMode;
    
    if (newMode === 'audio' && aiResponse && !isSpeaking) {
      speakResponse(aiResponse);
    } else if (newMode === 'text') {
      stopSpeaking();
    }
  }

  function replaySpeech() {
    unlockAudio(); // Unlock audio on button click
    if (aiResponse) {
      speakResponse(aiResponse);
    }
  }

  function retryListening() {
    transcript = '';
    aiResponse = '';
    error = '';
    stopSpeaking();
    startListening();
  }

  onDestroy(() => {
    stopListening();
    stopSpeaking();
    
    // Clean up audio context
    if (audioContext) {
      audioContext.close()
    }
  });

  $: formattedResponse = aiResponse ? marked(aiResponse) : '';
</script>

<div class="modal-overlay" on:click={close}>
  <div class="modal-content" on:click|stopPropagation>
    <div class="modal-header">
      <div class="header-content">
        <h2>🎤 Voice AI Diagnosis</h2>
        <p class="header-subtitle">Speak to describe the issue you're experiencing</p>
      </div>
      <button class="close-btn" on:click={close}>
        <svg width="24" height="24" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
        </svg>
      </button>
    </div>

    <div class="modal-body">
      <!-- Voice Input Section -->
      <div class="voice-section">
        <div class="voice-controls">
          {#if !isListening && !transcript && !isProcessing}
            <button class="voice-record-btn" on:click={startListening}>
              <svg width="60" height="60" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"/>
              </svg>
              <span>Click to Start Speaking</span>
            </button>
          {:else if isListening}
            <div class="listening-indicator">
              <div class="pulse-ring"></div>
              <button class="voice-stop-btn" on:click={stopListening}>
                <svg width="40" height="40" fill="currentColor" viewBox="0 0 24 24">
                  <rect x="6" y="6" width="12" height="12" rx="2"/>
                </svg>
              </button>
            </div>
            <p class="listening-text">Listening... Speak now</p>
          {/if}
        </div>

        {#if transcript}
          <div class="transcript-box">
            <div class="transcript-header">
              <strong>Your Query:</strong>
              {#if !isProcessing && !aiResponse}
                <button class="retry-btn" on:click={retryListening}>
                  <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
                  </svg>
                  Retry
                </button>
              {/if}
            </div>
            <p class="transcript-text">{transcript}</p>
          </div>
        {/if}

        {#if error}
          <div class="error-box">
            <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
            {error}
          </div>
        {/if}
      </div>

      <!-- Processing Indicator -->
      {#if isProcessing}
        <div class="processing-section">
          <div class="loading-spinner"></div>
          <p>Processing your query with AI...</p>
        </div>
      {/if}

      <!-- AI Response Section -->
      {#if aiResponse}
        <div class="response-section">
          <div class="response-header">
            <h3>
              <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/>
              </svg>
              AI Diagnosis Result
            </h3>
            
            <div class="view-toggle">
              <button 
                class="toggle-btn" 
                class:active={viewMode === 'audio'}
                on:click={toggleViewMode}
              >
                <svg width="18" height="18" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/>
                </svg>
                Audio
              </button>
              <button 
                class="toggle-btn" 
                class:active={viewMode === 'text'}
                on:click={toggleViewMode}
              >
                <svg width="18" height="18" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M3 18h12v-2H3v2zM3 6v2h18V6H3zm0 7h18v-2H3v2z"/>
                </svg>
                Text
              </button>
            </div>
          </div>

          {#if viewMode === 'audio'}
            <div class="audio-mode">
              <div class="audio-controls">
                {#if isSpeaking}
                  <div class="speaking-indicator">
                    <div class="sound-wave">
                      <span></span>
                      <span></span>
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>
                    <p>AI Assistant is speaking...</p>
                    <div class="speech-controls">
                      <button class="interrupt-btn" on:click={interruptAndSpeak}>
                        <svg width="20" height="20" fill="currentColor" viewBox="0 0 24 24">
                          <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/>
                          <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/>
                        </svg>
                        Interrupt & Ask
                      </button>
                      <button class="stop-speech-btn" on:click={stopSpeaking}>
                        <svg width="20" height="20" fill="currentColor" viewBox="0 0 24 24">
                          <rect x="6" y="6" width="12" height="12" rx="1"/>
                        </svg>
                        Stop
                      </button>
                    </div>
                  </div>
                {:else}
                  <button class="replay-btn" on:click={replaySpeech}>
                    <svg width="24" height="24" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"/>
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                    </svg>
                    Replay Diagnosis
                  </button>
                {/if}
              </div>
              <p class="audio-hint">The AI diagnosis is being spoken. Switch to Text mode to read instead.</p>
            </div>
          {:else}
            <div class="response-content">
              {@html formattedResponse}
            </div>
          {/if}

          <button class="new-query-btn" on:click={retryListening}>
            Ask Another Question
          </button>
        </div>
      {/if}
    </div>
  </div>
</div>

<style>
  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.75);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    padding: 2rem;
  }

  .modal-content {
    background: #ffffff;
    border-radius: 16px;
    width: 100%;
    max-width: 800px;
    max-height: 90vh;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
    border: 1px solid #e0e0e0;
  }

  .modal-header {
    padding: 2rem;
    background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%);
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    border-radius: 16px 16px 0 0;
    color: white;
  }

  .header-content h2 {
    margin: 0 0 0.5rem 0;
    font-size: 1.5rem;
    font-weight: 700;
  }

  .header-subtitle {
    margin: 0;
    opacity: 0.95;
    font-size: 0.95rem;
  }

  .close-btn {
    background: rgba(255, 255, 255, 0.15);
    border: none;
    border-radius: 8px;
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.2s;
    color: white;
  }

  .close-btn:hover {
    background: rgba(255, 255, 255, 0.25);
    transform: rotate(90deg);
  }

  .modal-body {
    overflow-y: auto;
    padding: 2rem;
    background: #ffffff;
    color: #1a1a1a;
  }

  .voice-section {
    text-align: center;
  }

  .voice-controls {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1rem;
    margin-bottom: 2rem;
  }

  .voice-record-btn {
    background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%);
    color: white;
    border: none;
    border-radius: 50%;
    width: 140px;
    height: 140px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    cursor: pointer;
    transition: all 0.3s;
    box-shadow: 0 8px 24px rgba(255, 107, 53, 0.4);
    font-weight: 600;
  }

  .voice-record-btn:hover {
    transform: scale(1.05);
    box-shadow: 0 12px 32px rgba(255, 107, 53, 0.5);
  }

  .voice-record-btn span {
    font-size: 0.9rem;
  }

  .listening-indicator {
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .pulse-ring {
    position: absolute;
    width: 160px;
    height: 160px;
    border: 4px solid #FF6B35;
    border-radius: 50%;
    animation: pulse 1.5s ease-out infinite;
  }

  @keyframes pulse {
    0% {
      transform: scale(0.8);
      opacity: 1;
    }
    100% {
      transform: scale(1.2);
      opacity: 0;
    }
  }

  .voice-stop-btn {
    background: #D32F2F;
    color: white;
    border: none;
    border-radius: 50%;
    width: 100px;
    height: 100px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.3s;
    box-shadow: 0 8px 24px rgba(211, 47, 47, 0.3);
    z-index: 1;
  }

  .voice-stop-btn:hover {
    transform: scale(1.05);
    box-shadow: 0 12px 32px rgba(211, 47, 47, 0.4);
  }

  .listening-text {
    font-size: 1.1rem;
    font-weight: 600;
    color: #FF6B35;
    margin: 1rem 0 0 0;
  }

  .transcript-box {
    background: #f5f5f5;
    border-left: 4px solid #FF6B35;
    padding: 1.5rem;
    border-radius: 8px;
    text-align: left;
    margin-top: 1.5rem;
  }

  .transcript-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.75rem;
  }

  .transcript-header strong {
    color: #333333;
    font-size: 0.9rem;
  }

  .retry-btn {
    background: #FF6B35;
    color: white;
    border: none;
    padding: 0.4rem 0.8rem;
    border-radius: 6px;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 0.4rem;
    font-size: 0.85rem;
    font-weight: 600;
    transition: all 0.2s;
  }

  .retry-btn:hover {
    background: #ff5722;
  }

  .transcript-text {
    margin: 0;
    color: #1a1a1a;
    font-size: 1.05rem;
    line-height: 1.6;
  }

  .error-box {
    background: #ffebee;
    border-left: 4px solid #D32F2F;
    padding: 1rem;
    border-radius: 8px;
    color: #c62828;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-top: 1rem;
  }

  .processing-section {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1rem;
    padding: 2rem;
    margin: 1.5rem 0;
  }

  .loading-spinner {
    width: 50px;
    height: 50px;
    border: 4px solid #e0e0e0;
    border-top: 4px solid #FF6B35;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }

  .processing-section p {
    font-size: 1rem;
    color: #666;
    margin: 0;
  }

  .response-section {
    background: #f9f9f9;
    padding: 1.5rem;
    border-radius: 12px;
    margin-top: 1.5rem;
    border: 1px solid #e0e0e0;
  }

  .response-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
    flex-wrap: wrap;
    gap: 1rem;
  }

  .response-section h3 {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 1.1rem;
    color: #1a1a1a;
    margin: 0;
    font-weight: 700;
  }

  .view-toggle {
    display: flex;
    gap: 0.5rem;
    background: #e0e0e0;
    padding: 0.25rem;
    border-radius: 8px;
  }

  .toggle-btn {
    background: transparent;
    border: none;
    color: #666;
    padding: 0.5rem 1rem;
    border-radius: 6px;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.9rem;
    font-weight: 600;
    transition: all 0.2s;
  }

  .toggle-btn:hover {
    color: #333;
    background: #d0d0d0;
  }

  .toggle-btn.active {
    background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%);
    color: white;
  }

  .audio-mode {
    background: #f5f5f5;
    padding: 2rem;
    border-radius: 8px;
    border-left: 4px solid #FF6B35;
  }

  .audio-controls {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1.5rem;
  }

  .speaking-indicator {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1rem;
  }

  .sound-wave {
    display: flex;
    align-items: center;
    gap: 0.3rem;
    height: 40px;
  }

  .sound-wave span {
    width: 4px;
    background: #FF6B35;
    border-radius: 2px;
    animation: wave 1.2s ease-in-out infinite;
  }

  .sound-wave span:nth-child(1) { animation-delay: 0s; height: 10px; }
  .sound-wave span:nth-child(2) { animation-delay: 0.1s; height: 20px; }
  .sound-wave span:nth-child(3) { animation-delay: 0.2s; height: 30px; }
  .sound-wave span:nth-child(4) { animation-delay: 0.3s; height: 20px; }
  .sound-wave span:nth-child(5) { animation-delay: 0.4s; height: 10px; }

  @keyframes wave {
    0%, 100% { transform: scaleY(1); }
    50% { transform: scaleY(2); }
  }

  .speaking-indicator p {
    color: #FF6B35;
    font-weight: 600;
    margin: 0;
  }

  .stop-speech-btn {
    background: #D32F2F;
    color: white;
    border: none;
    padding: 0.6rem 1.2rem;
    border-radius: 8px;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-weight: 600;
    transition: all 0.2s;
  }

  .stop-speech-btn:hover {
    background: #b71c1c;
  }

  .replay-btn {
    background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%);
    color: white;
    border: none;
    padding: 1rem 2rem;
    border-radius: 12px;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    font-size: 1.05rem;
    font-weight: 600;
    transition: all 0.3s;
    box-shadow: 0 4px 12px rgba(255, 107, 53, 0.3);
  }

  .replay-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(255, 107, 53, 0.4);
  }

  .audio-hint {
    color: #666;
    font-size: 0.9rem;
    margin: 1rem 0 0 0;
    text-align: center;
  }

  .response-content {
    background: #f5f5f5;
    padding: 1.5rem;
    border-radius: 8px;
    border-left: 4px solid #FF6B35;
    line-height: 1.8;
    color: #1a1a1a;
  }

  .response-content :global(h1),
  .response-content :global(h2),
  .response-content :global(h3) {
    color: #1a1a1a;
    margin-top: 1.5rem;
    margin-bottom: 0.75rem;
  }

  .response-content :global(h1:first-child),
  .response-content :global(h2:first-child),
  .response-content :global(h3:first-child) {
    margin-top: 0;
  }

  .response-content :global(strong) {
    color: #FF6B35;
    font-weight: 700;
  }

  .response-content :global(ul),
  .response-content :global(ol) {
    padding-left: 1.5rem;
  }

  .response-content :global(li) {
    margin-bottom: 0.5rem;
  }

  .response-content :global(p) {
    margin-bottom: 1rem;
  }

  .response-content :global(code) {
    background: #e0e0e0;
    padding: 0.2rem 0.4rem;
    border-radius: 4px;
    font-family: monospace;
    font-size: 0.9em;
    color: #FF6B35;
  }

  .new-query-btn {
    margin-top: 1rem;
    padding: 0.75rem 1.5rem;
    background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%);
    color: white;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-weight: 600;
    font-size: 1rem;
    transition: all 0.2s;
    width: 100%;
  }

  .new-query-btn:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(255, 107, 53, 0.3);
  }

  @media (max-width: 768px) {
    .modal-overlay {
      padding: 1rem;
    }

    .modal-header {
      padding: 1.5rem;
    }

    .modal-body {
      padding: 1.5rem;
    }

    .voice-record-btn {
      width: 120px;
      height: 120px;
    }

    .voice-stop-btn {
      width: 80px;
      height: 80px;
    }

    .pulse-ring {
      width: 140px;
      height: 140px;
    }

    .response-header {
      flex-direction: column;
      align-items: flex-start;
    }
  }

  .speech-controls {
    display: flex;
    gap: 1rem;
    align-items: center;
  }

  .interrupt-btn {
    background: #FF6B35;
    color: white;
    border: none;
    padding: 0.6rem 1.2rem;
    border-radius: 8px;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-weight: 600;
    transition: all 0.2s;
  }

  .interrupt-btn:hover {
  background: #ff5722;
  transform: translateY(-1px);
}
</style>


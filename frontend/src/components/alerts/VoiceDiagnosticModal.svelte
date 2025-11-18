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
  let currentAudio = null;
  let acknowledgmentAudio = null;
  let audioContext = null;
  let isAudioUnlocked = false;
  let isPressing = false;
  let isPlayingAcknowledgment = false;
  let viewMode = 'audio'; // 'audio' or 'text'
  let currentAudioUrl = null; // Track the current audio URL for cleanup
  let acknowledgmentAudioUrl = null; // Track the acknowledgment audio URL for cleanup

  function close() {
    // Stop all audio and processing
    stopListening();
    stopSpeaking();

    // Reset all state
    isProcessing = false;
    isSpeaking = false;
    isPlayingAcknowledgment = false;

    dispatch('close');
  }

  async function unlockAudio() {
    if (isAudioUnlocked) return;

    try {
      // Create a silent audio element and play it to unlock audio
      const silentAudio = new Audio('data:audio/mp3;base64,SUQzBAAAAAAAI1RTU0UAAAAPAAADTGF2ZjU4Ljc2LjEwMAAAAAAAAAAAAAAA//tQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAWGluZwAAAA8AAAACAAADhAC7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7v/////////////////////////////////////////////////////////////////AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAATGFtZTMuMTAwVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV//sQZAAP8AAAaQAAAAgAAA0gAAABAAABpAAAACAAADSAAAAETEFNRTMuMTAwVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV');
      silentAudio.volume = 0.01;
      await silentAudio.play();

      isAudioUnlocked = true;
      console.log('Audio unlocked successfully');
    } catch (e) {
      console.error('Failed to unlock audio:', e);
    }
  }

  function handleMouseDown() {
    unlockAudio();
    isPressing = true;
    startListening();
  }

  function handleMouseUp() {
    if (isPressing) {
      isPressing = false;
      stopListening();
    }
  }

  function handleTouchStart(e) {
    e.preventDefault();
    unlockAudio();
    isPressing = true;
    startListening();
  }

  function handleTouchEnd(e) {
    e.preventDefault();
    if (isPressing) {
      isPressing = false;
      stopListening();
    }
  }

  function startListening() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      error = 'Speech recognition is not supported in your browser. Please use Chrome, Edge, or Safari.';
      return;
    }

    recognition = new SpeechRecognition();
    recognition.continuous = true;
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
        error = 'No speech detected. Please hold the button longer and speak clearly.';
      } else if (event.error === 'aborted') {
        error = 'Recording stopped too quickly. Please hold the button while speaking, then release.';
      } else if (event.error === 'not-allowed') {
        error = 'Microphone access denied. Please allow microphone access and try again.';
      } else if (event.error === 'audio-capture') {
        error = 'Microphone not detected. Please check your microphone connection.';
      } else {
        error = `Speech recognition error. Please try again.`;
      }
    };

    recognition.onend = () => {
      isListening = false;
      console.log('Voice recognition ended');

      if (transcript.trim() && !isPressing) {
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

  function getInstantAcknowledgment(query) {
    // Extract key phrases and create specific acknowledgments that mention what they said
    const lowerQuery = query.toLowerCase();

    // Try to extract the specific issue mentioned
    const extractIssue = () => {
      // Look for "issue with X", "problem with X", "X is/isn't working"
      const patterns = [
        /(?:issue|problem|trouble|error).*?with\s+(?:the\s+)?(\w+(?:\s+\w+)?)/i,
        /(\w+(?:\s+\w+)?)\s+(?:is|isn't|not|won't)\s+(\w+)/i,
        /(?:why|what's|whats).*?(\w+(?:\s+\w+)?)/i
      ];

      for (const pattern of patterns) {
        const match = query.match(pattern);
        if (match) {
          return match[1] || match[2];
        }
      }
      return null;
    };

    const specificIssue = extractIssue();

    if (lowerQuery.includes('conveyor') || lowerQuery.includes('belt')) {
      return specificIssue
        ? `Got it, you're reporting ${specificIssue} with the conveyor belt. Let me pull up the diagnostics right now.`
        : `Understood, checking the conveyor belt system. Let me analyze the current status for you.`;
    } else if (lowerQuery.includes('elevator') || lowerQuery.includes('lift')) {
      return specificIssue
        ? `I hear you about ${specificIssue} with the elevator. Pulling up the system diagnostics now.`
        : `Checking the elevator system status. Let me get you the diagnostic information.`;
    } else if (lowerQuery.includes('motor') || lowerQuery.includes('drive')) {
      return specificIssue
        ? `Understood, ${specificIssue} on the motor system. Let me check the diagnostics immediately.`
        : `Got it, analyzing the motor drive system. Checking diagnostics now.`;
    } else if (lowerQuery.includes('sensor') || lowerQuery.includes('detect')) {
      return specificIssue
        ? `I see, ${specificIssue} with the sensor. Let me check the sensor logs right away.`
        : `Checking the sensor systems. Let me pull up the detection logs for you.`;
    } else if (lowerQuery.includes('alarm') || lowerQuery.includes('alert')) {
      return specificIssue
        ? `Got it, ${specificIssue} alarm. Let me retrieve the alert details immediately.`
        : `Understood, checking the alarm status. Pulling up alert details now.`;
    } else if (lowerQuery.includes('temperature') || lowerQuery.includes('temp') || lowerQuery.includes('heat')) {
      return specificIssue
        ? `I hear you, ${specificIssue} with temperature. Checking thermal sensors right now.`
        : `Checking temperature readings. Let me analyze the thermal sensor data.`;
    } else {
      return specificIssue
        ? `Understood, you mentioned ${specificIssue}. Let me check the system diagnostics for you.`
        : `Got it, analyzing your question. Checking the system diagnostics now.`;
    }
  }

  async function speakInstantAcknowledgment(text) {
    try {
      isPlayingAcknowledgment = true;
      console.log('🔊 Playing acknowledgment:', text);

      // Unlock audio first
      await unlockAudio();

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
      acknowledgmentAudioUrl = audioUrl; // Track the URL for cleanup
      console.log('🎵 Acknowledgment audio blob created, size:', audioBlob.size);

      acknowledgmentAudio = new Audio(audioUrl);
      acknowledgmentAudio.volume = 1.0;

      // Wait for the audio to finish playing
      await new Promise((resolve, reject) => {
        acknowledgmentAudio.onended = () => {
          console.log('✅ Acknowledgment audio finished');
          if (acknowledgmentAudioUrl) {
            URL.revokeObjectURL(acknowledgmentAudioUrl);
            acknowledgmentAudioUrl = null;
          }
          acknowledgmentAudio = null;
          resolve();
        };
        acknowledgmentAudio.onerror = (e) => {
          console.error('❌ Acknowledgment audio error:', e);
          if (acknowledgmentAudioUrl) {
            URL.revokeObjectURL(acknowledgmentAudioUrl);
            acknowledgmentAudioUrl = null;
          }
          acknowledgmentAudio = null;
          reject(e);
        };

        acknowledgmentAudio.play()
          .then(() => console.log('▶️ Acknowledgment audio started playing'))
          .catch(reject);
      });

      isPlayingAcknowledgment = false;
    } catch (err) {
      console.error('❌ Error playing acknowledgment:', err);
      isPlayingAcknowledgment = false;
      acknowledgmentAudio = null;
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

    const greetingKeywords = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening', 'greetings'];
    const isGreeting = greetingKeywords.some(keyword => transcript.toLowerCase().includes(keyword));
    const isShortGreeting = isGreeting && transcript.split(' ').length <= 5;

    try {
      // Start fetching the full response immediately
      console.log('Sending query to backend:', transcript);
      const responsePromise = fetch('http://localhost:8000/api/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: transcript }),
      });

      // Play acknowledgment while waiting for the full response (parallel processing)
      if (viewMode === 'audio' && !isShortGreeting) {
        const acknowledgment = getInstantAcknowledgment(transcript);
        await speakInstantAcknowledgment(acknowledgment);
      }

      // Wait for the full response to complete
      const response = await responsePromise;
      console.log('Response status:', response.status);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log('Received data:', data);

      // Store response but don't show it yet if in audio mode
      const responseText = data.response || 'No response received';

      // In audio mode, speak first then show the UI
      // In text mode, show immediately
      if (viewMode === 'audio' && responseText) {
        // Don't set aiResponse yet - let speakResponse do it when audio starts
        await speakResponse(responseText);
      } else {
        // In text mode, show immediately
        aiResponse = responseText;
      }
    } catch (err) {
      console.error('Error querying AI:', err);
      error = `${err.message}. Please ensure the backend server is running.`;
      viewMode = 'text'; // Fall back to text mode on error
    } finally {
      isProcessing = false;
    }
  }

  async function speakResponse(text) {
    console.log('🔊 Playing full AI response');
    console.log('Response text:', text);

    stopSpeaking();

    try {
      isSpeaking = true;

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

      const audioBlob = await response.blob();
      const audioUrl = URL.createObjectURL(audioBlob);
      currentAudioUrl = audioUrl; // Track the URL for cleanup
      console.log('🎵 Full response audio blob created, size:', audioBlob.size);

      currentAudio = new Audio(audioUrl);
      currentAudio.volume = 1.0;

      currentAudio.onplay = () => {
        console.log('▶️ Full response audio started playing');
        isSpeaking = true;
        // Show the AI response UI when audio starts playing
        aiResponse = text;
      };

      currentAudio.onended = () => {
        console.log('✅ Full response audio finished');
        isSpeaking = false;
        if (currentAudioUrl) {
          URL.revokeObjectURL(currentAudioUrl);
          currentAudioUrl = null;
        }
      };

      currentAudio.onerror = (e) => {
        console.error('❌ Full response audio playback error:', e);
        isSpeaking = false;
        if (currentAudioUrl) {
          URL.revokeObjectURL(currentAudioUrl);
          currentAudioUrl = null;
        }
        error = 'Failed to play the response. You can switch to text mode to read it.';
        // Show response even on error so user can read it
        aiResponse = text;
      };

      await currentAudio.play();
      console.log('🎤 Full response play() called successfully');

    } catch (err) {
      console.error('❌ Error generating/playing speech:', err);
      isSpeaking = false;
      error = `Failed to generate speech: ${err.message}. Falling back to text mode.`;
      viewMode = 'text';
      // Show the response in text mode on error
      aiResponse = text;
    }
  }

  function stopSpeaking() {
    // Stop and clean up current audio
    if (currentAudio) {
      try {
        currentAudio.pause();
        currentAudio.currentTime = 0;
        currentAudio.src = ''; // Clear the source
        currentAudio.load(); // Reset the audio element
      } catch (e) {
        console.error('Error stopping current audio:', e);
      }
      currentAudio = null;
    }

    // Revoke current audio URL to free memory
    if (currentAudioUrl) {
      try {
        URL.revokeObjectURL(currentAudioUrl);
      } catch (e) {
        console.error('Error revoking current audio URL:', e);
      }
      currentAudioUrl = null;
    }

    // Stop and clean up acknowledgment audio
    if (acknowledgmentAudio) {
      try {
        acknowledgmentAudio.pause();
        acknowledgmentAudio.currentTime = 0;
        acknowledgmentAudio.src = ''; // Clear the source
        acknowledgmentAudio.load(); // Reset the audio element
      } catch (e) {
        console.error('Error stopping acknowledgment audio:', e);
      }
      acknowledgmentAudio = null;
    }

    // Revoke acknowledgment audio URL to free memory
    if (acknowledgmentAudioUrl) {
      try {
        URL.revokeObjectURL(acknowledgmentAudioUrl);
      } catch (e) {
        console.error('Error revoking acknowledgment audio URL:', e);
      }
      acknowledgmentAudioUrl = null;
    }

    // Cancel any speech synthesis
    if (window.speechSynthesis) {
      window.speechSynthesis.cancel();
    }

    isSpeaking = false;
    isPlayingAcknowledgment = false;
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
    unlockAudio();
    if (aiResponse) {
      speakResponse(aiResponse);
    }
  }

  function retryListening() {
    transcript = '';
    aiResponse = '';
    error = '';
    isPlayingAcknowledgment = false;
    stopSpeaking();
  }

  onDestroy(() => {
    stopListening();
    stopSpeaking();

    if (audioContext) {
      audioContext.close();
    }
  });

  $: formattedResponse = aiResponse ? marked(aiResponse) : '';
</script>

<div class="modal-overlay" on:click={close}>
  <div class="modal-content" on:click|stopPropagation>
    <div class="modal-header">
      <div class="header-content">
        <h2>Voice AI Diagnosis</h2>
        <p class="header-subtitle">Hold to speak, release to get diagnosis</p>
      </div>
      <button class="close-btn" on:click={close} aria-label="Close dialog">
        <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
        </svg>
      </button>
    </div>

    <div class="modal-body">
      <!-- Voice Input Section - Always Visible -->
      <div class="voice-section">
        <div class="ptt-container">
          <button
            class="ptt-button"
            class:active={isPressing}
            class:disabled={isProcessing || isPlayingAcknowledgment || isSpeaking}
            on:mousedown={handleMouseDown}
            on:mouseup={handleMouseUp}
            on:mouseleave={handleMouseUp}
            on:touchstart={handleTouchStart}
            on:touchend={handleTouchEnd}
            on:touchcancel={handleTouchEnd}
            disabled={isProcessing || isPlayingAcknowledgment || isSpeaking}
            aria-label="Push to talk"
          >
            <div class="ptt-ripple" class:active={isPressing}></div>
            <div class="ptt-icon">
              <svg width="36" height="36" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"/>
              </svg>
            </div>
          </button>
          <p class="ptt-instruction">
            {#if isPressing}
              Listening...
            {:else if isProcessing || isPlayingAcknowledgment}
              Processing...
            {:else if isSpeaking}
              Speaking...
            {:else}
              Hold to Speak
            {/if}
          </p>
        </div>
      </div>

      <!-- Transcript Box -->
      {#if transcript}
        <div class="transcript-box" class:show={transcript}>
          <div class="transcript-header">
            <div class="header-label">
              <svg width="16" height="16" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/>
                <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/>
              </svg>
              <strong>Your Query</strong>
            </div>
            {#if !isProcessing && !aiResponse}
              <button class="retry-btn" on:click={retryListening}>
                <svg width="14" height="14" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
                </svg>
                Retry
              </button>
            {/if}
          </div>
          <p class="transcript-text">{transcript}</p>
        </div>
      {/if}

      <!-- Error Box -->
      {#if error}
        <div class="error-box" class:show={error}>
          <svg width="18" height="18" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
          <span>{error}</span>
        </div>
      {/if}

      <!-- Acknowledgment Visual (No Text - Just Animation) -->
      {#if isPlayingAcknowledgment}
        <div class="acknowledgment-section" class:show={isPlayingAcknowledgment}>
          <div class="ack-content">
            <div class="listening-animation">
              <div class="listening-bar"></div>
              <div class="listening-bar"></div>
              <div class="listening-bar"></div>
              <div class="listening-bar"></div>
            </div>
            <p class="ack-status">Processing your request...</p>
          </div>
        </div>
      {/if}

      <!-- Processing Indicator (shows after acknowledgment finishes, before response plays) -->
      {#if isProcessing && !isPlayingAcknowledgment && !isSpeaking}
        <div class="processing-section" class:show={isProcessing}>
          <div class="listening-animation">
            <div class="listening-bar"></div>
            <div class="listening-bar"></div>
            <div class="listening-bar"></div>
            <div class="listening-bar"></div>
          </div>
          <p>Preparing your diagnosis...</p>
        </div>
      {/if}

      <!-- AI Response Section -->
      {#if aiResponse}
        <div class="response-section" class:show={aiResponse}>
          <div class="response-header">
            <h3>
              <svg width="18" height="18" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/>
              </svg>
              AI Diagnosis
            </h3>

            <div class="view-toggle">
              <button
                class="toggle-btn"
                class:active={viewMode === 'audio'}
                on:click={toggleViewMode}
              >
                <svg width="16" height="16" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/>
                </svg>
                Audio
              </button>
              <button
                class="toggle-btn"
                class:active={viewMode === 'text'}
                on:click={toggleViewMode}
              >
                <svg width="16" height="16" fill="currentColor" viewBox="0 0 24 24">
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
                    <p>Playing diagnosis...</p>
                    <button class="stop-speech-btn" on:click={stopSpeaking}>
                      <svg width="16" height="16" fill="currentColor" viewBox="0 0 24 24">
                        <rect x="6" y="6" width="12" height="12" rx="2"/>
                      </svg>
                      Stop
                    </button>
                  </div>
                {:else}
                  <button class="replay-btn" on:click={replaySpeech}>
                    <svg width="22" height="22" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"/>
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                    </svg>
                    Replay Response
                  </button>
                {/if}
              </div>
              <p class="audio-hint">Switch to Text mode to read the diagnosis instead</p>
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
  * {
    -webkit-tap-highlight-color: transparent;
  }

  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.65);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    padding: 2rem;
    animation: fadeIn 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
  }

  @keyframes fadeIn {
    from {
      opacity: 0;
    }
    to {
      opacity: 1;
    }
  }

  .modal-content {
    background: #FFFFFF;
    border-radius: 28px;
    width: 100%;
    max-width: 680px;
    max-height: 90vh;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    box-shadow: 0 32px 64px -12px rgba(0, 0, 0, 0.4), 0 0 0 1px rgba(0, 0, 0, 0.05);
    animation: slideUp 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
  }

  @keyframes slideUp {
    from {
      opacity: 0;
      transform: translateY(32px) scale(0.94);
    }
    to {
      opacity: 1;
      transform: translateY(0) scale(1);
    }
  }

  .modal-header {
    padding: 2rem 2rem 1.75rem 2rem;
    background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%);
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    color: white;
    position: relative;
    overflow: hidden;
  }

  .modal-header::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(135deg, rgba(255,255,255,0.12) 0%, rgba(255,255,255,0) 100%);
    pointer-events: none;
  }

  .header-content {
    position: relative;
    z-index: 1;
  }

  .header-content h2 {
    margin: 0 0 0.4rem 0;
    font-size: 1.5rem;
    font-weight: 600;
    letter-spacing: -0.02em;
  }

  .header-subtitle {
    margin: 0;
    opacity: 0.9;
    font-size: 0.9375rem;
    font-weight: 400;
  }

  .close-btn {
    background: rgba(255, 255, 255, 0.2);
    border: none;
    border-radius: 12px;
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.2s cubic-bezier(0.25, 0.46, 0.45, 0.94);
    color: white;
    position: relative;
    z-index: 1;
  }

  .close-btn:hover {
    background: rgba(255, 255, 255, 0.3);
    transform: scale(1.05);
  }

  .close-btn:active {
    transform: scale(0.95);
    transition: all 0.12s cubic-bezier(0.25, 0.46, 0.45, 0.94);
  }

  .modal-body {
    overflow-y: auto;
    padding: 2.5rem 2rem;
    background: #FAFBFC;
  }

  .voice-section {
    text-align: center;
    margin-bottom: 2rem;
  }

  .ptt-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1.5rem;
  }

  .ptt-button {
    position: relative;
    background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%);
    border: none;
    border-radius: 50%;
    width: 140px;
    height: 140px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.25s cubic-bezier(0.25, 0.46, 0.45, 0.94);
    box-shadow: 0 16px 32px rgba(255, 107, 53, 0.35), 0 4px 12px rgba(255, 107, 53, 0.2);
    user-select: none;
    -webkit-user-select: none;
    touch-action: none;
  }

  .ptt-button:hover:not(:disabled) {
    transform: scale(1.05);
    box-shadow: 0 20px 40px rgba(255, 107, 53, 0.45), 0 8px 16px rgba(255, 107, 53, 0.25);
  }

  .ptt-button:active:not(:disabled),
  .ptt-button.active {
    transform: scale(0.95);
    box-shadow: 0 8px 20px rgba(255, 107, 53, 0.3), 0 2px 8px rgba(255, 107, 53, 0.15);
    transition: all 0.12s cubic-bezier(0.25, 0.46, 0.45, 0.94);
  }

  .ptt-button:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .ptt-ripple {
    position: absolute;
    width: 100%;
    height: 100%;
    border: 4px solid #FF6B35;
    border-radius: 50%;
    opacity: 0;
    transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
  }

  .ptt-ripple.active {
    animation: ripple 1.5s cubic-bezier(0.25, 0.46, 0.45, 0.94) infinite;
  }

  @keyframes ripple {
    0% {
      transform: scale(1);
      opacity: 0.8;
    }
    100% {
      transform: scale(1.6);
      opacity: 0;
    }
  }

  .ptt-icon {
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    z-index: 1;
    filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.15));
  }

  .ptt-instruction {
    font-size: 1.0625rem;
    font-weight: 500;
    color: #4B5563;
    margin: 0;
    transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
  }

  .transcript-box {
    background: #FFFFFF;
    border: 1.5px solid #E5E7EB;
    border-left: 4px solid #FF6B35;
    padding: 1.5rem;
    border-radius: 18px;
    text-align: left;
    margin-bottom: 1.5rem;
    opacity: 0;
    transform: translateY(16px);
    transition: all 0.35s cubic-bezier(0.25, 0.46, 0.45, 0.94);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  }

  .transcript-box.show {
    opacity: 1;
    transform: translateY(0);
  }

  .transcript-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.875rem;
  }

  .header-label {
    display: flex;
    align-items: center;
    gap: 0.625rem;
    color: #4B5563;
  }

  .header-label svg {
    color: #FF6B35;
  }

  .header-label strong {
    font-size: 0.9375rem;
    font-weight: 600;
  }

  .retry-btn {
    background: #FF6B35;
    color: white;
    border: none;
    padding: 0.5625rem 1rem;
    border-radius: 10px;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 0.4375rem;
    font-size: 0.875rem;
    font-weight: 500;
    transition: all 0.2s cubic-bezier(0.25, 0.46, 0.45, 0.94);
    box-shadow: 0 2px 6px rgba(255, 107, 53, 0.25);
  }

  .retry-btn:hover {
    background: #F7931E;
    transform: translateY(-1px);
    box-shadow: 0 4px 10px rgba(255, 107, 53, 0.35);
  }

  .retry-btn:active {
    transform: translateY(0);
    transition: all 0.12s cubic-bezier(0.25, 0.46, 0.45, 0.94);
  }

  .transcript-text {
    margin: 0;
    color: #1F2937;
    font-size: 1.0625rem;
    line-height: 1.65;
  }

  .error-box {
    background: #FEF2F2;
    border: 1.5px solid #FCA5A5;
    border-left: 4px solid #DC2626;
    padding: 1.25rem;
    border-radius: 16px;
    color: #991B1B;
    display: flex;
    align-items: flex-start;
    gap: 0.875rem;
    margin-bottom: 1.5rem;
    font-size: 0.9375rem;
    opacity: 0;
    transform: translateY(16px);
    transition: all 0.35s cubic-bezier(0.25, 0.46, 0.45, 0.94);
    box-shadow: 0 2px 8px rgba(220, 38, 38, 0.08);
  }

  .error-box.show {
    opacity: 1;
    transform: translateY(0);
  }

  .error-box svg {
    flex-shrink: 0;
    margin-top: 0.125rem;
  }

  .acknowledgment-section {
    background: linear-gradient(135deg, rgba(255, 107, 53, 0.08) 0%, rgba(247, 147, 30, 0.05) 100%);
    border: 1.5px solid rgba(255, 107, 53, 0.2);
    border-radius: 18px;
    padding: 1.75rem;
    margin-bottom: 1.5rem;
    opacity: 0;
    transform: translateY(16px);
    transition: all 0.35s cubic-bezier(0.25, 0.46, 0.45, 0.94);
    box-shadow: 0 2px 8px rgba(255, 107, 53, 0.06);
  }

  .acknowledgment-section.show {
    opacity: 1;
    transform: translateY(0);
  }

  .ack-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1.5rem;
  }

  .listening-animation {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    height: 60px;
  }

  .listening-bar {
    width: 6px;
    height: 20px;
    background: linear-gradient(180deg, #FF6B35 0%, #F7931E 100%);
    border-radius: 4px;
    animation: listeningWave 1.2s ease-in-out infinite;
  }

  .listening-bar:nth-child(1) {
    animation-delay: 0s;
  }

  .listening-bar:nth-child(2) {
    animation-delay: 0.15s;
  }

  .listening-bar:nth-child(3) {
    animation-delay: 0.3s;
  }

  .listening-bar:nth-child(4) {
    animation-delay: 0.45s;
  }

  @keyframes listeningWave {
    0%, 100% {
      height: 20px;
      opacity: 0.6;
    }
    50% {
      height: 55px;
      opacity: 1;
    }
  }

  .ack-status {
    margin: 0;
    color: #FF6B35;
    font-size: 1rem;
    font-weight: 600;
    text-align: center;
  }

  .processing-section {
    background: linear-gradient(135deg, rgba(255, 107, 53, 0.08) 0%, rgba(247, 147, 30, 0.05) 100%);
    border: 1.5px solid rgba(255, 107, 53, 0.2);
    border-radius: 18px;
    padding: 1.75rem;
    margin-bottom: 1.5rem;
    opacity: 0;
    transform: translateY(16px);
    transition: all 0.35s cubic-bezier(0.25, 0.46, 0.45, 0.94);
    box-shadow: 0 2px 8px rgba(255, 107, 53, 0.06);
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1.5rem;
  }

  .processing-section.show {
    opacity: 1;
    transform: translateY(0);
  }

  .processing-section p {
    margin: 0;
    color: #FF6B35;
    font-size: 1rem;
    font-weight: 600;
    text-align: center;
  }

  .response-section {
    background: #FFFFFF;
    padding: 2rem;
    border-radius: 20px;
    border: 1.5px solid #E5E7EB;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
    opacity: 0;
    transform: translateY(16px);
    transition: all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
  }

  .response-section.show {
    opacity: 1;
    transform: translateY(0);
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
    gap: 0.625rem;
    font-size: 1.125rem;
    color: #1F2937;
    margin: 0;
    font-weight: 600;
  }

  .view-toggle {
    display: flex;
    gap: 0.5rem;
    background: #F3F4F6;
    padding: 0.375rem;
    border-radius: 14px;
  }

  .toggle-btn {
    background: transparent;
    border: none;
    color: #6B7280;
    padding: 0.5625rem 1rem;
    border-radius: 11px;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 0.4375rem;
    font-size: 0.875rem;
    font-weight: 500;
    transition: all 0.2s cubic-bezier(0.25, 0.46, 0.45, 0.94);
  }

  .toggle-btn:hover {
    color: #374151;
    background: #E5E7EB;
  }

  .toggle-btn.active {
    background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%);
    color: white;
    box-shadow: 0 2px 8px rgba(255, 107, 53, 0.3);
  }

  .audio-mode {
    background: #FAFBFC;
    padding: 2rem;
    border-radius: 16px;
    border: 1.5px solid #E5E7EB;
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
    gap: 1.25rem;
    width: 100%;
  }

  .sound-wave {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    height: 48px;
  }

  .sound-wave span {
    width: 5px;
    background: linear-gradient(180deg, #FF6B35 0%, #F7931E 100%);
    border-radius: 3px;
    animation: wave 1.2s ease-in-out infinite;
  }

  .sound-wave span:nth-child(1) { animation-delay: 0s; height: 14px; }
  .sound-wave span:nth-child(2) { animation-delay: 0.1s; height: 28px; }
  .sound-wave span:nth-child(3) { animation-delay: 0.2s; height: 42px; }
  .sound-wave span:nth-child(4) { animation-delay: 0.3s; height: 28px; }
  .sound-wave span:nth-child(5) { animation-delay: 0.4s; height: 14px; }

  @keyframes wave {
    0%, 100% { transform: scaleY(1); }
    50% { transform: scaleY(1.6); }
  }

  .speaking-indicator p {
    color: #4B5563;
    font-weight: 500;
    margin: 0;
    font-size: 1rem;
  }

  .stop-speech-btn {
    background: #DC2626;
    color: white;
    border: none;
    padding: 0.75rem 1.375rem;
    border-radius: 14px;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 0.5625rem;
    font-weight: 500;
    font-size: 0.9375rem;
    transition: all 0.2s cubic-bezier(0.25, 0.46, 0.45, 0.94);
    box-shadow: 0 2px 8px rgba(220, 38, 38, 0.3);
  }

  .stop-speech-btn:hover {
    background: #B91C1C;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(220, 38, 38, 0.4);
  }

  .stop-speech-btn:active {
    transform: translateY(0);
    transition: all 0.12s cubic-bezier(0.25, 0.46, 0.45, 0.94);
  }

  .replay-btn {
    background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%);
    color: white;
    border: none;
    padding: 1.125rem 2rem;
    border-radius: 16px;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    font-size: 1.0625rem;
    font-weight: 500;
    transition: all 0.25s cubic-bezier(0.25, 0.46, 0.45, 0.94);
    box-shadow: 0 4px 14px rgba(255, 107, 53, 0.35);
  }

  .replay-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 22px rgba(255, 107, 53, 0.45);
  }

  .replay-btn:active {
    transform: translateY(0);
    transition: all 0.12s cubic-bezier(0.25, 0.46, 0.45, 0.94);
  }

  .audio-hint {
    color: #6B7280;
    font-size: 0.875rem;
    margin: 0.875rem 0 0 0;
    text-align: center;
  }

  .response-content {
    background: #FAFBFC;
    padding: 1.5rem;
    border-radius: 16px;
    border: 1.5px solid #E5E7EB;
    line-height: 1.75;
    color: #1F2937;
  }

  .response-content :global(h1),
  .response-content :global(h2),
  .response-content :global(h3) {
    color: #1F2937;
    margin-top: 1.5rem;
    margin-bottom: 0.875rem;
    font-weight: 600;
  }

  .response-content :global(h1:first-child),
  .response-content :global(h2:first-child),
  .response-content :global(h3:first-child) {
    margin-top: 0;
  }

  .response-content :global(strong) {
    color: #F7931E;
    font-weight: 600;
  }

  .response-content :global(ul),
  .response-content :global(ol) {
    padding-left: 1.75rem;
  }

  .response-content :global(li) {
    margin-bottom: 0.625rem;
  }

  .response-content :global(p) {
    margin-bottom: 1.125rem;
  }

  .response-content :global(code) {
    background: #E5E7EB;
    padding: 0.25rem 0.5rem;
    border-radius: 6px;
    font-family: 'SF Mono', 'Monaco', 'Inconsolata', 'Consolas', monospace;
    font-size: 0.875em;
    color: #F7931E;
  }

  .new-query-btn {
    margin-top: 1.25rem;
    padding: 1rem 1.75rem;
    background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%);
    color: white;
    border: none;
    border-radius: 16px;
    cursor: pointer;
    font-weight: 500;
    font-size: 1rem;
    transition: all 0.25s cubic-bezier(0.25, 0.46, 0.45, 0.94);
    width: 100%;
    box-shadow: 0 2px 10px rgba(255, 107, 53, 0.3);
  }

  .new-query-btn:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 16px rgba(255, 107, 53, 0.4);
  }

  .new-query-btn:active {
    transform: translateY(0);
    transition: all 0.12s cubic-bezier(0.25, 0.46, 0.45, 0.94);
  }

  @media (max-width: 768px) {
    .modal-overlay {
      padding: 1rem;
    }

    .modal-content {
      max-width: 100%;
      border-radius: 24px;
    }

    .modal-header {
      padding: 1.5rem 1.5rem 1.25rem 1.5rem;
    }

    .header-content h2 {
      font-size: 1.375rem;
    }

    .modal-body {
      padding: 2rem 1.5rem;
    }

    .ptt-button {
      width: 120px;
      height: 120px;
    }

    .ptt-icon svg {
      width: 32px;
      height: 32px;
    }

    .response-header {
      flex-direction: column;
      align-items: flex-start;
    }

    .view-toggle {
      width: 100%;
    }

    .toggle-btn {
      flex: 1;
      justify-content: center;
    }
  }
</style>

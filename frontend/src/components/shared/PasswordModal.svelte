<script>
  import { createEventDispatcher } from 'svelte';

  let { title = 'Enter Password', description = 'Please enter the password', show = false } = $props();

  const dispatch = createEventDispatcher();

  let password = $state('');
  let passwordError = $state('');
  let capsLock = $state(false);
  let audioCtx = null;
  let passwordInput = null;

  // Audio context
  const getAudioContext = () => {
    if (audioCtx) return audioCtx;
    if (typeof window !== 'undefined' && (window.AudioContext || window.webkitAudioContext)) {
      audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    }
    return audioCtx;
  };

  const playKeySound = () => {
    const ctx = getAudioContext();
    if (!ctx) return;
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = 'sine';
    osc.frequency.value = 420;
    gain.gain.value = 1.0;
    osc.connect(gain).connect(ctx.destination);
    const now = ctx.currentTime;
    osc.start(now);
    gain.gain.setValueAtTime(gain.gain.value, now);
    gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.1);
    osc.stop(now + 0.12);
  };

  const handleKeyPress = (key) => {
    playKeySound();
    if (key === 'backspace') {
      password = password.slice(0, -1);
    } else if (key === 'clear') {
      password = '';
    } else if (key === 'capslock') {
      capsLock = !capsLock;
    } else {
      const char = capsLock ? key.toUpperCase() : key;
      password += char;
    }
    passwordError = '';
  };

  // Hold-to-delete on backspace
  let backspaceTimeout = null;
  let backspaceInterval = null;

  const startBackspaceHold = (event) => {
    event.preventDefault();
    stopBackspaceHold();
    handleKeyPress('backspace');
    backspaceTimeout = setTimeout(() => {
      backspaceInterval = setInterval(() => handleKeyPress('backspace'), 60);
    }, 300);
  };

  const stopBackspaceHold = () => {
    if (backspaceTimeout) {
      clearTimeout(backspaceTimeout);
      backspaceTimeout = null;
    }
    if (backspaceInterval) {
      clearInterval(backspaceInterval);
      backspaceInterval = null;
    }
  };

  const animateKeyPress = (event) => {
    const button = event.currentTarget;
    button.classList.add('key-pressed');
    setTimeout(() => {
      button.classList.remove('key-pressed');
    }, 80);
  };

  const handleSubmit = () => {
    if (password.trim()) {
      dispatch('submit', { password });
    }
  };

  const handleCancel = () => {
    password = '';
    passwordError = '';
    dispatch('cancel');
  };

  // Watch for external error
  export function setError(message) {
    passwordError = message;
    password = '';
  }

  // Reset when modal closes
  $effect(() => {
    if (!show) {
      password = '';
      passwordError = '';
      capsLock = false;
      stopBackspaceHold();
    } else if (passwordInput) {
      passwordInput.focus();
      passwordInput.setSelectionRange(password.length, password.length);
    }
  });

  const handlePhysicalKeydown = (event) => {
    if (event.key === 'Enter') {
      event.preventDefault();
      handleSubmit();
      return;
    }
    if (event.key === 'Escape') {
      event.preventDefault();
      handleCancel();
      return;
    }

    if (event.key.length === 1 || event.key === 'Backspace' || event.key === 'Delete') {
      playKeySound();
      passwordError = '';
    }
  };
</script>

{#if show}
  <div class="modal-overlay">
    <div class="modal-content" onclick={(e) => e.stopPropagation()}>
      <div class="modal-header">
        <h2>{title}</h2>
        <button class="close-btn" onclick={handleCancel}>
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <line x1="18" y1="6" x2="6" y2="18" stroke-width="2" stroke-linecap="round"/>
            <line x1="6" y1="6" x2="18" y2="18" stroke-width="2" stroke-linecap="round"/>
          </svg>
        </button>
      </div>

      <div class="modal-body">
        <p class="modal-description">{description}</p>

        <div class="input-group">
          <svg class="input-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <rect x="3" y="11" width="18" height="11" rx="2" ry="2" stroke-width="2"/>
            <path d="M7 11V7a5 5 0 0110 0v4" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <input
            class="password-display password-input"
            class:error={passwordError}
            type="password"
            placeholder="Enter password"
            bind:this={passwordInput}
            bind:value={password}
            oninput={() => (passwordError = '')}
            onkeydown={handlePhysicalKeydown}
          />
        </div>

        {#if passwordError}
          <div class="error-message">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <circle cx="12" cy="12" r="10" stroke-width="2"/>
              <line x1="12" y1="8" x2="12" y2="12" stroke-width="2" stroke-linecap="round"/>
              <line x1="12" y1="16" x2="12.01" y2="16" stroke-width="2" stroke-linecap="round"/>
            </svg>
            {passwordError}
          </div>
        {/if}
      </div>

      <div class="modal-footer">
        <button class="btn-cancel" onclick={handleCancel}>Cancel</button>
        <button class="btn-submit" onclick={handleSubmit}>Submit</button>
      </div>
    </div>

    <!-- Floating Virtual Keyboard -->
    <div class="keyboard-overlay" onclick={(e) => e.stopPropagation()}>
      <div class="virtual-keyboard">
        <div class="keyboard-body">
          <!-- Row 1 - Numbers -->
          <div class="keyboard-row">
            <button class="key" onclick={(e) => { animateKeyPress(e); handleKeyPress('1'); }}>1</button>
            <button class="key" onclick={(e) => { animateKeyPress(e); handleKeyPress('2'); }}>2</button>
            <button class="key" onclick={(e) => { animateKeyPress(e); handleKeyPress('3'); }}>3</button>
            <button class="key" onclick={(e) => { animateKeyPress(e); handleKeyPress('4'); }}>4</button>
            <button class="key" onclick={(e) => { animateKeyPress(e); handleKeyPress('5'); }}>5</button>
            <button class="key" onclick={(e) => { animateKeyPress(e); handleKeyPress('6'); }}>6</button>
            <button class="key" onclick={(e) => { animateKeyPress(e); handleKeyPress('7'); }}>7</button>
            <button class="key" onclick={(e) => { animateKeyPress(e); handleKeyPress('8'); }}>8</button>
            <button class="key" onclick={(e) => { animateKeyPress(e); handleKeyPress('9'); }}>9</button>
            <button class="key" onclick={(e) => { animateKeyPress(e); handleKeyPress('0'); }}>0</button>
          </div>

          <!-- Row 2 - QWERTY -->
          <div class="keyboard-row">
            <button class="key" onclick={(e) => { animateKeyPress(e); handleKeyPress('q'); }}>{capsLock ? 'Q' : 'q'}</button>
            <button class="key" onclick={(e) => { animateKeyPress(e); handleKeyPress('w'); }}>{capsLock ? 'W' : 'w'}</button>
            <button class="key" onclick={(e) => { animateKeyPress(e); handleKeyPress('e'); }}>{capsLock ? 'E' : 'e'}</button>
            <button class="key" onclick={(e) => { animateKeyPress(e); handleKeyPress('r'); }}>{capsLock ? 'R' : 'r'}</button>
            <button class="key" onclick={(e) => { animateKeyPress(e); handleKeyPress('t'); }}>{capsLock ? 'T' : 't'}</button>
            <button class="key" onclick={(e) => { animateKeyPress(e); handleKeyPress('y'); }}>{capsLock ? 'Y' : 'y'}</button>
            <button class="key" onclick={(e) => { animateKeyPress(e); handleKeyPress('u'); }}>{capsLock ? 'U' : 'u'}</button>
            <button class="key" onclick={(e) => { animateKeyPress(e); handleKeyPress('i'); }}>{capsLock ? 'I' : 'i'}</button>
            <button class="key" onclick={(e) => { animateKeyPress(e); handleKeyPress('o'); }}>{capsLock ? 'O' : 'o'}</button>
            <button class="key" onclick={(e) => { animateKeyPress(e); handleKeyPress('p'); }}>{capsLock ? 'P' : 'p'}</button>
          </div>

          <!-- Row 3 - ASDFGH -->
          <div class="keyboard-row">
            <button class="key" onclick={(e) => { animateKeyPress(e); handleKeyPress('a'); }}>{capsLock ? 'A' : 'a'}</button>
            <button class="key" onclick={(e) => { animateKeyPress(e); handleKeyPress('s'); }}>{capsLock ? 'S' : 's'}</button>
            <button class="key" onclick={(e) => { animateKeyPress(e); handleKeyPress('d'); }}>{capsLock ? 'D' : 'd'}</button>
            <button class="key" onclick={(e) => { animateKeyPress(e); handleKeyPress('f'); }}>{capsLock ? 'F' : 'f'}</button>
            <button class="key" onclick={(e) => { animateKeyPress(e); handleKeyPress('g'); }}>{capsLock ? 'G' : 'g'}</button>
            <button class="key" onclick={(e) => { animateKeyPress(e); handleKeyPress('h'); }}>{capsLock ? 'H' : 'h'}</button>
            <button class="key" onclick={(e) => { animateKeyPress(e); handleKeyPress('j'); }}>{capsLock ? 'J' : 'j'}</button>
            <button class="key" onclick={(e) => { animateKeyPress(e); handleKeyPress('k'); }}>{capsLock ? 'K' : 'k'}</button>
            <button class="key" onclick={(e) => { animateKeyPress(e); handleKeyPress('l'); }}>{capsLock ? 'L' : 'l'}</button>
            <button
              class="key key-backspace"
              onpointerdown={(e) => { animateKeyPress(e); startBackspaceHold(e); }}
              onpointerup={stopBackspaceHold}
              onpointerleave={stopBackspaceHold}
              onpointercancel={stopBackspaceHold}
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M9 3h11a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H9l-7-9 7-9z" stroke-linecap="round" stroke-linejoin="round"/>
                <line x1="14" y1="9" x2="18" y2="13" stroke-linecap="round"/>
                <line x1="18" y1="9" x2="14" y2="13" stroke-linecap="round"/>
              </svg>
            </button>
          </div>

          <!-- Row 4 - ZXCVBN -->
          <div class="keyboard-row">
            <button class="key key-capslock" class:active={capsLock} onclick={(e) => { animateKeyPress(e); handleKeyPress('capslock'); }}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="M12 3l-8 8h5v10h6V11h5L12 3z" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </button>
            <button class="key" onclick={(e) => { animateKeyPress(e); handleKeyPress('z'); }}>{capsLock ? 'Z' : 'z'}</button>
            <button class="key" onclick={(e) => { animateKeyPress(e); handleKeyPress('x'); }}>{capsLock ? 'X' : 'x'}</button>
            <button class="key" onclick={(e) => { animateKeyPress(e); handleKeyPress('c'); }}>{capsLock ? 'C' : 'c'}</button>
            <button class="key" onclick={(e) => { animateKeyPress(e); handleKeyPress('v'); }}>{capsLock ? 'V' : 'v'}</button>
            <button class="key" onclick={(e) => { animateKeyPress(e); handleKeyPress('b'); }}>{capsLock ? 'B' : 'b'}</button>
            <button class="key" onclick={(e) => { animateKeyPress(e); handleKeyPress('n'); }}>{capsLock ? 'N' : 'n'}</button>
            <button class="key" onclick={(e) => { animateKeyPress(e); handleKeyPress('m'); }}>{capsLock ? 'M' : 'm'}</button>
            <button class="key key-clear" onclick={(e) => { animateKeyPress(e); handleKeyPress('clear'); }}>Clear</button>
          </div>
        </div>
      </div>
    </div>
  </div>
{/if}

<style>
  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: var(--overlay-bg);
    backdrop-filter: blur(8px);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 10000;
    animation: fadeIn 0.2s ease-out;
  }

  @keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
  }

  .modal-content {
    background: linear-gradient(135deg, var(--card-gradient-start), var(--card-gradient-end));
    border-radius: 20px;
    width: 90%;
    max-width: 450px;
    box-shadow: 0 20px 60px var(--shadow-heavy);
    animation: modalSlide 0.3s ease-out;
    overflow: hidden;
    transition: background 0.3s ease;
    margin-bottom: 300px;
    border: 1px solid var(--border);
  }

  @keyframes modalSlide {
    from {
      opacity: 0;
      transform: translateY(-20px) scale(0.95);
    }
    to {
      opacity: 1;
      transform: translateY(0) scale(1);
    }
  }

  .modal-header {
    padding: 24px 24px 16px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid var(--border, #E0E0E0);
    transition: border-bottom 0.3s ease;
  }

  .modal-header h2 {
    margin: 0;
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--primary, #212121);
    transition: color 0.3s ease;
  }

  .close-btn {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    border: none;
    background: var(--surface-muted);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s ease;
    color: var(--secondary, #757575);
  }

  .close-btn:hover {
    background: var(--border, #E0E0E0);
    transform: rotate(90deg);
  }

  .modal-body {
    padding: 24px;
  }

  .modal-description {
    margin: 0 0 20px 0;
    color: var(--secondary, #616161);
    font-size: 0.95rem;
    line-height: 1.5;
    transition: color 0.3s ease;
  }

  .input-group {
    position: relative;
    display: flex;
    align-items: center;
  }

  .input-icon {
    position: absolute;
    left: 16px;
    color: var(--secondary, #9E9E9E);
    pointer-events: none;
    transition: color 0.3s ease, filter 0.3s ease;
  }

  .password-display {
    width: 100%;
    padding: 14px 16px 14px 48px;
    border: 2px solid var(--border, #E0E0E0);
    border-radius: 12px;
    font-size: 1.5rem;
    font-weight: 500;
    background: var(--bg-card);
    min-height: 52px;
    display: block;
    letter-spacing: 4px;
    color: var(--primary, #212121);
    transition: all 0.2s ease;
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
    box-sizing: border-box;
  }

  .password-display.error {
    border-color: var(--danger);
    background: var(--surface-critical);
    animation: shake 0.3s ease-in-out;
  }

  .password-input {
    outline: none;
    box-shadow: none;
    height: 100%;
  }

  .password-input::placeholder {
    font-size: 0.95rem;
    color: var(--secondary, #9E9E9E);
    letter-spacing: normal;
    font-weight: 400;
    opacity: 1;
  }

  .placeholder-text {
    font-size: 0.95rem;
    color: var(--secondary, #9E9E9E);
    letter-spacing: normal;
    font-weight: 400;
    transition: color 0.3s ease;
  }

  .error-message {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-top: 12px;
    padding: 12px;
    background: var(--surface-critical);
    border-radius: 8px;
    color: var(--danger);
    font-size: 0.9rem;
    font-weight: 500;
    animation: shake 0.3s ease-in-out;
    transition: color 0.3s ease;
  }

  @keyframes shake {
    0%, 100% { transform: translateX(0); }
    25% { transform: translateX(-8px); }
    75% { transform: translateX(8px); }
  }

  .modal-footer {
    padding: 16px 24px 24px;
    display: flex;
    gap: 12px;
    justify-content: flex-end;
  }

  .btn-cancel,
  .btn-submit {
    padding: 12px 28px;
    border-radius: 10px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
    border: none;
  }

  .btn-cancel {
    background: var(--surface-muted);
    color: var(--secondary, #616161);
  }

  .btn-cancel:hover {
    background: var(--border, #E0E0E0);
  }

  .btn-submit {
    background: linear-gradient(135deg, var(--brand) 0%, var(--brand-strong) 100%);
    color: var(--on-brand);
    box-shadow: 0 4px 12px color-mix(in srgb, var(--brand) 30%, transparent);
  }

  .btn-submit:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px color-mix(in srgb, var(--brand) 45%, transparent);
  }

  .btn-submit:active {
    transform: translateY(0);
  }

  /* Virtual Keyboard - Floating at bottom */
  .keyboard-overlay {
    position: fixed;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%);
    z-index: 10001;
    animation: slideUpKeyboard 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
    pointer-events: none;
  }

  @keyframes slideUpKeyboard {
    from {
      transform: translateX(-50%) translateY(100%);
      opacity: 0;
    }
    to {
      transform: translateX(-50%) translateY(0);
      opacity: 1;
    }
  }

  .virtual-keyboard {
    background: transparent;
    padding: 0;
    pointer-events: auto;
  }

  :global(html.dark-mode) .virtual-keyboard {
    background: transparent;
  }

  .keyboard-body {
    display: flex;
    flex-direction: column;
    gap: 10px;
    max-width: 900px;
    width: 100%;
    margin: 0 auto;
  }

  .keyboard-row {
    width: 100%;
    display: grid;
    grid-template-columns: repeat(10, minmax(64px, 1fr));
    gap: 10px;
    justify-items: center;
    align-items: center;
  }

  .key {
    width: 100%;
    height: 54px;
    border: none;
    border-radius: 12px;
    background: linear-gradient(135deg, var(--accent-warm-start), var(--accent-warm-end));
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--on-brand);
    cursor: pointer;
    transition: all 0.08s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3), 0 3px 6px rgba(0, 0, 0, 0.2);
    display: flex;
    align-items: center;
    justify-content: center;
    user-select: none;
    -webkit-user-select: none;
    -webkit-tap-highlight-color: transparent;
    position: relative;
  }

  .key:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4), 0 4px 8px rgba(0, 0, 0, 0.3);
  }

  .key:active {
    transform: scale(0.95) translateY(0);
    box-shadow: 0 3px 10px rgba(0, 0, 0, 0.3);
  }

  :global(.key-pressed) {
    transform: scale(0.95);
    opacity: 0.8;
  }

  .key-backspace, .key-clear {
    background: linear-gradient(135deg, var(--brand) 0%, var(--brand-strong));
    color: var(--on-brand);
  }

  .key-backspace {
    color: var(--on-brand);
  }

  .key-backspace svg {
    stroke: var(--on-brand);
  }

  .key-clear {
    grid-column: span 2;
    color: var(--on-brand);
  }

  .key-capslock {
    background: linear-gradient(135deg, var(--border), var(--border-strong));
    color: var(--on-brand);
  }

  .key-capslock.active {
    background: linear-gradient(135deg, var(--success) 0%, var(--accent-green) 100%);
    box-shadow: 0 0 20px color-mix(in srgb, var(--success) 50%, transparent);
    color: white;
  }

  .key-capslock svg {
    stroke: var(--on-brand);
  }

  .key-capslock.active svg {
    stroke: white;
  }

  @media (max-width: 768px) {
    .keyboard-body {
      max-width: 100%;
      padding: 0 6px;
    }

    .keyboard-row {
      grid-template-columns: repeat(10, minmax(48px, 1fr));
      gap: 8px;
    }

    .key {
      height: 48px;
      font-size: 1rem;
      border-radius: 10px;
    }
  }
</style>


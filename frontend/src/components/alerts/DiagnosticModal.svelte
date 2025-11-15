<script>
  import { createEventDispatcher } from 'svelte';
  import { diagnosticOptions } from '../../stores/alertStore.js';

  const dispatch = createEventDispatcher();
  const API_BASE = 'http://localhost:8000';

  const steps = ['subsystem', 'component', 'symptom'];
  const stepTitles = ['Select Subsystem', 'Select Component', 'Describe the Symptom'];
  const stepQuestions = [
    'Which part of the machine is affected?',
    'Which specific component is failing?',
    'What is the observable issue?'
  ];
  const symptoms = ['No movement', 'Incorrect position', 'Loud noise', 'Overheating', 'Failed to read', 'Low pressure'];

  // Map backend subsystem names to display names
  const subsystemDisplayMap = {
    'conveyor': 'Conveyor System',
    'elevator': 'Elevator/Lift',
    'gantry': 'Gantry/Crane',
    'storage': 'Storage Racks',
    'safety': 'Safety Systems',
    'plc_network': 'PLC/Network',
    'qc_vision': 'QC/Vision',
    'pneumatics': 'Pneumatics',
    'hmi': 'HMI/Interface',
    'subsystem': 'General Subsystem'
  };

  // Component mapping based on subsystem
  const componentMap = {
    'conveyor': ['Motor', 'Belt', 'Encoder (E1)', 'Photoeye (PE1)', 'Rollers', 'Drive Controller'],
    'elevator': ['Motor', 'Cable', 'Brake', 'Position Sensor', 'Limit Switch'],
    'gantry': ['X-Axis Motor', 'Y-Axis Motor', 'Z-Axis Motor', 'Gripper', 'Cable Chain'],
    'storage': ['Rack Structure', 'Bin Sensor', 'Location Marker', 'Access Door'],
    'safety': ['Emergency Stop', 'Light Curtain', 'Interlock', 'Safety Relay'],
    'plc_network': ['PLC Module', 'Network Switch', 'I/O Card', 'Power Supply'],
    'qc_vision': ['Camera', 'Barcode Scanner', 'Vision Processor', 'Lighting'],
    'pneumatics': ['Compressor', 'Valve', 'Cylinder', 'Air Line', 'Pressure Sensor'],
    'hmi': ['Touch Panel', 'Display', 'Control Board', 'Ethernet Cable'],
    'subsystem': ['Controller', 'Sensor', 'Actuator', 'Power Module']
  };

  let currentStep = 0;
  let selections = {};
  let options = [];
  let displayOptions = [];
  let loading = false;

  $: updateOptions(currentStep, selections, $diagnosticOptions);

  function updateOptions(step, sel, diagOpts) {
    if (step === 0) {
      // First step: show subsystems with display names
      const subsystems = diagOpts || [];
      options = subsystems;
      displayOptions = subsystems.map(s => subsystemDisplayMap[s] || s);
    } else if (step === 1) {
      // Second step: show components for selected subsystem
      const selectedSubsystem = sel.subsystem;
      if (selectedSubsystem && componentMap[selectedSubsystem]) {
        options = componentMap[selectedSubsystem];
        displayOptions = options; // Components use their own names
      } else {
        options = ['Motor', 'Sensor', 'Controller', 'Actuator'];
        displayOptions = options;
      }
    } else {
      // Third step: symptoms
      options = symptoms;
      displayOptions = symptoms;
    }
  }

  function selectOption(value, displayValue) {
    selections[steps[currentStep]] = value;
    // Store display name for later use
    if (currentStep === 0) {
      selections.subsystemDisplay = displayValue;
    }
    selections = selections;
  }

  function back() {
    if (currentStep > 0) {
      currentStep--;
    } else {
      dispatch('close');
    }
  }

  async function next() {
    if (currentStep < steps.length - 1) {
      currentStep++;
    } else {
      // Build query with display names for better context
      const subsystemName = selections.subsystemDisplay || subsystemDisplayMap[selections.subsystem] || selections.subsystem;
      const query = `Issue with ${subsystemName} - ${selections.component || 'Unknown Component'}. Symptom: ${selections.symptom}.`;

      loading = true; // Start loading
      try {
        const response = await fetch(`${API_BASE}/api/query`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ query })
        });

        const data = await response.json();
        loading = false; // Stop loading
        dispatch('complete', { result: data.response });
      } catch (error) {
        console.error('Diagnosis error:', error);
        loading = false; // Stop loading on error
        dispatch('complete', { result: 'Error generating diagnosis. Please try again.' });
      }
    }
  }

  function handleKeydown(e) {
    if (e.key === 'Escape') {
      dispatch('close');
    }
  }

  $: canProceed = selections[steps[currentStep]] !== undefined;
</script>

<div class="modal-overlay" on:click={() => dispatch('close')} on:keydown={handleKeydown} role="button" tabindex="-1">
  <div class="modal" on:click|stopPropagation>
    <div class="modal-header">
      <button class="back-button" on:click={back}>
        <svg width="24" height="24" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
        </svg>
      </button>
      <div class="modal-title">{stepTitles[currentStep]}</div>
      <div class="progress-bar">
        {#each steps as step, i}
          <div class="progress-segment" class:active={i <= currentStep}></div>
        {/each}
      </div>
    </div>

    <div class="modal-body">
      {#if loading}
        <div class="loading-container">
          <div class="spinner"></div>
          <p class="loading-text">Analyzing issue and generating diagnosis...</p>
        </div>
      {:else}
        <div class="question-title">{stepQuestions[currentStep]}</div>
        <div class="options-grid">
          {#each displayOptions as displayOption, i}
            <button
              class="option-button"
              class:selected={selections[steps[currentStep]] === options[i]}
              on:click={() => selectOption(options[i], displayOption)}
            >
              {displayOption}
            </button>
          {/each}
        </div>
      {/if}
    </div>

    <div class="modal-footer">
      <button class="footer-button back" on:click={back}>Back</button>
      <button
        class="footer-button next"
        on:click={next}
        disabled={!canProceed}
      >
        {currentStep === steps.length - 1 ? 'Diagnose' : 'Next'}
      </button>
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
    background: rgba(0,0,0,0.5);
    z-index: 1000;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .modal {
    background: white;
    border-radius: 16px;
    width: 90%;
    max-width: 800px;
    max-height: 90vh;
    overflow: hidden;
    display: flex;
    flex-direction: column;
  }

  .modal-header {
    padding: 2rem;
    border-bottom: 1px solid #E0E0E0;
    position: relative;
  }

  .back-button {
    position: absolute;
    top: 2rem;
    left: 2rem;
    width: 48px;
    height: 48px;
    border: 1px solid #E0E0E0;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    background: white;
  }

  .modal-title {
    text-align: center;
    font-size: 2rem;
    font-weight: 700;
  }

  .progress-bar {
    display: flex;
    gap: 0.5rem;
    margin-top: 1.5rem;
    justify-content: center;
  }

  .progress-segment {
    height: 4px;
    width: 80px;
    background: #E0E0E0;
    border-radius: 2px;
  }

  .progress-segment.active {
    background: #FF5722;
  }

  .modal-body {
    flex: 1;
    overflow-y: auto;
    padding: 2rem;
  }

  .question-title {
    font-size: 1.75rem;
    font-weight: 600;
    text-align: center;
    margin-bottom: 2rem;
  }

  .options-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
  }

  .option-button {
    padding: 2rem 1rem;
    border: 1px solid #E0E0E0;
    border-radius: 12px;
    background: white;
    cursor: pointer;
    font-weight: 500;
    font-size: 1rem;
    transition: all 0.2s;
    text-align: center;
  }

  .option-button:hover {
    border-color: #FF5722;
    background: #FFF3E0;
  }

  .option-button.selected {
    border-color: #FF5722;
    background: #FF5722;
    color: white;
  }

  .modal-footer {
    padding: 1.5rem 2rem;
    border-top: 1px solid #E0E0E0;
    display: flex;
    gap: 1rem;
  }

  .footer-button {
    flex: 1;
    padding: 1rem;
    border-radius: 8px;
    font-weight: 600;
    font-size: 1rem;
    cursor: pointer;
    transition: all 0.2s;
  }

  .footer-button.back {
    background: white;
    border: 1px solid #E0E0E0;
  }

  .footer-button.next {
    background: #424242;
    color: white;
    border: none;
  }

  .footer-button.next:hover:not(:disabled) {
    background: #212121;
  }

  .footer-button:disabled {
    opacity: 0.4;
    cursor: not-allowed;
  }

  .loading-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 400px;
    gap: 1.5rem;
  }

  .spinner {
    width: 60px;
    height: 60px;
    border: 4px solid #E0E0E0;
    border-top: 4px solid #FF5722;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }

  .loading-text {
    font-size: 1.1rem;
    color: #757575;
    font-weight: 500;
  }
</style>

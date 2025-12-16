<script>
  import { createEventDispatcher } from 'svelte';
  import { marked } from 'marked';

  export let result = '';

  const dispatch = createEventDispatcher();

  function handleKeydown(e) {
    if (e.key === 'Escape') {
      dispatch('close');
    }
  }

  $: htmlContent = marked.parse(result);
</script>

<div class="modal-overlay" on:click={() => dispatch('close')} on:keydown={handleKeydown} role="button" tabindex="-1">
  <div class="modal" on:click|stopPropagation>
    <div class="modal-header">
      <button class="back-button" on:click={() => dispatch('close')}>
        <svg width="24" height="24" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/>
        </svg>
      </button>
      <div class="modal-title">Diagnostic Report</div>
    </div>

    <div class="modal-body">
      <div class="diagnosis-content">
        {@html htmlContent}
      </div>
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

  .modal-body {
    flex: 1;
    overflow-y: auto;
    padding: 2rem;
  }

  .diagnosis-content {
    line-height: 1.8;
  }

  .diagnosis-content :global(h2) {
    color: #FF5722;
    margin-top: 1.5rem;
    margin-bottom: 0.75rem;
  }

  .diagnosis-content :global(h3) {
    color: #FF5722;
    margin-top: 1.25rem;
    margin-bottom: 0.5rem;
  }

  .diagnosis-content :global(strong) {
    color: #FF5722;
  }

  .diagnosis-content :global(ol),
  .diagnosis-content :global(ul) {
    margin-left: 1.5rem;
    margin-top: 0.5rem;
  }

  .diagnosis-content :global(li) {
    margin-bottom: 0.5rem;
  }

  .diagnosis-content :global(p) {
    margin-bottom: 1rem;
  }
</style>
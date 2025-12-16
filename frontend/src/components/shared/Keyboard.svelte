<script>
  import { createEventDispatcher } from 'svelte';
  const dispatch = createEventDispatcher();

  // Definition of the keyboard rows based on your image
  const rows = [
    ['~ `', '! 1', '@ 2', '# 3', '$ 4', '% 5', '^ 6', '& 7', '* 8', '( 9', ') 0', '- _', '+ =', 'backspace'],
    ['tab', 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '{ [', '} ]', '| \\'],
    ['caps lock', 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ': ;', '" \'', 'enter'],
    ['shift', 'z', 'x', 'c', 'v', 'b', 'n', 'm', '< ,', '> .', '? /', 'shift'],
    ['ctrl', 'win', 'alt', 'space', 'alt', 'win', 'del', 'ctrl']
  ];

  function handleKey(key) {
    // We dispatch the key value (or label) to the parent
    dispatch('keypress', key);
  }
</script>

<div class="keyboard-container">
  {#each rows as row, i}
    <div class="row">
      {#each row as key}
        <button 
          class="key" 
          class:space={key === 'space'}
          class:backspace={key === 'backspace'}
          class:tab={key === 'tab'}
          class:caps={key === 'caps lock'}
          class:enter={key === 'enter'}
          class:shift={key === 'shift'}
          class:wide={['ctrl', 'win', 'alt', 'del'].includes(key)}
          on:click={() => handleKey(key)}
        >
          {#if key.includes(' ') && !['caps lock', 'space'].includes(key)}
             <div class="multi-char">
                <span>{key.split(' ')[0]}</span>
                <span>{key.split(' ')[1]}</span>
             </div>
          {:else}
             {key}
          {/if}
        </button>
      {/each}
    </div>
  {/each}
</div>

<style>
  .keyboard-container {
    background-color: white;
    padding: 20px;
    display: flex;
    flex-direction: column;
    gap: 8px;
    width: 100%;
    max-width: 1000px;
    margin: 0 auto;
    box-sizing: border-box;
    font-family: sans-serif;
  }

  .row {
    display: flex;
    gap: 6px;
    justify-content: center;
  }

  .key {
    background-color: #E5E7EB; /* Light grey key color */
    border: none;
    border-radius: 6px;
    padding: 10px;
    font-size: 16px;
    color: #374151;
    cursor: pointer;
    flex: 1; /* Default width */
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 50px;
    box-shadow: 0 1px 2px rgba(0,0,0,0.1);
    transition: background-color 0.1s;
    user-select: none;
  }

  .key:active {
    background-color: #D1D5DB;
  }

  .multi-char {
    display: flex;
    flex-direction: column;
    line-height: 1;
    font-size: 13px;
    gap: 2px;
  }

  /* Specific sizing logic to match standard layout proportions */
  .backspace { flex: 2; }
  .tab { flex: 1.5; }
  .caps { flex: 1.8; text-align: left; align-items: flex-start; padding-left: 15px; }
  .enter { flex: 2; }
  .shift { flex: 2.4; text-align: left; align-items: flex-start; padding-left: 15px; }
  .space { flex: 6; }
  .wide { flex: 1.2; }

</style>
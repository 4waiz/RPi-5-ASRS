<script>
  import { myVariable } from './store.js';
  import Home from './Pages/Home.svelte';
  import Setting from './Pages/Setting.svelte';

  // Set the store value to the Setting component dynamically
  myVariable.set(Home);  // Now the store holds the Setting component
</script>

<div class="main">
  <!-- Dynamically render the component based on the store's value -->
  <svelte:component this={$myVariable} />
</div>

<style>
  .main {
    width: 100%; 
    height: 100vh;
  }
</style>

<script>
  import { myVariable } from './store.js';
  import Home from './Pages/Home.svelte';
  import Setting from './Pages/Setting.svelte';

  myVariable.set(Home);  // Now the store holds the Setting component
</script>

<div class="main">
  <svelte:component this={$myVariable} />
</div>

<style>
  .main {
    width: 100%; 
    height: 100vh;
  }
</style>

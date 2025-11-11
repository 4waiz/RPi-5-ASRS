<script>
    import SideBar from "../lib/side-bar.svelte";
</script>
<div class="main">
    <div>
         <SideBar AlertsNum="5" WoriginNum="2" ActivePage="AI Assistant" />
    </div>
    <h1>AI Assistant</h1>
</div>

<style>
  .main {
    width: 100%;
    height: calc(100vh);
    display: flex;
    gap: 32px;
    background-color: #ebebeb;
    box-sizing: border-box;
    padding-right: 32px;
  }
</style>
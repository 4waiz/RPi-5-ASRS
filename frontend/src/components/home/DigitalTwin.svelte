<script>
  import { curentMode } from "../../stores/AppStore.js";

  $: iframeSrc = $curentMode === "Live"
    ? "/3d digital twin/index.html"
    : "/Live_3D_twin/index.html";
</script>

<div class="crane-wrapper">
  <iframe
    class="crane-frame"
    src={iframeSrc}
    title="ASRS Crane"
    loading="lazy"

  ></iframe>
</div>

<style>
  .crane-wrapper {
    display: inline-block;
  }

  .crane-frame {
    border: none;
    width: 770px;
    height: 472px;
  }
</style>

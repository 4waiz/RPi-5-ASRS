<script>
  let activeIndex = $state(0);
  import SideBar from "../lib/side-bar.svelte";
  import TopBar from "../lib/top-bar.svelte";
  import DigitalTwinTabPage from "../lib/Home-pages/DigitalTwin.svelte";
  import InventoryTabPage from "../lib/Home-pages/Inventory.svelte";
  import ComponentsOverviewTab from "../lib/Home-pages/Components.svelte";
  import OverviewTabPage from "../lib/Home-pages/Overview.svelte";
  import SmallAlert from "../lib/small-alert.svelte";
  import greyOverview from "../assets/TopPageIcon/grey-overview.svg?url";
  import orangeOverview from "../assets/TopPageIcon/orange-overview.svg?url";
  import greyInventory from "../assets/TopPageIcon/grey-inventory.svg?url";
  import orangeInventory from "../assets/TopPageIcon/orange-inventory.svg?url";
  import greyDigital from "../assets/TopPageIcon/grey-digitaltwin.svg?url";
  import orangeDigital from "../assets/TopPageIcon/orange-digitaltwin.svg?url";
  import greyComponent from "../assets/TopPageIcon/grey-component.svg?url";
  import orangeComponent from "../assets/TopPageIcon/orange-component.svg?url";

  let Alerts = [2, 5];
  let Names = ["Overview", "Inventory", "Digital Twin", "Components"];
  let Icons = [
    { inactive: greyOverview,  active: orangeOverview },
    { inactive: greyInventory, active: orangeInventory },
    { inactive: greyDigital,   active: orangeDigital },
    { inactive: greyComponent, active: orangeComponent }
  ];
  let Pages = [
    OverviewTabPage,
    InventoryTabPage,
    DigitalTwinTabPage,
    ComponentsOverviewTab,
  ];
</script>

<div class="main">
  <SideBar WoriginNum={Alerts[1]} AlertsNum={Alerts[0]} ActivePage={"Home"} />

  <section class="right-con">
    <TopBar {Names} {Pages} {Icons} bind:activeIndex>
  <svelte:fragment slot="alerts">
    {#if activeIndex === 0}
      <div class="alert-section">
        <SmallAlert Massage="massage 1" Type="W" Time="12:16" />
        <SmallAlert Massage="massage 2" Type="Alert" Time="10:25" />
      </div>
    {/if}
  </svelte:fragment>
</TopBar>
</section>
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

  .right-con {
    flex: 1;
    min-width: 0; /* <— lets it shrink instead of pushing page wider */
    display: flex;
    flex-direction: column;
    height: 100%;
    box-sizing: border-box;
  }

  .alert-section {
    width: 100%;
    min-width: 0; /* safe in flex contexts */
    margin: 24px 0;
    height: 120px;
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    align-items: flex-start;
    gap: 8px;
  }

      /* 🔧 Make sure components fit perfectly */
  :global(html),
  :global(body) {
    margin: 0;
    padding: 0;
    overflow-x: hidden;
  }
</style>

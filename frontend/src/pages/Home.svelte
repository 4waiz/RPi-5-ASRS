<script>
  import { setContext } from "svelte";

  let activeIndex = $state(0);
  import SideBar from "../components/shared/Sidebar.svelte";
  import TopBar from "../components/shared/TopBar.svelte";
  import DigitalTwinTabPage from "../components/home/DigitalTwin.svelte";
  import InventoryTabPage from "../components/home/Inventory.svelte";
  import ComponentsOverviewTab from "../components/home/Components.svelte";
  import OverviewTabPage from "../components/home/Overview.svelte";
  import SmallAlert from "../components/shared/SmallAlert.svelte";
  import greyOverview from "../assets/TopPageIcon/grey-overview.svg?url";
  import orangeOverview from "../assets/TopPageIcon/orange-overview.svg?url";
  import greyInventory from "../assets/TopPageIcon/grey-inventory.svg?url";
  import orangeInventory from "../assets/TopPageIcon/orange-inventory.svg?url";
  import greyDigital from "../assets/TopPageIcon/grey-digitaltwin.svg?url";
  import orangeDigital from "../assets/TopPageIcon/orange-digitaltwin.svg?url";
  import greyComponent from "../assets/TopPageIcon/grey-component.svg?url";
  import orangeComponent from "../assets/TopPageIcon/orange-component.svg?url";
  import { t } from "../lib/i18n";

  const totalErrors = 5;
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

  // Provide navigation context for child components
  setContext('navigation', {
    navigateToTab: (index) => {
      activeIndex = index;
    }
  });
</script>

<div class="main">
  <SideBar AlertsNum={totalErrors} ActivePage={"Home"} />
  <section class="right-con">
    <TopBar Names={[$t('home.tabs.overview'), $t('home.tabs.inventory'), $t('home.tabs.digitalTwin'), $t('home.tabs.components')]} {Pages} {Icons} bind:activeIndex>
  <svelte:fragment slot="alerts">
    {#if activeIndex === 0 || activeIndex === 1}
      <div class="alert-section">
        <SmallAlert Massage={$t('home.alerts.noStockBox8')} Type="W" Time="12:16" />
        <SmallAlert Massage={$t('home.alerts.supplierRejected')} Type="Alert" Time="10:25" />
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
    padding-left: 220px;
    padding-right: 32px;
  }

  .right-con {
    flex: 1;
    min-width: 0;
    display: flex;
    flex-direction: column;
    height: 100%;
    box-sizing: border-box;
  }

  .alert-section {
    width: 100%;
    min-width: 0;
    margin: 9px 0 0 24px;
    height: auto;
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    align-items: flex-start;
    gap: 8px;
  }

  :global(html),
  :global(body) {
    margin: 0;
    padding: 0;
    overflow-x: hidden;
  }
</style>

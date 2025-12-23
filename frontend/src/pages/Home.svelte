<script>
  import { ActiveTapHomePag, currentPage } from "../stores/AppStore.js";
  import SideBar from "../components/shared/Sidebar.svelte";
  import TopBar from "../components/shared/TopBar.svelte";
  import DigitalTwinTabPage from "../components/home/DigitalTwin.svelte";
  import InverntoryTabPage from "../components/home/Inventory.svelte";
  import CompunentsOverviewTab from "../components/home/Components.svelte";
  import OverviewTabPage from "../components/home/Overview.svelte";
  import SmallAlert from "../components/shared/SmallAlert.svelte";
  import Control from "../components/home/control.svelte";
  import {curentMode} from "../stores/AppStore.js";
  import { t } from "../lib/i18n";

  //test models 
  import TestModels from "../components/home/TestModels.svelte";

  let Alerts = [2, 5];
  // Tab names are now derived from translations
  $: Names = [$t('home.tabs.overview'), $t('home.tabs.inventory'), $t('home.tabs.digitalTwin'), $t('home.tabs.components')];

  // Reactively update tabe3 when curentMode changes
  $: tabe3 = $curentMode === "Test" ? Control : TestModels;

  // Reactively rebuild Pages array when tabe3 changes
  $: Pages = [
    OverviewTabPage,
    InverntoryTabPage,
    tabe3,
    CompunentsOverviewTab,
  ];

  let AlertMessages = [];
  let smootHours = 5;
</script>

<div class="main">
  <SideBar WarningNum={Alerts[1]} AlertsNum={Alerts[0]} ActivePage={"Home"} />
  <section class="right-con">
    <!-- svelte-ignore a11y_click_events_have_key_events -->
    <!-- svelte-ignore a11y_no_static_element_interactions -->
    <div
      class="alert-section"
      onclick={() => {
        currentPage.set("Alerts");
      }}
    >
      {#if AlertMessages.length === 0}
        <div class="alert-placeholder">
          <svg
            width="13"
            height="10"
            viewBox="0 0 13 10"
            fill="none"
          >
            <path
              d="M12.0598 0.458151C11.7904 0.188721 11.4319 0.0268679 11.0516 0.00295544C10.6713 -0.0209579 10.2953 0.0947132 9.99422 0.328269L9.84712 0.458151L4.69402 5.60962L2.67065 3.58784L2.52355 3.45796C2.22245 3.22457 1.84654 3.10904 1.46633 3.13303C1.08612 3.15701 0.727721 3.31887 0.458338 3.58825C0.188954 3.85763 0.027092 4.21603 0.00310516 4.59624C-0.0208826 4.97644 0.0946522 5.35234 0.328043 5.65344L0.457928 5.80053L3.58766 8.93023L3.73476 9.06011C4.00919 9.27303 4.34667 9.3886 4.69402 9.3886C5.04137 9.3886 5.37885 9.27303 5.65328 9.06011L5.80038 8.93023L12.0598 2.67084L12.1897 2.52375C12.4233 2.22266 12.539 1.84671 12.515 1.46641C12.4911 1.08611 12.3293 0.727606 12.0598 0.458151Z"
              fill="#1CB542"
            />
          </svg>
          <span>{$t('home.smoothOperation').replace('{hours}', smootHours.toString())}</span>
        </div>
      {/if}
      {#each AlertMessages as alert}
        <SmallAlert
          Message={alert.Message}
          Type={alert.Type}
          Time={alert.Time}
        />
      {/each}
    </div>
    <TopBar {Names} {Pages} bind:activeIndex={$ActiveTapHomePag} />
  </section>
</div>

<style>
  .alert-placeholder {
    font-size: 16px;
    font-weight: 50px;
    background-color: #30d15814;
    width: 100%;
    height: 72px;
    border-radius: 16px;
    display: flex;
    justify-content: center;
    align-items: center;
    border: solid 2px rgba(0, 0, 0, 0.1);
    gap: 8px;
  }
  .main {
    width: 100%;
    height: calc(100vh);
    display: flex;
    gap: 32px;
    background-color: #ebebeb;
    box-sizing: border-box;
    padding-right: 32px;
  }

  .alert-section {
    width: 100%;
    min-width: 0; /* safe in flex contexts */
    height: 72px;
    display: flex;
    margin-top: 24px;
    flex-direction: column;
    justify-content: flex-end;
    align-items: flex-start;
    gap: 8px;
  }
  .right-con {
    flex: 1;
    min-width: 0; /* <— lets it shrink instead of pushing page wider */
    display: flex;
    flex-direction: column;
    height: 100%;
    box-sizing: border-box;
  }
  /* 🔧 Make sure components fit perfectly */
  :global(html),
  :global(body) {
    margin: 0;
    padding: 0;
    overflow-x: hidden;
  }
</style>

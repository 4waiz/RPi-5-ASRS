<script>
    import { myVariable } from "../store.js";
    import Home from "../Pages/Home.svelte";
    import Setting from "../Pages/Setting.svelte";
    import Alerts from "../Pages/Alerts.svelte";
    import AIAssistrnt from "../Pages/AIAssistrnt.svelte";
    let { AlertsNum, WoriginNum, ActivePage } = $props();
    function setActive(page) {
        if (ActivePage == page) {
            return "nav-item active";
        } else {
            return "nav-item";
        }
    }
</script>

<nav class="sidebar">
    <div class="logo-section">
        <img src="\src\assets\Edge_logo.png" alt="Egde Logo" height="50px" />
    </div>

    <div class="nav-menu">
        <div class={setActive("Home")} onclick={() => myVariable.set(Home)}>
            <svg class="nav-icon" viewBox="0 0 24 24">
                <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
                <polyline points="9 22 9 12 15 12 15 22"></polyline>
            </svg>
            Home
        </div>

        <div class={setActive("Alerts")} onclick={() => myVariable.set(Alerts)}>
            <svg class="nav-icon" viewBox="0 0 24 24">
                <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
                <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
            </svg>
            Alerts
            <div class="badge-container">
                <span class="badge red">{AlertsNum}</span>
                <span class="badge yellow">{WoriginNum}</span>
            </div>
        </div>

        <div class={setActive("AI Assistant")} onclick={() => myVariable.set(AIAssistrnt)}>
            <svg class="nav-icon" viewBox="0 0 24 24">
                <path
                    d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"
                ></path>
                <circle cx="9" cy="10" r="1"></circle>
                <circle cx="12" cy="10" r="1"></circle>
                <circle cx="15" cy="10" r="1"></circle>
            </svg>
            AI Assistant
        </div>
    </div>

    <button class="settings-btn" onclick={() => myVariable.set(Setting)}>
        <svg width="19" height="19" viewBox="0 0 19 19" fill="none">
            <path
                d="M9.45457 11.8184C10.76 11.8184 11.8182 10.7602 11.8182 9.45475C11.8182 8.14935 10.76 7.09112 9.45457 7.09112C8.14917 7.09112 7.09093 8.14935 7.09093 9.45475C7.09093 10.7602 8.14917 11.8184 9.45457 11.8184Z"
                stroke="black"
                stroke-opacity="0.68"
                stroke-width="1.57576"
                stroke-linecap="round"
                stroke-linejoin="round"
            />
            <path
                d="M15.2849 11.8184C15.18 12.056 15.1487 12.3196 15.1951 12.5752C15.2414 12.8308 15.3632 13.0666 15.5449 13.2523L15.5921 13.2996C15.7387 13.4459 15.8549 13.6197 15.9342 13.811C16.0135 14.0023 16.0543 14.2074 16.0543 14.4144C16.0543 14.6215 16.0135 14.8266 15.9342 15.0179C15.8549 15.2092 15.7387 15.383 15.5921 15.5293C15.4458 15.6758 15.272 15.792 15.0807 15.8713C14.8894 15.9506 14.6844 15.9914 14.4773 15.9914C14.2702 15.9914 14.0652 15.9506 13.8739 15.8713C13.6826 15.792 13.5088 15.6758 13.3624 15.5293L13.3152 15.482C13.1295 15.3004 12.8936 15.1785 12.6381 15.1322C12.3825 15.0859 12.1189 15.1171 11.8812 15.222C11.6482 15.3219 11.4495 15.4877 11.3095 15.6991C11.1695 15.9105 11.0944 16.1582 11.0934 16.4117V16.5457C11.0934 16.9636 10.9273 17.3644 10.6318 17.6599C10.3363 17.9554 9.93552 18.1214 9.5176 18.1214C9.09968 18.1214 8.69888 17.9554 8.40337 17.6599C8.10786 17.3644 7.94184 16.9636 7.94184 16.5457V16.4748C7.93574 16.214 7.85133 15.9611 7.69958 15.7489C7.54783 15.5367 7.33575 15.3751 7.09093 15.2851C6.8533 15.1802 6.58969 15.1489 6.33411 15.1952C6.07852 15.2416 5.84268 15.3634 5.65699 15.5451L5.60972 15.5923C5.46338 15.7388 5.28959 15.8551 5.09829 15.9344C4.907 16.0137 4.70195 16.0545 4.49487 16.0545C4.28779 16.0545 4.08275 16.0137 3.89145 15.9344C3.70016 15.8551 3.52637 15.7388 3.38002 15.5923C3.23352 15.446 3.11729 15.2722 3.03799 15.0809C2.95869 14.8896 2.91788 14.6846 2.91788 14.4775C2.91788 14.2704 2.95869 14.0654 3.03799 13.8741C3.11729 13.6828 3.23352 13.509 3.38002 13.3626L3.4273 13.3154C3.60893 13.1297 3.73078 12.8938 3.77712 12.6382C3.82346 12.3827 3.79218 12.1191 3.6873 11.8814C3.58742 11.6484 3.42159 11.4496 3.21021 11.3097C2.99883 11.1697 2.75113 11.0946 2.4976 11.0935H2.36366C1.94574 11.0935 1.54494 10.9275 1.24943 10.632C0.95392 10.3365 0.787903 9.9357 0.787903 9.51778C0.787903 9.09987 0.95392 8.69907 1.24943 8.40355C1.54494 8.10804 1.94574 7.94202 2.36366 7.94202H2.43457C2.69535 7.93592 2.94827 7.85151 3.16044 7.69976C3.37261 7.54801 3.53422 7.33594 3.62427 7.09112C3.72914 6.85348 3.76043 6.58987 3.71409 6.33429C3.66775 6.0787 3.5459 5.84286 3.36427 5.65718L3.31699 5.6099C3.17049 5.46356 3.05426 5.28977 2.97496 5.09848C2.89566 4.90718 2.85484 4.70213 2.85484 4.49506C2.85484 4.28798 2.89566 4.08293 2.97496 3.89163C3.05426 3.70034 3.17049 3.52655 3.31699 3.38021C3.46334 3.2337 3.63713 3.11747 3.82842 3.03817C4.01971 2.95887 4.22476 2.91806 4.43184 2.91806C4.63892 2.91806 4.84397 2.95887 5.03526 3.03817C5.22656 3.11747 5.40035 3.2337 5.54669 3.38021L5.59396 3.42748C5.77965 3.60911 6.01549 3.73096 6.27107 3.7773C6.52666 3.82364 6.79027 3.79236 7.0279 3.68748H7.09093C7.32396 3.58761 7.5227 3.42177 7.66269 3.21039C7.80268 2.99901 7.8778 2.75131 7.87881 2.49778V2.36384C7.87881 1.94593 8.04483 1.54513 8.34034 1.24961C8.63585 0.954103 9.03665 0.788086 9.45457 0.788086C9.87249 0.788086 10.2733 0.954103 10.5688 1.24961C10.8643 1.54513 11.0303 1.94593 11.0303 2.36384V2.43475C11.0313 2.68828 11.1065 2.93598 11.2464 3.14736C11.3864 3.35874 11.5852 3.52458 11.8182 3.62445C12.0558 3.72933 12.3194 3.76061 12.575 3.71427C12.8306 3.66793 13.0665 3.54608 13.2521 3.36445L13.2994 3.31718C13.4458 3.17067 13.6196 3.05444 13.8108 2.97514C14.0021 2.89584 14.2072 2.85503 14.4143 2.85503C14.6213 2.85503 14.8264 2.89584 15.0177 2.97514C15.209 3.05444 15.3828 3.17067 15.5291 3.31718C15.6756 3.46352 15.7918 3.63731 15.8711 3.8286C15.9504 4.0199 15.9913 4.22495 15.9913 4.43203C15.9913 4.6391 15.9504 4.84415 15.8711 5.03545C15.7918 5.22674 15.6756 5.40053 15.5291 5.54687L15.4818 5.59415C15.3002 5.77983 15.1784 6.01567 15.132 6.27126C15.0857 6.52684 15.117 6.79045 15.2218 7.02809V7.09112C15.3217 7.32415 15.4875 7.52289 15.6989 7.66287C15.9103 7.80286 16.158 7.87798 16.4115 7.87899H16.5455C16.9634 7.87899 17.3642 8.04501 17.6597 8.34052C17.9552 8.63604 18.1212 9.03684 18.1212 9.45475C18.1212 9.87267 17.9552 10.2735 17.6597 10.569C17.3642 10.8645 16.9634 11.0305 16.5455 11.0305H16.4746C16.221 11.0315 15.9733 11.1066 15.762 11.2466C15.5506 11.3866 15.3847 11.5854 15.2849 11.8184Z"
                stroke="black"
                stroke-opacity="0.68"
                stroke-width="1.57576"
                stroke-linecap="round"
                stroke-linejoin="round"
            />
        </svg>
        Settings
    </button>
</nav>

<style>
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }

    .sidebar {
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        align-items: flex-start;
        width: 190px;
        height: 100%;
        padding: 32px 16px;
        background-color: #fff;
        flex-shrink: 0;
    }

    .logo-section {
        margin-bottom: 60px;
    }

    .nav-menu {
        display: flex;
        flex-direction: column;
        gap: 16px;
        width: 100%;
        flex: 1;
    }

    .nav-item {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 12px;
        width: 100%;
        border-radius: 12px;
        color: #4a5568;
        text-decoration: none;
        cursor: pointer;
        transition: all 0.3s ease;
        position: relative;
    }

    .nav-item.active {
        border: 1px solid rgba(255, 86, 34, 0.2);
        background: rgba(255, 86, 34, 0.08);
        color: #ff5622;
        font-weight: 700;
        border-radius: 10px;
    }

    .nav-icon {
        width: 24px;
        height: 24px;
        stroke: currentColor;
        fill: none;
        stroke-width: 2;
        stroke-linecap: round;
        stroke-linejoin: round;
    }

    .badge-container {
        display: flex;
        gap: 6px;
        margin-left: auto;
        width: fit-content;
    }

    .badge {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 20px;
        height: 20px;
        border-radius: 50%;
        font-size: 12px;
        font-weight: 600;
        color: #fff;
    }

    .badge.red {
        background: #ef4444;
    }

    .badge.yellow {
        background: #fbbf24;
        color: #000;
    }

    .settings-btn {
        height: 48px;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        width: 100%;
        margin-top: auto;
        border: 1.5px solid #0000002a;
        border-radius: 50px;
        background: #fff;
        color: #4a5568;
        cursor: pointer;
        transition: all 0.3s ease;
    }

    .settings-icon {
        width: 18px;
        height: 18px;
    }
</style>

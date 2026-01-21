<!-- Modal.svelte -->
<script>
    export let open = false; // control from parent
    export let onClose = () => {}; // function to call when closing
    import { curentMode, isPassWordPopupOpen, USER_TOKEN } from "../../stores/AppStore.js";

    function selectMode(modeId) {
        if (modeId === "Live") {
            curentMode.set("Live");
            USER_TOKEN.set("");
        }
        if (modeId === "Test") {
            isPassWordPopupOpen.set(true);
        }
        onClose();
    }

    // Define the options matching your 'live' and 'test' variables
    const options = [
        {
            id: "Live",
            title: "Live Mode",
            description: "The MES system assumes full control of the machine.",
        },
        {
            id: "Test",
            title: "Test Mode",
            description:
                "This mode halts automatic production and enables manual operation.",
        },
    ];
</script>

{#if open}
    <!-- svelte-ignore a11y_click_events_have_key_events -->
    <!-- svelte-ignore a11y_no_static_element_interactions -->
    <div class="backdrop" onclick={onClose}>
        <div class="card">
            {#each options as option, index}
                <button
                    class="option-row"
                    onclick={() => selectMode(option.id)}
                    type="button"
                >
                    <div class="icon-container">
                        {#if $curentMode === option.id}
                            <div class="radio-checked">
                                <svg
                                    width="12"
                                    height="10"
                                    viewBox="0 0 12 10"
                                    fill="none"
                                    xmlns="http://www.w3.org/2000/svg"
                                >
                                    <path
                                        d="M1 5L4.5 8.5L11 1.5"
                                        stroke="white"
                                        stroke-width="2"
                                        stroke-linecap="round"
                                        stroke-linejoin="round"
                                    />
                                </svg>
                            </div>
                        {:else}
                            <div class="radio-unchecked"></div>
                        {/if}
                    </div>

                    <div class="text-content">
                        <h3 class="title">{option.title}</h3>
                        <p class="description">{option.description}</p>
                    </div>
                </button>

                {#if index < options.length - 1}
                    <div class="divider"></div>
                {/if}
            {/each}
        </div>
    </div>
{/if}

<style>
    /* Scoped Reset */
    * {
        box-sizing: border-box;
        margin: 0;
        padding: 0;
    }

    .backdrop {
        position: fixed;
        inset: 0; /* top:0 right:0 bottom:0 left:0 */
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 999; /* make sure it's on top */
    }

    /* Main Container */
    .card {
        position: absolute;
        top: 182px;
        left: 14px;
        background: white;
        width: 400px; /* Fixed width as per design intent */
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        padding: 24px;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
            Helvetica, Arial, sans-serif;
        box-sizing: border-box;
    }

    /* Clickable Row */
    .option-row {
        display: flex;
        align-items: flex-start;
        background: none;
        border: none;
        text-align: left;
        cursor: pointer;
        width: 100%;
        padding: 0;
        margin: 0;
    }

    /* Icon Spacing: 16px */
    .icon-container {
        margin-right: 16px;
        padding-top: 2px; /* Visual alignment with text */
        flex-shrink: 0;
    }

    /* Text Layout */
    .text-content {
        display: flex;
        flex-direction: column;
        gap: 4px; /* Tight spacing between title and desc */
    }

    /* Title Font: 16px */
    .title {
        font-size: 16px;
        font-weight: 600;
        color: #111827;
        margin: 0;
        line-height: 1.2;
    }

    /* Description Font: 14px */
    .description {
        font-size: 14px;
        color: #6b7280;
        margin: 0;
        line-height: 1.4;
    }

    /* Selected Icon Style */
    .radio-checked {
        width: 24px;
        height: 24px;
        background-color: #1d4ed8; /* Blue */
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    /* Unselected Icon Style */
    .radio-unchecked {
        width: 24px;
        height: 24px;
        border: 2px solid #5d5f63; /* Grey Border */
        border-radius: 50%;
        box-sizing: border-box;
    }

    /* Divider Spacing: 16px */
    .divider {
        height: 1px;
        background-color: #e5e7eb;
        margin: 16px 0 16px 0;
    }
</style>

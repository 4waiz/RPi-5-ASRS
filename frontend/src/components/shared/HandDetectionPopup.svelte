<script>
    let { open = false, onClose = () => {}, imageSrc = "" } = $props();
</script>

{#if open}
    <!-- svelte-ignore a11y_click_events_have_key_events -->
    <!-- svelte-ignore a11y_no_static_element_interactions -->
    <div class="backdrop" onclick={onClose}>
        <div class="popup-card" onclick={(e) => e.stopPropagation()}>
            <div class="popup-header">
                <h2>Live Feed</h2>
                <button class="close-btn" onclick={onClose} aria-label="Close">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M18 6L6 18M6 6L18 18" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </button>
            </div>
            <div class="video-container">
                {#if imageSrc}
                    <img src={imageSrc} alt="Live Stream" />
                {/if}
            </div>
        </div>
    </div>
{/if}

<style>
    * {
        box-sizing: border-box;
        margin: 0;
        padding: 0;
    }

    .backdrop {
        position: fixed;
        inset: 0;
        background: rgba(0, 0, 0, 0.7);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000;
    }

    .popup-card {
        background: #1a1a2e;
        border-radius: 16px;
        padding: 20px;
        max-width: 90%;
        max-height: 90%;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    .popup-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 16px;
    }

    .popup-header h2 {
        color: #ffffff;
        font-size: 20px;
        font-weight: 600;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }

    .close-btn {
        background: #ef4444;
        border: none;
        padding: 8px;
        border-radius: 8px;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: background 0.2s ease;
    }

    .close-btn:hover {
        background: #dc2626;
    }

    .video-container {
        border-radius: 12px;
        overflow: hidden;
        background: #000;
        width: 320px;
        height: 240px;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .video-container img {
        width: 100%;
        height: 100%;
        display: block;
        object-fit: contain;
    }

    .placeholder {
        color: #666;
        font-size: 14px;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
</style>

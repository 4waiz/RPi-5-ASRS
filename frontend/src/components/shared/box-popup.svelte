<!-- Modal.svelte -->
<script>
    export let open = false; // control from parent
    export let message = "Popup message ";
    export let imageSrc = ""; // optional image source
    export let onClose = () => {}; // function to call when closing
</script>


{#if open}
    <!-- svelte-ignore a11y_click_events_have_key_events -->
    <!-- svelte-ignore a11y_no_static_element_interactions -->
    <div class="backdrop" on:click={onClose}>
        <div class="card">
            <!-- Close Button -->
            <button class="close-btn" aria-label="Close" on:click={onClose}>
                <svg class="close-icon" viewBox="0 0 24 24" fill="none">
                    <path d="M18 6L6 18M6 6l12 12"></path>
                </svg>
            </button>
            <!-- Content -->
            <div class="content">
                <!-- Image Area -->
                <div class="image-placeholder">
                    <img src={imageSrc} alt="" style="height: 290.16px"/>
                </div>

                <!-- Message -->
                <p class="message">
                    {message}
                </p>

                <!-- Actions -->
                <div class="button-group">
                    <button class="btn btn-cancel">Cancel</button>
                    <button class="btn btn-confirm">Get Supplies</button>
                </div>
            </div>
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
    inset: 0;                /* top:0 right:0 bottom:0 left:0 */
    background: rgba(0,0,0,0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 999;            /* make sure it's on top */
  }

  /* === Card Container === */
  .card {
    position: relative;
    width: 600px;
    height: 560px;
    background-color: #ffffff;
    border-radius: 22px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
    display: flex;
    flex-direction: column;
    align-items: center;
    padding-top: 50px;
  }

  /* === Close Button === */
  .close-btn {
    position: absolute;
    top: 24px;
    left: 35px;
    width: 44px;
    height: 44px;
    border-radius: 50%;
    background-color: rgba(0, 0, 0, 0.08);
    border: none;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: background-color 0.2s;
  }

  .close-icon {
    width: 20px;
    height: 20px;
    stroke: #000;
    stroke-width: 2;
    stroke-linecap: round;
  }

  /* === Main Content Area === */
  .content {
    width: 470px;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 40px;
  }

  /* Image Placeholder */
  .image-placeholder {
    width: 365px;
    height: 250px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #888;
    font-size: 14px;
  }

  /* Text */
  .message {
    font-size: 26px;
    font-weight: 500;
    text-align: center;
    color: #000;
    line-height: 1.3;
    max-width: 400px;
  }

  /* === Buttons === */
  .button-group {
    display: flex;
    gap: 26px;
    width: 100%;
    padding: 0 50px;
  }

  .btn {
    flex: 1;
    height: 60px;
    width: 100%;
    border-radius: 9px;
    font-size: 18px;
    font-weight: 500;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: opacity 0.2s;
    border: none; /* Reset default border */
    
  }

  .btn-cancel {
    background-color: transparent;
    border: 1px solid rgba(0, 0, 0, 0.3);
    color: #000;
  }

  .btn-confirm {
    background-color: #30d158;
    color: #000;
  }
</style>
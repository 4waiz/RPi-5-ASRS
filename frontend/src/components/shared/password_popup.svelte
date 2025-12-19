<script>
  import Keyboard from "./Keyboard.svelte";
  export let open = false; // control from parent
  export let onClose = () => {}; // function to call when closing
  export let changeMode = true; // whether to switch to Test mode after login
  import { curentMode, isPassWordPopupOpen, USER_TOKEN } from "../../stores/AppStore.js";

  let username = "Admin";
  let password = "";
  let isLoading = false;
  let errorMessage = "";

  async function handleEnter() {
    if (!username || !password) {
      errorMessage = "Please enter password.";
      return;
    }

    isLoading = true;
    errorMessage = "";

    try {
      const response = await fetch("http://localhost:8010/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ username, password }),
      });

      if (response.ok) {
        const data = await response.json();
        USER_TOKEN.set(data.access_token);
        // Only change mode if changeMode is true (not from Settings page)
        if (changeMode) {
          curentMode.set("Test");
        }
        isPassWordPopupOpen.set(false);
        password = "";
        console.log(USER_TOKEN);
        onClose();
      } else {
        const error = await response.json();
        errorMessage = error.detail || "Invalid credentials. Please try again.";
        password = "";
      }
    } catch (err) {
      errorMessage = "Connection error. Please try again.";
      console.error("Auth error:", err);
    } finally {
      isLoading = false;
      password = "";
    }
  }


  function handleVirtualKey(event) {
    const key = event.detail;

    if (key === "backspace") {
      password = password.slice(0, -1);
    } else if (key === "space") {
      password += " ";
    } else if (key === "enter") {
      handleEnter();
    } else if (
      ["shift", "ctrl", "alt", "win", "caps lock", "tab", "del"].includes(key)
    ) {
      console.log("Modifier pressed:", key);
    } else {
      const charToAdd = key.split(" ").pop();
      password += charToAdd;
    }
  }
</script>

{#if open}
  <!-- svelte-ignore a11y_click_events_have_key_events -->
  <!-- svelte-ignore a11y_no_static_element_interactions -->
    <!-- svelte-ignore a11y_no_noninteractive_element_interactions -->
    <div class="page-container" onclick={onClose}>
      <section class="top-section">
        <div class="modal" onclick={(e) => e.stopPropagation()}>
          <h1 class="title">Enter the Password</h1>
          <p class="subtitle">
            This is a protected feature for admin users only.
          </p>

          {#if errorMessage}
            <p class="error-message">{errorMessage}</p>
          {/if}

          <div class="input-wrapper">
            <input
              type="password"
              bind:value={password}
              placeholder="Enter password..."
              onkeydown={(e) => e.key === 'Enter' && handleEnter()}
            />
          </div>

          {#if isLoading}
            <p class="loading">Authenticating...</p>
          {/if}
        </div>
      </section>

      <section class="bottom-section" onclick={(e) => e.stopPropagation()}>
        <Keyboard on:keypress={handleVirtualKey} />
      </section>
    </div>
{/if}

<style>
  /* Scoped Reset */
  * {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }


  .page-container {
    display: flex;
    flex-direction: column;
    height: 100vh;
    width: 100%;
    position: fixed;
    background-color: rgba(0, 0, 0, 0.5);
    inset: 0; /* top:0 right:0 bottom:0 left:0 */
    z-index: 999; /* make sure it's on top */
  }

  /* --- Top Section Styling --- */
  .top-section {
    flex: 1; /* Takes up remaining space */
    display: flex;
    align-items: center; /* Center Vertically */
    justify-content: center; /* Center Horizontally */
    min-height: 200px; /* Ensure space for modal */
  }

  .modal {
    background-color: #eeeeee;
    border-radius: 20px;
    padding: 24px; /* Side padding based on redlines (blue 48 box) */
    text-align: center;
    width: 100%;
    max-width: 500px;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  }

  .title {
    font-size: 28px; /* Requested font size */
    font-weight: 500;
    color: #111;
    margin: 0px;
  }

  .subtitle {
    font-size: 16px; /* Requested font size */
    color: #6b7280;
    margin: 0 0 30px 0; /* Approximate gap */
  }

  .input-wrapper {
    /* Padding around the input as seen in redlines (blue 24 box) */
    padding-top: 0px;
    padding-bottom: 0px;
    border-top: 1px dashed #ccc; /* Visual aid similar to redlines, remove if strictly UI */
    border-bottom: 1px dashed #ccc; /* Visual aid similar to redlines, remove if strictly UI */
  }

  /* Actual Input Field Styling */
  input {
    width: 100%;
    padding: 16px;
    font-size: 24px;
    background-color: #e5e5e5;
    border: 1px solid #999;
    border-radius: 8px;
    outline: none;
    text-align: left;
    letter-spacing: 4px; /* Space out the dots/asterisks */
    box-sizing: border-box;
  }

  /* Make the asterisk dots look larger/centered if desired */
  input::placeholder {
    letter-spacing: 1px;
    font-size: 16px;
  }

  /* --- Bottom Section Styling --- */
  .bottom-section {
    background-color: white;
    border-top: 1px solid #e5e5e5;
  }
</style>

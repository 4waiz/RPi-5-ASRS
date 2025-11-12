<script>
  import SideBar from "../lib/side-bar.svelte";

  // --- counts shown next to "Alerts" (red) and warning (yellow) ---
  // Replace with your real store later; this mirrors how other pages pass them.
  let Alerts = [2, 5];             // [alertsNum, warningNum]
  let AlertsNum = Alerts[0];
  let WoriginNum = Alerts[1];

  // IMPORTANT: this must match the label used in side-bar.svelte
  let ActivePage = "AI Assistant";

  // simple local chat state (placeholder)
  let messages = $state([
    { role: "assistant", text: "Hi! How can I help you at the station today?" }
  ]);
  let draft = $state("");

  function send() {
    const t = draft.trim();
    if (!t) return;
    messages = [...messages, { role: "user", text: t }];
    messages = [...messages, { role: "assistant", text: `Got it — logging: “${t}”.` }];
    draft = "";
    queueMicrotask(() => {
      const scroller = document.querySelector(".chat-scroll");
      if (scroller) scroller.scrollTop = scroller.scrollHeight;
    });
  }

  function onSubmit(e) {
    e.preventDefault();
    send();
  }
</script>

<div class="page">
  <SideBar {WoriginNum} {AlertsNum} {ActivePage} />

  <section class="right">
    <h1 class="title">AI Assistant</h1>

    <div class="chat-card">
      <div class="chat-scroll">
        {#each messages as m}
          <div class="bubble {m.role}">
            <div class="txt">{m.text}</div>
          </div>
        {/each}
      </div>

      <!-- Svelte 5 prefers `onsubmit` (not `on:submit`) -->
      <form class="composer" onsubmit={onSubmit}>
        <input
          class="input"
          bind:value={draft}
          placeholder="Type a message…"
          autocomplete="off"
        />
        <button class="send" type="submit" aria-label="Send">Send</button>
      </form>
    </div>
  </section>
</div>

<style>
  .page {
    display: grid;
    grid-template-columns: 220px 1fr; /* your sidebar width */
    gap: 0;                           /* keep this 0 to avoid a black line */
    min-height: 100vh;
    width: 100%;
    background: #f2f2f2;
  }

  .right {
    background: #f2f2f2;
    padding: 24px;
    display: flex;
    flex-direction: column;
    gap: 16px;
    margin: 0;
  }

  .title {
    font-size: 28px;
    font-weight: 800;
    margin: 0 0 4px 0;
  }

  .chat-card {
    display: flex;
    flex-direction: column;
    gap: 12px;
    background: #fff;
    border: 1px solid #ececec;
    border-radius: 12px;
    padding: 12px;
    flex: 1 1 auto;
    width: 100%;
    max-width: 1100px;
  }

  .chat-scroll {
    overflow: auto;
    flex: 1 1 auto;
    display: flex;
    flex-direction: column;
    gap: 10px;
    min-height: 320px;
    padding-right: 4px;
  }

  .bubble {
    max-width: min(72ch, 90%);
    padding: 10px 12px;
    border-radius: 12px;
    line-height: 1.35;
    border: 1px solid #e8e8e8;
  }
  .bubble.user {
    margin-left: auto;
    background: #f2f5ff;
    border-color: #dbe4ff;
  }
  .bubble.assistant {
    margin-right: auto;
    background: #f9fafb;
  }
  .txt { white-space: pre-wrap; }

  .composer {
    display: grid;
    grid-template-columns: 1fr auto;
    gap: 10px;
    padding-top: 6px;
    border-top: 1px dashed #eee;
  }

  .input {
    width: 100%;
    padding: 12px 14px;
    border-radius: 10px;
    border: 1px solid #ddd;
    outline: none;
    background: #fff;
  }
  .input:focus { border-color: #c9c9c9; }

  .send {
    padding: 12px 16px;
    border-radius: 10px;
    border: 1px solid #ddd;
    background: #fff;
    cursor: pointer;
  }
  .send:hover { background: #fafafa; }
</style>

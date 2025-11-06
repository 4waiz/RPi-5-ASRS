<!-- NotificationCard.svelte -->
<script>
  export let title = "Box 1 retrieved";
  export let timestamp = "12:10pm";
</script>

<div class="notification-card">
  <div class="icon-container">
    <svg 
      class="checkmark" 
      width="24" 
      height="24" 
      viewBox="0 0 24 24" 
      fill="none" 
      stroke="currentColor" 
      stroke-width="2.5"
    >
      <polyline points="20 6 9 17 4 12"></polyline>
    </svg>
  </div>
  
  <div class="content">
    <h3 class="title">{title}</h3>
    <p class="timestamp">Done at {timestamp}</p>
  </div>
</div>

<style>
  .notification-card {
    border-radius: 17.134px;
    border: 1.606px solid rgba(0, 0, 0, 0.24);
    box-shadow: 
      0 0 0.535px 0 rgba(66, 71, 76, 0.32), 
      0 4.284px 8.567px 0 rgba(66, 71, 76, 0.05), 
      0 4.284px 42.836px 0 #EEE;
    display: flex;
    flex-direction: row;
    align-items: center;
    width: 290px;
    height: 68px;
    padding: 14.993px 19.276px 14.993px 14.993px;
    gap: 16px;
    flex-shrink: 0;
  }

  .icon-container {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 40px;
    height: 40px;
    background: #00000025;
    border-radius: 10px;
    flex-shrink: 0;
  }

  .checkmark {
    color: #374151;
  }

  .content {
    display: flex;
    flex-direction: column;
    gap: 2px;
    flex: 1;
    min-width: 0;
  }

  .title {
    margin: 0;
    font-size: 16px;
    font-weight: 600;
    color: #111827;
    line-height: 1.3;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .timestamp {
    margin: 0;
    font-size: 13px;
    color: #6b7280;
    line-height: 1.4;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
</style>

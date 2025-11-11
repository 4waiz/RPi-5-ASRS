<script>
  // NOTE: You must provide the actual path to your ImageInventory component
  import ImageInventory from "../image-inventory.svelte";
  import NotificationCard from "../notificationCard.svelte";

  // Define notification cards data
  let cardNotificationData = $state([
    { title: "Box 1 retrieved", timestamp: "Done at 12:10pm" },
    { title: "Box 2 retrieved", timestamp: "Done at 1:45pm" },
    { title: "Box 3 retrieved", timestamp: "Done at 3:20pm" }
  ]);

  // 1. FIX: Define colorArray using $state() to make it reactive
  let colorArray = $state([
    "grey",
    "green",
    "red",
    "green",
    "grey",
    "red",
    "green",
    "grey",
    "red",
    "green",
    "grey",
    "red",
    "green",
    "red",
    "grey",
    "green",
    "grey",
    "green",
    "red",
    "green",
    "grey",
    "green",
    "red",
    "grey",
  ]);

  // Derived state to count each color
  let fullCount = $derived(colorArray.filter(color => color === "green").length);
  let partiallyFullCount = $derived(colorArray.filter(color => color === "grey").length);
  let emptyCount = $derived(colorArray.filter(color => color === "red").length);

  const colors = ["red", "green", "grey"];

  // This function picks a random color from the 'colors' array
  function getRandomColor() {
    const randomIndex = Math.floor(Math.random() * colors.length);
    return colors[randomIndex];
  }

  // 2. Add $effect to handle the 2-second interval
  $effect(() => {
    // Start an interval to update the array every 2 seconds
    const intervalId = setInterval(() => {
      // Update each item in the array to a new random color
      for (let i = 0; i < colorArray.length; i++) {
        colorArray[i] = getRandomColor();
      }
    }, 2000);
    return () => {
      clearInterval(intervalId);
    };
  });
</script>

<div class="main">
  <div class="notifications-container">
    <h2>Live Operations</h2>
    <div class="live-operations-container">
      {#each cardNotificationData as notification}
        <NotificationCard 
          title={notification.title} 
          timestamp={notification.timestamp} 
        />
      {/each}
    </div>
    <div class="legend">
      <div class="legend-item">
        <span class="dot full"></span>
        <span>{fullCount} : Full</span>
      </div>
      <div class="legend-item">
        <span class="dot partially-full"></span>
        <span>{partiallyFullCount} : Partially full.</span>
      </div>
      <div class="legend-item">
        <span class="dot empty"></span>
        <span>{emptyCount} : Empty</span>
      </div>
    </div>
  </div>

  <div class="inve">
    <ImageInventory {colorArray} />
  </div>
</div>

<style>
  .inve {
    margin-top: 20px;
  }
  .main {
    width: 100%;
    height: fit-content;
    display: flex;
    flex-direction: row;
    gap: 32px;
    background-color: #ebebeb;
    box-sizing: border-box;
    padding-right: 32px;
  }

  .notifications-container {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  /* Styles for Live Operations Section */

  .live-operations-container {
    width: fit-content;
    box-sizing: border-box;
    padding-left: 8px;
    border-left: blue 2px solid;
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  h2 {
    margin: 0 0 12px 0;
    color: blue;
  }

  /* Legend Styling */
  .legend {
    margin: 0px;
    margin-top: 12px;
    display: flex;
    flex-direction: row;
    gap: 8px;
    align-items: center;
    flex-wrap: wrap;
    width: 250px;
  }

  .legend-item {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 14px;
    color: #333333;
    width: fit-content;
  }

  .dot {
    width: 16px;
    height: 16px;
    border-radius: 50%;
    flex-shrink: 0;
  }

  .dot.full {
    background-color: #4caf50;
  }

  .dot.partially-full {
    background-color: #d3d3d3;
    border: 2px solid #999999;
  }

  .dot.empty {
    background-color: #ff3b30;
  }
</style>

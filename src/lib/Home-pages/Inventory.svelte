<script>
  import { onMount, onDestroy } from "svelte";
  import InventoryImage from '../../assets/inventory/Inventory.png';

  // Define notification cards data
  let cardNotificationData = $state([
    { title: "Box 1 retrieved", timestamp: "12:10pm" },
    { title: "Box 2 retrieved", timestamp: "1:45pm" },
    { title: "Box 3 retrieved", timestamp: "3:20pm" }
  ]);

  // Define colorArray using $state() to make it reactive
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

  function getRandomColor() {
    const randomIndex = Math.floor(Math.random() * colors.length);
    return colors[randomIndex];
  }

  let interval;

  // Update colors dynamically to show liveness
  function updateColors() {
    // Randomly change 2-4 boxes each update
    const numChanges = Math.floor(Math.random() * 3) + 2; // 2 to 4 changes

    for (let i = 0; i < numChanges; i++) {
      const randomIndex = Math.floor(Math.random() * colorArray.length);
      colorArray[randomIndex] = getRandomColor();
    }
  }

  let isVisible = $state(true);

  onMount(() => {
    // Start interval only when visible
    if (isVisible) {
      interval = setInterval(updateColors, 3000);
    }

    // Pause/resume based on page visibility
    const handleVisibilityChange = () => {
      if (document.hidden) {
        // Page is hidden, stop the interval
        if (interval) {
          clearInterval(interval);
          interval = null;
        }
        isVisible = false;
      } else {
        // Page is visible again, restart the interval
        isVisible = true;
        if (!interval) {
          interval = setInterval(updateColors, 3000);
        }
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);

    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      if (interval) {
        clearInterval(interval);
      }
    };
  });

  onDestroy(() => {
    if (interval) {
      clearInterval(interval);
    }
  });
</script>

<div class="main">
  <div class="notifications-container">
    <h2>Live Operations</h2>
    <div class="live-operations-container">
      {#each cardNotificationData as notification}
        <!-- NotificationCard component merged inline -->
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
            <h3 class="title">{notification.title}</h3>
            <p class="timestamp">Done at {notification.timestamp}</p>
          </div>
        </div>
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
    <!-- ImageInventory component merged inline -->
    <div class="image-container">
      <img src={InventoryImage} alt="Inventory Image" class="inventory-image" />

      <div class="boxs-con">
        {#each colorArray as color, index}
          <div class="box-container">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 55 22"
              fill="none"
              class={color}
            >
              <g filter="url(#filter0_d_664_1718)">
                <g clip-path="url(#clip0_664_1718)">
                  <rect x="1" width="53" height="19" rx="2" fill="#FFFF" />
                  <rect
                    x="2"
                    y="1"
                    width="51"
                    height="17"
                    rx="1"
                    stroke="black"
                    stroke-opacity="0.19"
                    stroke-width="2"
                  />
                  <path
                    d="M14 14.5288C14 13.9115 14.5004 13.4111 15.1176 13.4111H39.7059C40.3231 13.4111 40.8235 13.9115 40.8235 14.5288V18.9994H14V14.5288Z"
                    fill="black"
                    fill-opacity="0.3"
                  />
                </g>
              </g>
              <defs>
                <filter
                  id="filter0_d_664_1718"
                  x="0"
                  y="0"
                  width="55"
                  height="22"
                  filterUnits="userSpaceOnUse"
                  color-interpolation-filters="sRGB"
                >
                  <feFlood flood-opacity="0" result="BackgroundImageFix" />
                  <feColorMatrix
                    in="SourceAlpha"
                    type="matrix"
                    values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0"
                    result="hardAlpha"
                  />
                  <feOffset dy="2" />
                  <feGaussianBlur stdDeviation="0.5" />
                  <feComposite in2="hardAlpha" operator="out" />
                  <feColorMatrix
                    type="matrix"
                    values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.3 0"
                  />
                  <feBlend
                    mode="normal"
                    in2="BackgroundImageFix"
                    result="effect1_dropShadow_664_1718"
                  />
                  <feBlend
                    mode="normal"
                    in="SourceGraphic"
                    in2="effect1_dropShadow_664_1718"
                    result="shape"
                  />
                </filter>
                <clipPath id="clip0_664_1718">
                  <rect x="1" width="53" height="19" rx="2" fill="white" />
                </clipPath>
              </defs>
            </svg>
          </div>
        {/each}
      </div>
    </div>
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

  /* NotificationCard styles (merged inline) */
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

  /* ImageInventory styles (merged inline) */
  .image-container {
    position: relative;
    width: 415px;
    height: auto;
  }

  .inventory-image {
    width: 100%;
    display: block;
    margin: 0;
  }

  .boxs-con {
    display: grid;
    grid-template-columns: repeat(4, 53px);
    grid-template-rows: repeat(6, 19px);
    grid-column-gap: 18px;
    grid-row-gap: 16px;
    position: absolute;
    top: 54px;
    left: 74px;
    padding: 0;
    margin: 0;
  }

  .box-container {
    width: 100%;
    height: 100%;
    margin: 0;
  }

  .box-container svg {
    width: 56px;
    height: 22px;
    margin: 0;
    display: block;
  }

  .box-container svg rect:first-of-type {
    transition: fill 0.5s ease-in-out;
  }

  /* Define the color classes */
  .red rect:first-of-type {
    fill: #ef4444 !important;
  }

  .green rect:first-of-type {
    fill: #22c55e !important;
  }

  .grey rect:first-of-type {
    fill: #6b7280 !important;
  }
</style>
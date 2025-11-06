<script>
  // Import the image for use
  let { colorArray = Array(24).fill('grey') } = $props();
  import InventoryImage from '../assets/Inventory.png';
</script>

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

<style>
  /* The container for both the image and the boxes */
  .image-container {
    position: relative;
    width: 415px; /* Width of the image */
    height: auto;
  }

  /* The image will be the background */
  .inventory-image {
    width: 100%; /* Fill the container */
    display: block;
    margin: 0; /* Ensure no margin around the image */
  }

  /* The container for the grid of boxes */
  .boxs-con {
    display: grid;
    /* FIX 1: Set grid columns and rows to your exact pixel size */
    grid-template-columns: repeat(4, 53px); /* 4 columns of 53px */
    grid-template-rows: repeat(6, 19px); /* 6 rows of 19px */
    
    grid-column-gap: 18px; /* Set horizontal gap */
    grid-row-gap: 16px; /* Set vertical gap */
    position: absolute;
    top: 54px;
    left: 74px;
    
    /* NOTE: width: 100% and height: 100% are removed.
      The grid will now have a fixed size based on the columns/rows.
    */
    padding: 0; /* Ensure no padding */
    margin: 0; /* Ensure no margin */
  }

  .box-container {
    /* FIX 2: Flex centering is no longer needed
      since the cell and SVG are the same size.
    */
    width: 100%;
    height: 100%;
    margin: 0; /* Ensure no margin between boxes */
  }

  .box-container svg {
    /* FIX 3: Set the SVG size to your requested dimensions */
    width: 56px;
    height: 22px;
    
    transition: fill 0.3s ease;
    margin: 0; /* Ensure no margin around the SVG */
    display: block; /* Good practice for SVGs in layouts */
  }

  /* Define the color classes */
  .red {
    fill: red;
  }

  .green {
    fill: green;
  }

  .grey {
    fill: rgb(81, 81, 81);
  }
</style>
import * as THREE from "../libs/three.module.js";
import { GLTFLoader } from "../libs/GLTFLoader.js";
import { OrbitControls } from "../libs/OrbitControls.js";


// ============================================================================
// GLOBAL VARIABLES & CONSTANTS
// ============================================================================
let scene, camera, renderer, crane, belt, controls, container3D;
let raycaster, mouse;
let boxGrid = [];
let currentlyMovingBox = null;
let isMoving = false;
let animationFrameId = null;
let clock = new THREE.Clock();
let craneMixer, beltMixer;
let craneAction, beltAction;
let animationProgress = 0;
let operationQueue = [];
let currentOperation = null;
let nextOperationId = 1;

// Constants for grid layout and box dimensions
const BOX_WIDTH = 40;
const BOX_HEIGHT = 20;
const BOX_DEPTH = 30;

const GRID_ROWS = 4;
const GRID_COLUMNS = 6;

const START_X = 70;
const START_Z = 110;
const GAP = 4;

// Pre-calculated positions for the grid (6 columns x 4 rows)
const X_POSITIONS = [70, 114, 158, 202, 246, 290]; // 6 positions in X
const Z_POSITIONS = [110, 70, 30, -10]; // 4 positions in Z

// Animation speed control
const ANIMATION_DURATION = 5; // seconds for full retrieval or insertion

// Colors for box status
const BOX_COLOR_IN = 0x226622;
const BOX_COLOR_OUT = 0x444444;

// Max and Min coordinates for shelves
const MIN_Y = 0;
const MAX_Y = 100;

// Define positions
const POSITIONS = {
  SHELF_Y_LEVELS: [0, 25, 50, 75], // Four levels for Y positions
  CRANE_START: { x: 60, y: 100, z: 125 },
  CRANE_ABOVE_SHELVES_Y: 120,
  BELT_POSITION: { x: 200, y: 15, z: -60 },
  ENTRY_POSITION: { x: 200, y: 0, z: -105 },
  EXIT_POSITION: { x: 200, y: 0, z: -100 },
  ROW_Z_POSITIONS: [110, 70, 30, -10], // Shelf row Z coordinates
  COLUMN_X_POSITIONS: [70, 114, 158, 202, 246, 290], // Shelf column X coordinates
  ENTRY_GATE_X: 206,
  POST_OUT_X: 260,
  ENTRY_GATE_Z: -15,
  EXIT_GATE_Z: -65
};

// ============================================================================
const VECTOR_C = {
  x: 200,
  y: 100,
  z: 125
};

// Initialize system state
const systemState = {
  isCraneAvailable: true,
  selectedBox: null,
  boxes: [],
  operations: new Map(),
  listeners: new Set(),

  // Job queue for operations
  isOperationInProgress() {
    return currentOperation !== null;
  },

  // Register a listener for state changes
  addListener(callback) {
    this.listeners.add(callback);
  },

  // Unregister a listener
  removeListener(callback) {
    this.listeners.delete(callback);
  },

  // Notify listeners about state change
  notifyListeners() {
    this.listeners.forEach(callback => callback(this));
  },

  setSelectedBox(boxName) {
    this.selectedBox = boxName;
    this.notifyListeners();
  },

  updateBoxStatus(boxName, status, payload) {
    const box = this.boxes.find(b => b.name === boxName);
    if (box) {
      box.status = status;
      box.payload = payload;
      this.notifyListeners();
    }
  },

  logOperation(type, boxName, status, metadata = {}) {
    const operation = {
      id: nextOperationId++,
      timestamp: new Date().toISOString(),
      type,
      boxName,
      status,
      metadata
    };
    this.operations.set(operation.id, operation);
    this.notifyListeners();
    return operation.id;
  },

  updateOperationStatus(operationId, status, metadata = {}) {
    const operation = this.operations.get(operationId);
    if (operation) {
      operation.status = status;
      Object.assign(operation.metadata, metadata);
      this.notifyListeners();
    }
  }
};


// ============================================================================
// BOX DATA - 6x4 Grid (24 boxes)
// ============================================================================
const SHELF_DATA = [
  [
    {
      name: "Box Rose-in-01",
      status: "In",
      payload: "full",
      position: { x: X_POSITIONS[0], y: POSITIONS.SHELF_Y_LEVELS[0], z: POSITIONS.ROW_Z_POSITIONS[0] }
    },
    {
      name: "Box Rose-in-02",
      status: "In",
      payload: "empty",
      position: { x: X_POSITIONS[1], y: POSITIONS.SHELF_Y_LEVELS[0], z: POSITIONS.ROW_Z_POSITIONS[0] }
    },
    {
      name: "Box Rose-out-03",
      status: "Out",
      payload: "partially full",
      position: { x: X_POSITIONS[2], y: POSITIONS.SHELF_Y_LEVELS[0], z: POSITIONS.ROW_Z_POSITIONS[0] }
    },
    {
      name: "Box Rose-in-04",
      status: "In",
      payload: "full",
      position: { x: X_POSITIONS[3], y: POSITIONS.SHELF_Y_LEVELS[0], z: POSITIONS.ROW_Z_POSITIONS[0] }
    },
    {
      name: "Box Rose-in-05",
      status: "In",
      payload: "empty",
      position: { x: X_POSITIONS[4], y: POSITIONS.SHELF_Y_LEVELS[0], z: POSITIONS.ROW_Z_POSITIONS[0] }
    },
    {
      name: "Box Rose-in-06",
      status: "In",
      payload: "partially full",
      position: { x: X_POSITIONS[5], y: POSITIONS.SHELF_Y_LEVELS[0], z: POSITIONS.ROW_Z_POSITIONS[0] }
    }
  ],
  [
    {
      name: "Box Tulip-out-07",
      status: "Out",
      payload: "empty",
      position: { x: X_POSITIONS[0], y: POSITIONS.SHELF_Y_LEVELS[1], z: POSITIONS.ROW_Z_POSITIONS[1] }
    },
    {
      name: "Box Tulip-in-08",
      status: "In",
      payload: "full",
      position: { x: X_POSITIONS[1], y: POSITIONS.SHELF_Y_LEVELS[1], z: POSITIONS.ROW_Z_POSITIONS[1] }
    },
    {
      name: "Box Tulip-in-09",
      status: "In",
      payload: "partially full",
      position: { x: X_POSITIONS[2], y: POSITIONS.SHELF_Y_LEVELS[1], z: POSITIONS.ROW_Z_POSITIONS[1] }
    },
    {
      name: "Box Tulip-in-10",
      status: "In",
      payload: "empty",
      position: { x: X_POSITIONS[3], y: POSITIONS.SHELF_Y_LEVELS[1], z: POSITIONS.ROW_Z_POSITIONS[1] }
    },
    {
      name: "Box Tulip-in-11",
      status: "In",
      payload: "full",
      position: { x: X_POSITIONS[4], y: POSITIONS.SHELF_Y_LEVELS[1], z: POSITIONS.ROW_Z_POSITIONS[1] }
    },
    {
      name: "Box Tulip-in-12",
      status: "In",
      payload: "empty",
      position: { x: X_POSITIONS[5], y: POSITIONS.SHELF_Y_LEVELS[1], z: POSITIONS.ROW_Z_POSITIONS[1] }
    }
  ],
  [
    {
      name: "Box Lily-in-13",
      status: "In",
      payload: "partially full",
      position: { x: X_POSITIONS[0], y: POSITIONS.SHELF_Y_LEVELS[2], z: POSITIONS.ROW_Z_POSITIONS[2] }
    },
    {
      name: "Box Lily-in-14",
      status: "In",
      payload: "empty",
      position: { x: X_POSITIONS[1], y: POSITIONS.SHELF_Y_LEVELS[2], z: POSITIONS.ROW_Z_POSITIONS[2] }
    },
    {
      name: "Box Lily-in-15",
      status: "In",
      payload: "full",
      position: { x: X_POSITIONS[2], y: POSITIONS.SHELF_Y_LEVELS[2], z: POSITIONS.ROW_Z_POSITIONS[2] }
    },
    {
      name: "Box Lily-out-16",
      status: "Out",
      payload: "empty",
      position: { x: X_POSITIONS[3], y: POSITIONS.SHELF_Y_LEVELS[2], z: POSITIONS.ROW_Z_POSITIONS[2] }
    },
    {
      name: "Box Lily-in-17",
      status: "In",
      payload: "partially full",
      position: { x: X_POSITIONS[4], y: POSITIONS.SHELF_Y_LEVELS[2], z: POSITIONS.ROW_Z_POSITIONS[2] }
    },
    {
      name: "Box Lily-in-18",
      status: "In",
      payload: "empty",
      position: { x: X_POSITIONS[5], y: POSITIONS.SHELF_Y_LEVELS[2], z: POSITIONS.ROW_Z_POSITIONS[2] }
    }
  ],
  [
    {
      name: "Box Daisy-in-19",
      status: "In",
      payload: "full",
      position: { x: X_POSITIONS[0], y: POSITIONS.SHELF_Y_LEVELS[3], z: POSITIONS.ROW_Z_POSITIONS[3] }
    },
    {
      name: "Box Daisy-in-20",
      status: "In",
      payload: "empty",
      position: { x: X_POSITIONS[1], y: POSITIONS.SHELF_Y_LEVELS[3], z: POSITIONS.ROW_Z_POSITIONS[3] }
    },
    {
      name: "Box Daisy-in-21",
      status: "In",
      payload: "partially full",
      position: { x: X_POSITIONS[2], y: POSITIONS.SHELF_Y_LEVELS[3], z: POSITIONS.ROW_Z_POSITIONS[3] }
    },
    {
      name: "Box Daisy-in-22",
      status: "In",
      payload: "full",
      position: { x: X_POSITIONS[3], y: POSITIONS.SHELF_Y_LEVELS[3], z: POSITIONS.ROW_Z_POSITIONS[3] }
    },
    {
      name: "Box Daisy-out-23",
      status: "Out",
      payload: "empty",
      position: { x: X_POSITIONS[4], y: POSITIONS.SHELF_Y_LEVELS[3], z: POSITIONS.ROW_Z_POSITIONS[3] }
    },
    {
      name: "Box Daisy-in-24",
      status: "In",
      payload: "partially full",
      position: { x: X_POSITIONS[5], y: POSITIONS.SHELF_Y_LEVELS[3], z: POSITIONS.ROW_Z_POSITIONS[3] }
    }
  ]
];

// Populate the system box data
SHELF_DATA.forEach((row, rowIndex) => {
  row.forEach((box, columnIndex) => {
    systemState.boxes.push({
      ...box,
      row: rowIndex,
      column: columnIndex
    });
  });
});

// ============================================================================
// DOM ELEMENTS
// ============================================================================
container3D = document.getElementById("container3D");


// ============================================================================
// INITIALIZATION FUNCTIONS
// ============================================================================
function initScene() {
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0xf0f0f0);

  camera = new THREE.PerspectiveCamera(
    60,
    window.innerWidth / window.innerHeight,
    0.1,
    1000
  );
  camera.position.set(300, 200, 300);

  renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.shadowMap.enabled = true;
  container3D.appendChild(renderer.domElement);

  controls = new OrbitControls(camera, renderer.domElement);
  controls.target.set(160, 50, 50);
  controls.update();

  raycaster = new THREE.Raycaster();
  mouse = new THREE.Vector2();

  // Lights
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
  scene.add(ambientLight);

  const directionalLight = new THREE.DirectionalLight(0xffffff, 0.6);
  directionalLight.position.set(100, 200, 100);
  directionalLight.castShadow = true;
  directionalLight.shadow.mapSize.width = 2048;
  directionalLight.shadow.mapSize.height = 2048;
  scene.add(directionalLight);

  // Ground
  const groundGeometry = new THREE.PlaneGeometry(1000, 1000);
  const groundMaterial = new THREE.MeshPhongMaterial({
    color: 0x999999,
    depthWrite: false
  });
  const ground = new THREE.Mesh(groundGeometry, groundMaterial);
  ground.rotation.x = -Math.PI / 2;
  ground.position.y = -1;
  ground.receiveShadow = true;
  scene.add(ground);

  // Grid Helper
  const gridHelper = new THREE.GridHelper(1000, 100, 0x000000, 0x000000);
  gridHelper.position.y = -0.99;
  scene.add(gridHelper);
}

function loadModel() {
  const loader = new GLTFLoader();
  loader.load(
    "../models/asrs.glb",
    (gltf) => {
      const model = gltf.scene;
      model.traverse((child) => {
        if (child.isMesh) {
          child.castShadow = true;
          child.receiveShadow = true;
        }
        if (child.name === "crane") crane = child;
        if (child.name === "belt") belt = child;
      });

      scene.add(model);

      // Create Animation Mixers if animations exist
      if (gltf.animations && gltf.animations.length > 0) {
        craneMixer = new THREE.AnimationMixer(model);
        beltMixer = new THREE.AnimationMixer(model);

        gltf.animations.forEach((clip) => {
          if (clip.name.toLowerCase().includes("crane")) {
            craneAction = craneMixer.clipAction(clip);
            craneAction.loop = THREE.LoopOnce;
            craneAction.clampWhenFinished = true;
          } else if (clip.name.toLowerCase().includes("belt")) {
            beltAction = beltMixer.clipAction(clip);
            beltAction.loop = THREE.LoopRepeat;
          }
        });
      }

      createBoxGrid();
      updateStatusCounts();
      populateBoxList();

      // Add click event listener for box selection
      renderer.domElement.addEventListener("click", onBoxClick);
    },
    undefined,
    (error) => {
      console.error("Error loading the GLTF model:", error);
      showToast("Failed to load the 3D model. Please refresh the page.", "error");
    }
  );
}


// ============================================================================
// BOX GRID CREATION AND MANAGEMENT
// ============================================================================
function createBoxGrid() {
  const boxMaterialIn = new THREE.MeshPhongMaterial({ color: BOX_COLOR_IN });
  const boxMaterialOut = new THREE.MeshPhongMaterial({ color: BOX_COLOR_OUT });

  SHELF_DATA.forEach((row, rowIndex) => {
    const boxRow = [];
    row.forEach((boxData, columnIndex) => {
      const geometry = new THREE.BoxGeometry(BOX_WIDTH, BOX_HEIGHT, BOX_DEPTH);
      const material = boxData.status === "In" ? boxMaterialIn : boxMaterialOut;
      const box = new THREE.Mesh(geometry, material);

      // Use the default position from SHELF_DATA
      box.position.set(
        boxData.position.x,
        boxData.position.y,
        boxData.position.z
      );

      box.castShadow = true;
      box.receiveShadow = true;

      // Store box metadata
      box.userData = {
        name: boxData.name,
        row: rowIndex,
        column: columnIndex,
        status: boxData.status,
        payload: boxData.payload,
        originalPosition: box.position.clone()
      };

      boxRow.push(box);
      scene.add(box);
    });
    boxGrid.push(boxRow);
  });
}

function findBoxInGrid(boxName) {
  for (let row of boxGrid) {
    for (let box of row) {
      if (box.userData.name === boxName) {
        return { box, data: box.userData };
      }
    }
  }
  return null;
}


// ============================================================================
// USER INTERACTION
// ============================================================================
function onBoxClick(event) {
  event.preventDefault();

  const rect = renderer.domElement.getBoundingClientRect();
  mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
  mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

  raycaster.setFromCamera(mouse, camera);

  const intersects = raycaster.intersectObjects(
    boxGrid.flat(),
    false
  );

  if (intersects.length > 0) {
    const selectedBox = intersects[0].object;
    const boxName = selectedBox.userData.name;

    systemState.setSelectedBox(boxName);
    highlightSelectedBox(boxName);
    showToast(`Selected ${boxName}`, "info");
  }
}

function highlightSelectedBox(boxName) {
  boxGrid.forEach(row => {
    row.forEach(box => {
      if (box.userData.name === boxName) {
        box.material.emissive.setHex(0x333333);
      } else {
        box.material.emissive.setHex(0x000000);
      }
    });
  });
}


// ============================================================================
// ANIMATION LOGIC
// ============================================================================
function animate() {
  animationFrameId = requestAnimationFrame(animate);

  const delta = clock.getDelta();

  if (craneMixer) craneMixer.update(delta);
  if (beltMixer) beltMixer.update(delta);

  if (currentOperation) {
    animationProgress += delta / ANIMATION_DURATION;
    updateOperationAnimation();
  } else if (operationQueue.length > 0) {
    startNextOperation();
  }

  renderer.render(scene, camera);
}

function startNextOperation() {
  if (operationQueue.length === 0 || currentOperation) return;

  currentOperation = operationQueue.shift();
  animationProgress = 0;

  if (currentOperation.type === "retrieve") {
    systemState.logOperation("retrieve", currentOperation.boxName, "in-progress");
  } else if (currentOperation.type === "insert") {
    systemState.logOperation("insert", currentOperation.boxName, "in-progress");
  }

  showToast(`Starting ${currentOperation.type} operation for ${currentOperation.boxName}`, "info");
}

function updateOperationAnimation() {
  if (!currentOperation) return;

  switch (currentOperation.type) {
    case "retrieve":
      updateRetrieveAnimation();
      break;
    case "insert":
      updateInsertAnimation();
      break;
    default:
      console.warn("Unknown operation type:", currentOperation.type);
      finishCurrentOperation(false);
      break;
  }
}

function updateRetrieveAnimation() {
  const { boxName } = currentOperation;
  const boxData = findBoxInGrid(boxName);
  if (!boxData) {
    console.error("Box not found for retrieval:", boxName);
    finishCurrentOperation(false);
    return;
  }

  const { box } = boxData;
  const shelfPosition = box.userData.originalPosition;

  if (animationProgress < 0.25) {
    const t = animationProgress / 0.25;
    crane.position.lerpVectors(
      crane.position,
      new THREE.Vector3(shelfPosition.x, POSITIONS.CRANE_ABOVE_SHELVES_Y, shelfPosition.z),
      t
    );
  } else if (animationProgress < 0.5) {
    const t = (animationProgress - 0.25) / 0.25;
    crane.position.lerpVectors(
      crane.position,
      new THREE.Vector3(shelfPosition.x, shelfPosition.y + BOX_HEIGHT / 2 + 10, shelfPosition.z),
      t
    );
    box.position.lerpVectors(
      box.position,
      new THREE.Vector3(
        shelfPosition.x,
        POSITIONS.CRANE_ABOVE_SHELVES_Y,
        shelfPosition.z
      ),
      t
    );
  } else if (animationProgress < 0.75) {
    const t = (animationProgress - 0.5) / 0.25;
    crane.position.lerpVectors(
      crane.position,
      new THREE.Vector3(POSITIONS.BELT_POSITION.x, POSITIONS.CRANE_ABOVE_SHELVES_Y, POSITIONS.BELT_POSITION.z),
      t
    );
    box.position.lerpVectors(
      box.position,
      new THREE.Vector3(
        POSITIONS.BELT_POSITION.x,
        POSITIONS.BELT_POSITION.y + BOX_HEIGHT / 2,
        POSITIONS.BELT_POSITION.z
      ),
      t
    );
  } else {
    const t = (animationProgress - 0.75) / 0.25;
    box.position.lerpVectors(
      box.position,
      new THREE.Vector3(
        POSITIONS.EXIT_POSITION.x,
        POSITIONS.EXIT_POSITION.y + BOX_HEIGHT / 2,
        POSITIONS.EXIT_POSITION.z
      ),
      t
    );
  }

  if (animationProgress >= 1) {
    finishCurrentOperation(true);
  }
}

function updateInsertAnimation() {
  const { boxName } = currentOperation;
  const boxData = findBoxInGrid(boxName);
  if (!boxData) {
    console.error("Box not found for insertion:", boxName);
    finishCurrentOperation(false);
    return;
  }

  const { box } = boxData;
  const shelfPosition = box.userData.originalPosition;

  if (animationProgress < 0.25) {
    const t = animationProgress / 0.25;
    box.position.lerpVectors(
      box.position,
      new THREE.Vector3(
        POSITIONS.BELT_POSITION.x,
        POSITIONS.BELT_POSITION.y + BOX_HEIGHT / 2,
        POSITIONS.BELT_POSITION.z
      ),
      t
    );
  } else if (animationProgress < 0.5) {
    const t = (animationProgress - 0.25) / 0.25;
    crane.position.lerpVectors(
      crane.position,
      new THREE.Vector3(POSITIONS.BELT_POSITION.x, POSITIONS.CRANE_ABOVE_SHELVES_Y, POSITIONS.BELT_POSITION.z),
      t
    );
    box.position.lerpVectors(
      box.position,
      new THREE.Vector3(
        POSITIONS.BELT_POSITION.x,
        POSITIONS.CRANE_ABOVE_SHELVES_Y,
        POSITIONS.BELT_POSITION.z
      ),
      t
    );
  } else if (animationProgress < 0.75) {
    const t = (animationProgress - 0.5) / 0.25;
    crane.position.lerpVectors(
      crane.position,
      new THREE.Vector3(shelfPosition.x, POSITIONS.CRANE_ABOVE_SHELVES_Y, shelfPosition.z),
      t
    );
    box.position.lerpVectors(
      box.position,
      new THREE.Vector3(
        shelfPosition.x,
        POSITIONS.CRANE_ABOVE_SHELVES_Y,
        shelfPosition.z
      ),
      t
    );
  } else {
    const t = (animationProgress - 0.75) / 0.25;
    crane.position.lerpVectors(
      crane.position,
      new THREE.Vector3(shelfPosition.x, shelfPosition.y + BOX_HEIGHT / 2 + 10, shelfPosition.z),
      t
    );
    box.position.lerpVectors(
      box.position,
      new THREE.Vector3(
        shelfPosition.x,
        shelfPosition.y + BOX_HEIGHT / 2,
        shelfPosition.z
      ),
      t
    );
  }

  if (animationProgress >= 1) {
    finishCurrentOperation(true);
  }
}

function finishCurrentOperation(success) {
  if (!currentOperation) return;

  const { boxName, type } = currentOperation;
  const boxData = findBoxInGrid(boxName);

  if (success && boxData) {
    if (type === "retrieve") {
      boxData.box.userData.status = "Out";
      boxData.box.material.color.setHex(BOX_COLOR_OUT);
      boxData.box.userData.payload = "empty";
      showToast(`${boxName} successfully retrieved.`, "success");
      systemState.updateBoxStatus(boxName, "Out", "empty");
    } else if (type === "insert") {
      boxData.box.userData.status = "In";
      boxData.box.material.color.setHex(BOX_COLOR_IN);
      showToast(`${boxName} successfully inserted.`, "success");
      systemState.updateBoxStatus(boxName, "In", boxData.box.userData.payload);
    }

    updateStatusCounts();
    updateBoxListUI();
  } else {
    showToast(`Operation for ${boxName} failed.`, "error");
  }

  currentOperation = null;
}


// ============================================================================
// OPERATION QUEUE MANAGEMENT
// ============================================================================
function retrieveBoxFromStorage(boxName) {
  const boxData = findBoxInGrid(boxName);
  if (!boxData) {
    showToast(`Box ${boxName} not found on shelves.`, "error");
    throw new Error(`Box ${boxName} not found.`);
  }

  if (boxData.data.status === "Out") {
    showToast(`Box ${boxName} is already out.`, "info");
    throw new Error(`Box ${boxName} is already out.`);
  }

  operationQueue.push({
    type: "retrieve",
    boxName,
    data: boxData.data
  });

  showToast(`Box ${boxName} added to retrieval queue.`, "info");
  updateButtonStates();
}

function insertBoxToStorage(boxName) {
  const boxData = findBoxInGrid(boxName);
  if (!boxData) {
    showToast(`Box ${boxName} not found.`, "error");
    throw new Error(`Box ${boxName} not found.`);
  }

  if (boxData.data.status === "In") {
    showToast(`Box ${boxName} is already in storage.`, "info");
    throw new Error(`Box ${boxName} is already in storage.`);
  }

  operationQueue.push({
    type: "insert",
    boxName,
    data: boxData.data
  });

  showToast(`Box ${boxName} added to insertion queue.`, "info");
  updateButtonStates();
}


// ============================================================================
// UI FUNCTIONS (UPDATED FOR VIEW-ONLY SAFE MODE)
// ============================================================================
function showToast(message, type = 'info') {
  const container = document.getElementById('toastContainer');
  
  // If there is no toast container (view-only mode), just log the message
  if (!container) {
    if (type === 'error') {
      console.error(message);
    } else if (type === 'success') {
      console.log('[SUCCESS]', message);
    } else {
      console.log(message);
    }
    return;
  }

  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = message;
  container.appendChild(toast);

  setTimeout(() => {
    toast.classList.add('removing');
    setTimeout(() => {
      container.removeChild(toast);
    }, 300);
  }, 6000);
}

function updateStatusCounts() {
  let fullCount = 0;
  let partialCount = 0;
  let emptyCount = 0;

  boxGrid.forEach(row => {
    row.forEach(box => {
      if (box.payload === "full") fullCount++;
      else if (box.payload === "partially full") partialCount++;
      else if (box.payload === "empty") emptyCount++;
    });
  });

  const fullEl = document.getElementById('fullCount');
  const partialEl = document.getElementById('partialCount');
  const emptyEl = document.getElementById('emptyCount');

  // In view-only mode, these elements might not exist
  if (!fullEl || !partialEl || !emptyEl) {
    return;
  }

  fullEl.textContent = fullCount;
  partialEl.textContent = partialCount;
  emptyEl.textContent = emptyCount;
}

function updateButtonStates() {
  const getOutBtn = document.getElementById('getBoxOutBtn');
  const putInBtn = document.getElementById('putBoxInBtn');
  const selectedBox = systemState.selectedBox;
  const isOperating = systemState.isOperationInProgress();

  // If buttons don't exist (view-only mode), nothing to update
  if (!getOutBtn || !putInBtn) {
    return;
  }

  if (!selectedBox || isOperating) {
    getOutBtn.disabled = true;
    putInBtn.disabled = true;
  } else {
    const boxData = findBoxInGrid(selectedBox);
    if (boxData) {
      getOutBtn.disabled = boxData.data.status !== "In";
      putInBtn.disabled = boxData.data.status !== "Out";
    }
  }
}

function populateBoxList() {
  const boxList = document.getElementById('boxList');

  // In view-only mode, the list container doesn't exist
  if (!boxList) {
    return;
  }

  boxList.innerHTML = '';

  boxGrid.forEach(row => {
    row.forEach(box => {
      const item = document.createElement('div');
      item.className = 'box-item';
      item.dataset.boxName = box.name;
      
      const nameSpan = document.createElement('span');
      nameSpan.className = 'box-name';
      nameSpan.textContent = box.name;
      
      const statusSpan = document.createElement('span');
      statusSpan.className = `box-status ${box.status.toLowerCase()}`;
      statusSpan.textContent = box.status.toUpperCase();
      
      item.appendChild(nameSpan);
      item.appendChild(statusSpan);
      
      item.addEventListener('click', () => {
        document.querySelectorAll('.box-item').forEach(el => el.classList.remove('selected'));
        item.classList.add('selected');
        systemState.setSelectedBox(box.name);
        updateButtonStates();
      });
      
      boxList.appendChild(item);
    });
  });
}

function updateBoxListUI() {
  boxGrid.forEach(row => {
    row.forEach(box => {
      const item = document.querySelector(`[data-box-name="${box.name}"]`);
      if (item) {
        const statusSpan = item.querySelector('.box-status');
        statusSpan.textContent = box.status.toUpperCase();
        statusSpan.className = `box-status ${box.status.toLowerCase()}`;
      }
    });
  });
}


// ============================================================================
// EVENT LISTENERS (SAFE IF BUTTONS ARE MISSING)
// ============================================================================
const getBoxOutBtn = document.getElementById('getBoxOutBtn');
if (getBoxOutBtn) {
  getBoxOutBtn.addEventListener('click', () => {
    const selectedBox = systemState.selectedBox;
    if (selectedBox) {
      retrieveBoxFromStorage(selectedBox).catch(err => console.error('Retrieval failed:', err));
    }
  });
}

const putBoxInBtn = document.getElementById('putBoxInBtn');
if (putBoxInBtn) {
  putBoxInBtn.addEventListener('click', () => {
    const selectedBox = systemState.selectedBox;
    if (selectedBox) {
      insertBoxToStorage(selectedBox).catch(err => console.error('Insertion failed:', err));
    }
  });
}

window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});


// ============================================================================
// INITIALIZE APPLICATION
// ============================================================================
initScene();
loadModel();
animate();

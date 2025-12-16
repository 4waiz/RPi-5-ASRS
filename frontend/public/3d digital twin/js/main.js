import * as THREE from "../libs/three.module.js";
import { GLTFLoader } from "../libs/GLTFLoader.js";
import { OrbitControls } from "../libs/OrbitControls.js";

// ============================================================================
// CONFIGURATION CONSTANTS
// ============================================================================
const CONFIG = {
  CRANE_SPEED: 50,
  STORAGE_X: 91.6,
  INTERMEDIATE_X: 141.5,
  FINAL_OUT_X: 206,
  POST_OUT_X: 260,
  ENTRY_GATE_Z: -15,
  EXIT_GATE_Z: 137,
  GATE_Y: 75.0,
  BASE_Y: 50.1,
  GATE_Y_BASE: 17.1,
  ROW_SPACING: 20,
  COL_SPACING: 40,
  BASE_Z: 44.6,
  ENTRY_GATE_Z_OFFSET: 28.3,
  EXIT_GATE_Z_OFFSET: 181.3,
  GLOW_DURATION_MS: 2000,
  GLOW_INTENSITY: 2.0,
  CRANE_NAMES: {
    decorative: ['crane', 'Crane', 'CRANE'],
    controllable: ['crane.002', 'crane002', 'Crane.002', 'Crane002', 'crane_002']
  }
};

// ============================================================================
// BOX DATA - 6x4 Grid (24 boxes)
// ============================================================================
const boxGrid = [
  [
    { name: "box_1", status: "Out", payload: "full" },
    { name: "box_2", status: "Out", payload: "empty" },
    { name: "box_3", status: "In", payload: "partially full" },
    { name: "box_4", status: "Out", payload: "full" }
  ],
  [
    { name: "box_5", status: "In", payload: "empty" },
    { name: "box_6", status: "In", payload: "full" },
    { name: "box_7", status: "In", payload: "full" },
    { name: "box_8", status: "In", payload: "partially full" }
  ],
  [
    { name: "box_9", status: "In", payload: "empty" },
    { name: "box_10", status: "In", payload: "full" },
    { name: "box_11", status: "In", payload: "full" },
    { name: "box_12", status: "In", payload: "empty" }
  ],
  [
    { name: "box_13", status: "In", payload: "empty" },
    { name: "box_14", status: "In", payload: "partially full" },
    { name: "box_15", status: "In", payload: "full" },
    { name: "box_16", status: "In", payload: "full" }
  ],
  [
    { name: "box_17", status: "In", payload: "partially full" },
    { name: "box_18", status: "In", payload: "empty" },
    { name: "box_19", status: "In", payload: "full" },
    { name: "box_20", status: "In", payload: "empty" }
  ],
  [
    { name: "box_21", status: "In", payload: "partially full" },
    { name: "box_22", status: "In", payload: "full" },
    { name: "box_23", status: "In", payload: "empty" },
    { name: "box_24", status: "In", payload: "full" }
  ]
];

// ============================================================================
// SYSTEM STATE
// ============================================================================
class SystemState {
  constructor() {
    this._ready = false;
    this._currentOperation = null;
    this._selectedBox = null;
  }

  get ready() {
    return this._ready;
  }

  setReady(value) {
    this._ready = value;
  }

  get currentOperation() {
    return this._currentOperation;
  }

  setOperation(boxName) {
    this._currentOperation = boxName;
  }

  clearOperation() {
    this._currentOperation = null;
  }

  isOperationInProgress() {
    return this._currentOperation !== null;
  }

  get selectedBox() {
    return this._selectedBox;
  }

  setSelectedBox(boxName) {
    this._selectedBox = boxName;
  }
}

const systemState = new SystemState();

// Map RFID tags to box targets (action decided based on current status)
const RFID_TAG_TO_BOX = {
  "0000000002": "box_2"
};

function getSseUrl() {
  const host = window.location.hostname || "localhost";
  return `http://${host}:8765/events`;
}

// ============================================================================
// SCENE OBJECTS
// ============================================================================
let scene, camera, renderer, controls, clock;
let decorativeCrane, controllableCrane, sceneRoot;

// ============================================================================
// MOVEMENT SYSTEM
// ============================================================================
class MovementController {
  constructor() {
    this.activeMovements = new Map();
  }

  moveObject(object, targetPos, speed = CONFIG.CRANE_SPEED) {
    if (!object.name) {
      throw new Error('Object must have a name property for movement tracking');
    }

    return new Promise((resolve) => {
      const movementData = {
        object,
        target: new THREE.Vector3(targetPos.x, targetPos.y, targetPos.z),
        speed,
        onComplete: resolve
      };
      this.activeMovements.set(object.name, movementData);
    });
  }

  update(delta) {
    this.activeMovements.forEach((movement, objectName) => {
      const { object, target, speed, onComplete } = movement;

      const direction = new THREE.Vector3().subVectors(target, object.position);
      const distanceToTarget = direction.length();

      if (distanceToTarget === 0) {
        this.activeMovements.delete(objectName);
        onComplete();
        return;
      }

      direction.normalize();

      const stepDistance = speed * delta;
      if (stepDistance >= distanceToTarget) {
        object.position.copy(target);
        this.activeMovements.delete(objectName);
        onComplete();
      } else {
        object.position.add(direction.multiplyScalar(stepDistance));
      }
    });
  }

  stopAll() {
    this.activeMovements.forEach(movement => {
      if (movement.onComplete) {
        movement.onComplete();
      }
    });
    this.activeMovements.clear();
  }
}

const movementController = new MovementController();

// ============================================================================
// VISUAL HELPERS
// ============================================================================
function forEachMaterial(object, callback) {
  object.traverse((child) => {
    if (child.isMesh && child.material) {
      const materials = Array.isArray(child.material) ? child.material : [child.material];
      materials.forEach((mat) => mat && callback(mat));
    }
  });
}

function setMeshColor(object, hexColor) {
  forEachMaterial(object, (mat) => {
    if (mat.color) mat.color.setHex(hexColor);
  });
}

function setMeshOpacity(object, opacity) {
  forEachMaterial(object, (mat) => {
    mat.transparent = true;
    mat.opacity = opacity;
    mat.depthWrite = opacity >= 1.0;
    mat.needsUpdate = true;
  });
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function fadeOpacity(object, toOpacity, durationMs) {
  return new Promise((resolve) => {
    let startTime = null;
    let startOpacity = 1.0;
    let captured = false;

    forEachMaterial(object, (mat) => {
      if (!captured) {
        startOpacity = (typeof mat.opacity === "number") ? mat.opacity : 1.0;
        captured = true;
      }
      mat.transparent = true;
    });

    function animate(timestamp) {
      if (!startTime) startTime = timestamp;
      const progress = Math.min(1, (timestamp - startTime) / durationMs);
      const currentOpacity = startOpacity + (toOpacity - startOpacity) * progress;
      setMeshOpacity(object, currentOpacity);

      if (progress < 1) {
        requestAnimationFrame(animate);
      } else {
        resolve();
      }
    }
    requestAnimationFrame(animate);
  });
}

async function glowEmissiveTemporarily(object, durationMs, intensity = CONFIG.GLOW_INTENSITY) {
  const originalStates = [];

  forEachMaterial(object, (mat) => {
    if (mat.emissive) {
      originalStates.push({
        material: mat,
        color: mat.emissive.clone(),
        intensity: (typeof mat.emissiveIntensity === 'number') ? mat.emissiveIntensity : 1
      });
      mat.emissiveIntensity = intensity;
      mat.needsUpdate = true;
    }
  });

  await sleep(durationMs);

  originalStates.forEach(({ material, color, intensity }) => {
    material.emissive.copy(color);
    material.emissiveIntensity = intensity;
    material.needsUpdate = true;
  });
}

// ============================================================================
// BOX DATA HELPERS
// ============================================================================
function findBoxInGrid(boxName) {
  for (let row = 0; row < boxGrid.length; row++) {
    for (let col = 0; col < boxGrid[row].length; col++) {
      if (boxGrid[row][col].name === boxName) {
        return { data: boxGrid[row][col], row, col };
      }
    }
  }
  return null;
}

function getPayloadColor(payload) {
  const colors = {
    "full": 0x00ff00,
    "partially full": 0xC0C0C0,
    "empty": 0xff0000
  };
  return colors[payload] || 0xffffff;
}

// ============================================================================
// POSITION CALCULATORS
// ============================================================================
function calculateCraneStoragePosition(row, col) {
  return {
    x: CONFIG.STORAGE_X,
    y: 9.2 + (19.8 * (5 - row)),
    z: 119.6 - (CONFIG.COL_SPACING * (3 - col))
  };
}

function calculateBoxCellPosition() {
  return { 
    x: CONFIG.STORAGE_X, 
    y: CONFIG.BASE_Y, 
    z: CONFIG.BASE_Z 
  };
}

function calculateBoxDeliveryPosition(row, col) {
  return {
    x: CONFIG.POST_OUT_X,
    y: CONFIG.GATE_Y_BASE + (CONFIG.ROW_SPACING * row),
    z: CONFIG.BASE_Z + (CONFIG.ENTRY_GATE_Z_OFFSET - CONFIG.BASE_Z) + (-CONFIG.COL_SPACING * col)
  };
}

function calculateRoutingY(row) {
  return CONFIG.GATE_Y_BASE + (CONFIG.ROW_SPACING * row);
}

function calculateRoutingZ(col, gateZOffset) {
  return CONFIG.BASE_Z + (gateZOffset - CONFIG.BASE_Z) + (-CONFIG.COL_SPACING * col);
}

function calculateExitRoutingPosition(row, col) {
  return {
    x: CONFIG.INTERMEDIATE_X,
    y: calculateRoutingY(row),
    z: calculateRoutingZ(col, CONFIG.EXIT_GATE_Z_OFFSET)
  };
}

function calculateEntryRoutingPosition(row, col) {
  return {
    x: CONFIG.INTERMEDIATE_X,
    y: calculateRoutingY(row),
    z: calculateRoutingZ(col, CONFIG.ENTRY_GATE_Z_OFFSET)
  };
}

// ============================================================================
// TRAVEL TIME CALCULATOR
// ============================================================================
function calculateTravelTime(fromPos, toPos) {
  const distance = fromPos.distanceTo(new THREE.Vector3(toPos.x, toPos.y, toPos.z));
  return Math.max(1, (distance / CONFIG.CRANE_SPEED) * 1000);
}

// ============================================================================
// VALIDATION
// ============================================================================
function validateBoxOperation(boxName, expectedStatus) {
  if (!systemState.ready) {
    throw new Error('System not ready');
  }

  if (systemState.isOperationInProgress()) {
    throw new Error(`Operation already in progress: ${systemState.currentOperation}`);
  }

  const boxData = findBoxInGrid(boxName);
  if (!boxData) {
    throw new Error(`Box ${boxName} not found in grid`);
  }

  if (boxData.data.status !== expectedStatus) {
    throw new Error(`Box ${boxName} has invalid status: ${boxData.data.status} (expected: ${expectedStatus})`);
  }

  const boxMesh = sceneRoot.getObjectByName(boxName);
  if (!boxMesh) {
    throw new Error(`Box mesh ${boxName} not found in scene`);
  }

  return { boxData, boxMesh };
}

// ============================================================================
// CRANE CONTROL FUNCTIONS
// ============================================================================
async function moveCraneToStorageCell(boxName) {
  const boxData = findBoxInGrid(boxName);
  if (!boxData) {
    throw new Error(`Box ${boxName} not found`);
  }
  const targetPos = calculateCraneStoragePosition(boxData.row, boxData.col);
  await movementController.moveObject(controllableCrane, targetPos);
}

async function moveCraneToExitGate() {
  const targetPos = { 
    x: controllableCrane.position.x, 
    y: CONFIG.GATE_Y, 
    z: CONFIG.EXIT_GATE_Z 
  };
  await movementController.moveObject(controllableCrane, targetPos);
}

async function moveCraneToEntryGate() {
  const targetPos = { 
    x: controllableCrane.position.x, 
    y: CONFIG.GATE_Y, 
    z: CONFIG.ENTRY_GATE_Z 
  };
  await movementController.moveObject(controllableCrane, targetPos);
}

// ============================================================================
// UI FUNCTIONS
// ============================================================================
function showToast(message, type = 'info') {
  const container = document.getElementById('toastContainer');
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

  document.getElementById('fullCount').textContent = fullCount;
  document.getElementById('partialCount').textContent = partialCount;
  document.getElementById('emptyCount').textContent = emptyCount;
}

function selectBoxInUI(boxName) {
  const item = document.querySelector(`[data-box-name="${boxName}"]`);
  if (!item) return;

  document.querySelectorAll('.box-item').forEach(el => el.classList.remove('selected'));
  item.classList.add('selected');
  systemState.setSelectedBox(boxName);
  updateButtonStates();
}

function updateButtonStates() {
  const getOutBtn = document.getElementById('getBoxOutBtn');
  const putInBtn = document.getElementById('putBoxInBtn');
  const selectedBox = systemState.selectedBox;
  const isOperating = systemState.isOperationInProgress();

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
// BOX RETRIEVAL
// ============================================================================
async function retrieveBoxFromStorage(boxName) {
  const { boxData, boxMesh } = validateBoxOperation(boxName, "In");
  systemState.setOperation(boxName);
  updateButtonStates();

  const routingPos = calculateExitRoutingPosition(boxData.row, boxData.col);

  showToast(`Box ${boxName} get out in progress…`, 'info');

  try {
    await moveCraneToStorageCell(boxName);

    await movementController.moveObject(boxMesh, {
      x: CONFIG.INTERMEDIATE_X,
      y: boxMesh.position.y,
      z: boxMesh.position.z
    });

    await Promise.all([
      movementController.moveObject(boxMesh, {
        x: CONFIG.INTERMEDIATE_X,
        y: routingPos.y,
        z: routingPos.z
      }),
      moveCraneToExitGate()
    ]);

    await movementController.moveObject(boxMesh, {
      x: CONFIG.FINAL_OUT_X,
      y: routingPos.y,
      z: routingPos.z
    });

    await glowEmissiveTemporarily(boxMesh, CONFIG.GLOW_DURATION_MS);

    const deliveryPos = { x: CONFIG.POST_OUT_X, y: routingPos.y, z: routingPos.z };
    const travelTime = calculateTravelTime(boxMesh.position, deliveryPos);

    await Promise.all([
      movementController.moveObject(boxMesh, deliveryPos),
      fadeOpacity(boxMesh, 0.0, travelTime)
    ]);

    boxData.data.status = "Out";
    systemState.clearOperation();
    
    showToast(`Box ${boxName} got out completed.`, 'success');
    updateStatusCounts();
    updateBoxListUI();
    updateButtonStates();

  } catch (error) {
    systemState.clearOperation();
    updateButtonStates();
    throw error;
  }
}

async function insertBoxToStorage(boxName) {
  const { boxData, boxMesh } = validateBoxOperation(boxName, "Out");
  systemState.setOperation(boxName);
  updateButtonStates();

  const storagePos = calculateBoxCellPosition();
  const routingPos = calculateEntryRoutingPosition(boxData.row, boxData.col);
  const cranePos = calculateCraneStoragePosition(boxData.row, boxData.col);

  showToast(`Box ${boxName} put in in progress…`, 'info');

  try {
    boxMesh.position.set(CONFIG.POST_OUT_X, routingPos.y, routingPos.z);
    const prestagePos = { x: CONFIG.FINAL_OUT_X, y: routingPos.y, z: routingPos.z };
    const prestageTime = calculateTravelTime(boxMesh.position, prestagePos);

    await Promise.all([
      movementController.moveObject(boxMesh, prestagePos),
      fadeOpacity(boxMesh, 1.0, prestageTime)
    ]);

    await moveCraneToEntryGate();

    await movementController.moveObject(boxMesh, {
      x: CONFIG.INTERMEDIATE_X,
      y: routingPos.y,
      z: routingPos.z
    });

    await Promise.all([
      movementController.moveObject(boxMesh, {
        x: CONFIG.INTERMEDIATE_X,
        y: storagePos.y,
        z: storagePos.z
      }),
      movementController.moveObject(controllableCrane, cranePos)
    ]);

    await movementController.moveObject(boxMesh, {
      x: CONFIG.STORAGE_X,
      y: storagePos.y,
      z: storagePos.z
    });

    await glowEmissiveTemporarily(boxMesh, CONFIG.GLOW_DURATION_MS);

    boxData.data.status = "In";
    systemState.clearOperation();
    
    showToast(`Box ${boxName} put in completed.`, 'success');
    updateStatusCounts();
    updateBoxListUI();
    updateButtonStates();

  } catch (error) {
    systemState.clearOperation();
    updateButtonStates();
    throw error;
  }
}

// ============================================================================
// OBJECT LOOKUP HELPER
// ============================================================================
function findObjectByNames(parent, nameList) {
  for (const name of nameList) {
    const obj = parent.getObjectByName(name);
    if (obj) return obj;
  }
  return null;
}

// ============================================================================
// THREE.JS SCENE INITIALIZATION
// ============================================================================
function initScene() {
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0xEBEBEB);

  camera = new THREE.PerspectiveCamera(
    75,
    window.innerWidth / window.innerHeight,
    0.1,
    1000
  );
  camera.position.set(250, 100, 200);
  camera.lookAt(100, 60, 80);

  renderer = new THREE.WebGLRenderer({
    alpha: true,
    antialias: false,
    powerPreference: "high-performance"
  });
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(1);
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.BasicShadowMap;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.2;
  document.getElementById("container3D").appendChild(renderer.domElement);

  const hemisphereLight = new THREE.HemisphereLight(0xffffff, 0x444444, 0.4);
  hemisphereLight.position.set(0, 200, 0);
  scene.add(hemisphereLight);

  const mainLight = new THREE.DirectionalLight(0xffffff, 1.0);
  mainLight.position.set(200, 300, 150);
  mainLight.castShadow = true;
  mainLight.shadow.camera.left = -300;
  mainLight.shadow.camera.right = 300;
  mainLight.shadow.camera.top = 300;
  mainLight.shadow.camera.bottom = -300;
  mainLight.shadow.camera.near = 0.5;
  mainLight.shadow.camera.far = 1000;
  mainLight.shadow.mapSize.width = 1024;
  mainLight.shadow.mapSize.height = 1024;
  mainLight.shadow.bias = -0.0005;
  scene.add(mainLight);

  const fillLight = new THREE.DirectionalLight(0xffffff, 0.3);
  fillLight.position.set(-150, 150, -100);
  scene.add(fillLight);

  const ambientLight = new THREE.AmbientLight(0xffffff, 0.4);
  scene.add(ambientLight);

  controls = new OrbitControls(camera, renderer.domElement);
  controls.target.set(100, 60, 80);
  controls.enableDamping = true;
  controls.dampingFactor = 0.05;
  controls.screenSpacePanning = true;
  controls.minDistance = 150;
  controls.maxDistance = 600;
  controls.maxPolarAngle = Math.PI / 2;
  controls.update();

  clock = new THREE.Clock();

  // Setup gizmo (orientation helper)
  setupGizmo();
}

// ============================================================================
// GIZMO SETUP
// ============================================================================
function setupGizmo() {
  // Create gizmo container
  const gizmoContainer = document.createElement('div');
  gizmoContainer.style.position = 'absolute';
  gizmoContainer.style.top = '20px';
  gizmoContainer.style.right = '20px';
  gizmoContainer.style.display = 'flex';
  gizmoContainer.style.flexDirection = 'column';
  gizmoContainer.style.gap = '10px';
  gizmoContainer.style.zIndex = '1000';
  gizmoContainer.style.padding = '12px';
  gizmoContainer.style.background = 'rgba(255, 255, 255, 0.12)';
  gizmoContainer.style.borderRadius = '16px';
  gizmoContainer.style.backdropFilter = 'blur(12px)';
  gizmoContainer.style.border = '1px solid rgba(255, 255, 255, 0.2)';
  gizmoContainer.style.boxShadow = '0 8px 32px rgba(0, 0, 0, 0.1)';
  document.getElementById("container3D").appendChild(gizmoContainer);

  // Title
  const title = document.createElement('div');
  title.textContent = 'VIEW';
  title.style.fontSize = '10px';
  title.style.fontWeight = '700';
  title.style.color = 'rgba(0, 0, 0, 0.6)';
  title.style.textAlign = 'center';
  title.style.letterSpacing = '1px';
  title.style.marginBottom = '4px';
  gizmoContainer.appendChild(title);

  // Button styles
  const buttonStyle = {
    width: '56px',
    height: '56px',
    borderRadius: '12px',
    border: 'none',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    cursor: 'pointer',
    fontWeight: '600',
    fontSize: '11px',
    transition: 'all 0.25s cubic-bezier(0.4, 0, 0.2, 1)',
    userSelect: 'none',
    boxShadow: '0 2px 8px rgba(0, 0, 0, 0.15)',
    outline: 'none',
    position: 'relative',
    overflow: 'hidden'
  };

  // Create view buttons
  const views = [
    { label: 'TOP', position: [100, 300, 80], color: '#4CAF50', hoverColor: '#66BB6A' },
    { label: 'FRONT', position: [300, 60, 80], color: '#2196F3', hoverColor: '#42A5F5' },
    { label: 'RIGHT', position: [100, 60, 300], color: '#F44336', hoverColor: '#EF5350' },
    { label: 'BACK', position: [100, 60, -150], color: '#9C27B0', hoverColor: '#AB47BC' }
  ];

  views.forEach(view => {
    const button = document.createElement('button');
    button.textContent = view.label;
    Object.assign(button.style, buttonStyle);
    button.style.backgroundColor = view.color;
    button.style.color = 'white';

    // Add ripple effect background
    const ripple = document.createElement('div');
    ripple.style.position = 'absolute';
    ripple.style.top = '0';
    ripple.style.left = '0';
    ripple.style.width = '100%';
    ripple.style.height = '100%';
    ripple.style.background = 'rgba(255, 255, 255, 0)';
    ripple.style.transition = 'background 0.3s';
    button.appendChild(ripple);

    const label = document.createElement('span');
    label.textContent = view.label;
    label.style.position = 'relative';
    label.style.zIndex = '1';
    button.appendChild(label);
    button.textContent = '';
    button.appendChild(ripple);
    button.appendChild(label);

    button.addEventListener('mouseenter', () => {
      button.style.transform = 'translateY(-2px) scale(1.05)';
      button.style.boxShadow = '0 6px 16px rgba(0, 0, 0, 0.25)';
      button.style.backgroundColor = view.hoverColor;
      ripple.style.background = 'rgba(255, 255, 255, 0.1)';
    });

    button.addEventListener('mouseleave', () => {
      button.style.transform = 'translateY(0) scale(1)';
      button.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.15)';
      button.style.backgroundColor = view.color;
      ripple.style.background = 'rgba(255, 255, 255, 0)';
    });

    button.addEventListener('mousedown', () => {
      button.style.transform = 'translateY(0) scale(0.98)';
    });

    button.addEventListener('mouseup', () => {
      button.style.transform = 'translateY(-2px) scale(1.05)';
    });

    button.addEventListener('click', () => {
      camera.position.set(...view.position);
      camera.lookAt(100, 60, 80);
      controls.target.set(100, 60, 80);
      controls.update();

      // Visual feedback
      ripple.style.background = 'rgba(255, 255, 255, 0.3)';
      setTimeout(() => {
        ripple.style.background = 'rgba(255, 255, 255, 0)';
      }, 300);
    });

    gizmoContainer.appendChild(button);
  });
}

// ============================================================================
// MODEL LOADING
// ============================================================================
function loadModel() {
  const loader = new GLTFLoader();

  loader.load(
    "./models/Box/full2.glb",
    function (gltf) {
      sceneRoot = gltf.scene;

      sceneRoot.traverse(child => {
        if (child.isMesh) {
          child.receiveShadow = true;

          // Only cast shadows for boxes and cranes (important objects)
          const parentName = child.parent?.name || '';
          if (parentName.toLowerCase().includes('box') ||
              parentName.toLowerCase().includes('crane')) {
            child.castShadow = true;
          } else {
            child.castShadow = false;
          }
        }
      });

      decorativeCrane = findObjectByNames(sceneRoot, CONFIG.CRANE_NAMES.decorative);
      controllableCrane = findObjectByNames(sceneRoot, CONFIG.CRANE_NAMES.controllable);

      if (!controllableCrane) {
        console.warn('Warning: Controllable crane not found in model');
      }

      boxGrid.forEach((row, rowIndex) => {
        row.forEach((boxData, colIndex) => {
          const boxMesh = sceneRoot.getObjectByName(boxData.name);

          if (boxMesh) {
            const color = getPayloadColor(boxData.payload);
            boxMesh.traverse((child) => {
              if (child.isMesh) {
                child.material = new THREE.MeshStandardMaterial({ color });
              }
            });

            const initialPos = (boxData.status === "In")
              ? calculateBoxCellPosition()
              : calculateBoxDeliveryPosition(rowIndex, colIndex);

            boxMesh.position.set(initialPos.x, initialPos.y, initialPos.z);
            setMeshOpacity(boxMesh, boxData.status === "In" ? 1.0 : 0.0);
          }
        });
      });

      scene.add(sceneRoot);
      systemState.setReady(true);
      
      populateBoxList();
      updateStatusCounts();
      updateButtonStates();
    },
    undefined,
    (error) => {
      console.error("Model load error:", error);
    }
  );
}

// ============================================================================
// ANIMATION LOOP
// ============================================================================
let lastFrameTime = 0;
const targetFPS = 30;
const frameInterval = 1000 / targetFPS;

function animate(currentTime) {
  requestAnimationFrame(animate);

  const elapsed = currentTime - lastFrameTime;

  // Limit to target FPS
  if (elapsed < frameInterval) {
    return;
  }

  lastFrameTime = currentTime - (elapsed % frameInterval);
  const delta = clock.getDelta();

  if (decorativeCrane && controllableCrane) {
    decorativeCrane.position.z = controllableCrane.position.z;
  }

  movementController.update(delta);

  controls.update();
  renderer.render(scene, camera);
}

// ============================================================================
// RFID / ROS BRIDGE LISTENER (SSE)
// ============================================================================
async function handleTwinAction(payload) {
  if (!payload || !systemState.ready || systemState.isOperationInProgress()) {
    return;
  }

  const { action, box } = payload;
  if (!action || !box) return;

  selectBoxInUI(box);
  if (payload.tag) {
    showToast(`RFID ${payload.tag} requested ${action} for ${box}`, 'info');
  }

  try {
    if (action === 'get_out') {
      await retrieveBoxFromStorage(box);
    } else if (action === 'put_in') {
      await insertBoxToStorage(box);
    }
  } catch (err) {
    console.error('RFID-triggered action failed:', err);
    showToast(`Action failed for ${box}`, 'info');
  }
}

function setupSseListener() {
  const url = getSseUrl();
  let source;

  try {
    source = new EventSource(url);
  } catch (err) {
    console.error('Unable to start SSE listener:', err);
    return;
  }

  source.onopen = () => console.log(`Connected to ROS twin bridge at ${url}`);
  source.onerror = () => {
    console.warn('SSE connection lost (will retry automatically)...');
  };

  source.onmessage = (event) => {
    if (!event.data) return;

    let payload;
    try {
      payload = JSON.parse(event.data);
    } catch (err) {
      return;
    }

    if (payload.type === 'action' && payload.box) {
      handleTwinAction(payload);
    } else if (payload.type === 'rfid' && payload.tag && RFID_TAG_TO_BOX[payload.tag]) {
      const boxName = RFID_TAG_TO_BOX[payload.tag];
      const boxData = findBoxInGrid(boxName);
      if (!boxData) return;

      // Toggle: if box is Out -> put it in; if In -> get it out
      const action = boxData.data.status === "Out" ? "put_in" : "get_out";
      handleTwinAction({ action, box: boxName, tag: payload.tag });
    }
  };
}

// ============================================================================
// EVENT LISTENERS
// ============================================================================
document.getElementById('getBoxOutBtn').addEventListener('click', () => {
  const selectedBox = systemState.selectedBox;
  if (selectedBox) {
    retrieveBoxFromStorage(selectedBox).catch(err => console.error('Retrieval failed:', err));
  }
});

document.getElementById('putBoxInBtn').addEventListener('click', () => {
  const selectedBox = systemState.selectedBox;
  if (selectedBox) {
    insertBoxToStorage(selectedBox).catch(err => console.error('Insertion failed:', err));
  }
});

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
setupSseListener();

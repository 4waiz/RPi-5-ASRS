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

// ============================================================================
// BOX INSERTION
// ============================================================================
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
  camera.position.set(0, 100, 500);

  renderer = new THREE.WebGLRenderer({
    alpha: true,
    antialias: true,
    powerPreference: "high-performance"
  });
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.2;
  document.getElementById("container3D").appendChild(renderer.domElement);

  const hemisphereLight = new THREE.HemisphereLight(0xffffff, 0x444444, 0.4);
  hemisphereLight.position.set(0, 200, 0);
  scene.add(hemisphereLight);

  const mainLight = new THREE.DirectionalLight(0xffffff, 0.8);
  mainLight.position.set(200, 300, 150);
  mainLight.castShadow = true;
  mainLight.shadow.camera.left = -300;
  mainLight.shadow.camera.right = 300;
  mainLight.shadow.camera.top = 300;
  mainLight.shadow.camera.bottom = -300;
  mainLight.shadow.camera.near = 0.5;
  mainLight.shadow.camera.far = 1000;
  mainLight.shadow.mapSize.width = 4096;
  mainLight.shadow.mapSize.height = 4096;
  mainLight.shadow.bias = -0.0005;
  mainLight.shadow.radius = 2;
  scene.add(mainLight);

  const fillLight = new THREE.DirectionalLight(0xffffff, 0.3);
  fillLight.position.set(-150, 150, -100);
  scene.add(fillLight);

  const rimLight = new THREE.DirectionalLight(0xadd8e6, 0.25);
  rimLight.position.set(-100, 100, -200);
  scene.add(rimLight);

  const ambientLight = new THREE.AmbientLight(0xffffff, 0.15);
  scene.add(ambientLight);

  const craneLight1 = new THREE.PointLight(0xffffff, 0.4, 150);
  craneLight1.position.set(100, 50, 100);
  scene.add(craneLight1);

  const craneLight2 = new THREE.PointLight(0xffffff, 0.3, 150);
  craneLight2.position.set(100, 50, -100);
  scene.add(craneLight2);

  controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.05;
  controls.screenSpacePanning = true;
  controls.minDistance = 1;
  controls.maxDistance = 1000;
  controls.maxPolarAngle = Math.PI;

  clock = new THREE.Clock();
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
          child.castShadow = true;
          child.receiveShadow = true;
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
function animate() {
  requestAnimationFrame(animate);

  const delta = clock.getDelta();

  if (decorativeCrane && controllableCrane) {
    decorativeCrane.position.z = controllableCrane.position.z;
  }

  movementController.update(delta);

  controls.update();
  renderer.render(scene, camera);
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

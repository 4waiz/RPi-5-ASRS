<script lang="ts">
  import { onMount } from 'svelte';
  import * as THREE from 'three';
  import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
  import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';

  // ---------- DOM refs (Svelte 5-friendly, no document.getElementById) ----------
  let container3DEl: HTMLDivElement;
  let boxListEl: HTMLDivElement;
  let getBoxOutBtnEl: HTMLButtonElement;
  let putBoxInBtnEl: HTMLButtonElement;
  let fullCountEl: HTMLDivElement;
  let partialCountEl: HTMLDivElement;
  let emptyCountEl: HTMLDivElement;
  let toastContainerEl: HTMLDivElement;

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
    },
    BOX_MODEL_URL: '/Static/Models/Box/full2.glb'
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
    _ready = false;
    _currentOperation: string | null = null;
    _selectedBox: string | null = null;
    _hideUI = $state(false);

    get ready() {
      return this._ready;
    }
    setReady(value: boolean) {
      this._ready = value;
    }

    get currentOperation() {
      return this._currentOperation;
    }
    setOperation(boxName: string) {
      this._currentOperation = boxName;
      this._hideUI = true;
    }
    clearOperation() {
      this._currentOperation = null;
      this._hideUI = false;
    }
    isOperationInProgress() {
      return this._currentOperation !== null;
    }

    get selectedBox() {
      return this._selectedBox;
    }
    setSelectedBox(boxName: string | null) {
      this._selectedBox = boxName;
    }

    get hideUI() {
      return this._hideUI;
    }
  }

  const systemState = new SystemState();

  // ============================================================================
  // SCENE OBJECTS
  // ============================================================================
  let scene: THREE.Scene;
  let camera: THREE.PerspectiveCamera;
  let renderer: THREE.WebGLRenderer;
  let controls: OrbitControls;
  let clock: THREE.Clock;
  let decorativeCrane: THREE.Object3D | null = null;
  let controllableCrane: THREE.Object3D | null = null;
  let sceneRoot: THREE.Object3D;

  // ============================================================================
  // MOVEMENT SYSTEM
  // ============================================================================
  type MovementData = {
    object: THREE.Object3D;
    target: THREE.Vector3;
    speed: number;
    onComplete: () => void;
  };

  class MovementController {
    activeMovements = new Map<string, MovementData>();

    moveObject(
      object: THREE.Object3D & { name: string },
      targetPos: { x: number; y: number; z: number },
      speed = CONFIG.CRANE_SPEED
    ) {
      if (!object.name) {
        throw new Error('Object must have a name property for movement tracking');
      }

      return new Promise<void>((resolve) => {
        const movementData: MovementData = {
          object,
          target: new THREE.Vector3(targetPos.x, targetPos.y, targetPos.z),
          speed,
          onComplete: resolve
        };
        this.activeMovements.set(object.name, movementData);
      });
    }

    update(delta: number) {
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
        if (movement.onComplete) movement.onComplete();
      });
      this.activeMovements.clear();
    }
  }

  const movementController = new MovementController();

  // ============================================================================
  // CAMERA ANIMATION SYSTEM
  // ============================================================================
  type CameraAnimationData = {
    startPos: THREE.Vector3;
    targetPos: THREE.Vector3;
    startTime: number;
    duration: number;
    onComplete: () => void;
  };

  class CameraController {
    private activeAnimation: CameraAnimationData | null = null;

    moveCameraToPreset(
      targetPos: { x: number; y: number; z: number },
      duration = 1000
    ) {
      return new Promise<void>((resolve) => {
        this.activeAnimation = {
          startPos: camera.position.clone(),
          targetPos: new THREE.Vector3(targetPos.x, targetPos.y, targetPos.z),
          startTime: performance.now(),
          duration,
          onComplete: resolve
        };

        // Disable user controls during animation
        controls.enabled = false;
      });
    }

    update() {
      if (!this.activeAnimation) return;

      const now = performance.now();
      const elapsed = now - this.activeAnimation.startTime;
      const progress = Math.min(1, elapsed / this.activeAnimation.duration);

      // Easing function (ease-in-out cubic)
      const eased = progress < 0.5
        ? 4 * progress * progress * progress
        : 1 - Math.pow(-2 * progress + 2, 3) / 2;

      // Interpolate position
      camera.position.lerpVectors(
        this.activeAnimation.startPos,
        this.activeAnimation.targetPos,
        eased
      );

      // Always look at the scene center (origin)
      camera.lookAt(CAMERA_LOOK_TARGET);

      if (progress >= 1) {
        const onComplete = this.activeAnimation.onComplete;
        this.activeAnimation = null;
        controls.enabled = true;
        controls.target.copy(CAMERA_LOOK_TARGET);
        onComplete();
      }
    }

    isAnimating() {
      return this.activeAnimation !== null;
    }
  }

  const cameraController = new CameraController();

  // ============================================================================
  // VISUAL HELPERS
  // ============================================================================
  function forEachMaterial(object: THREE.Object3D, callback: (mat: THREE.Material) => void) {
    object.traverse((child: any) => {
      if (child.isMesh && child.material) {
        const materials = Array.isArray(child.material) ? child.material : [child.material];
        materials.forEach((mat) => mat && callback(mat));
      }
    });
  }

  function setMeshColor(object: THREE.Object3D, hexColor: number) {
    forEachMaterial(object, (mat: any) => {
      if (mat.color) mat.color.setHex(hexColor);
    });
  }

  function setMeshOpacity(object: THREE.Object3D, opacity: number) {
    forEachMaterial(object, (mat: any) => {
      mat.transparent = true;
      mat.opacity = opacity;
      mat.depthWrite = opacity >= 1.0;
      mat.needsUpdate = true;
    });
  }

  function sleep(ms: number) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  function fadeOpacity(object: THREE.Object3D, toOpacity: number, durationMs: number) {
    return new Promise<void>((resolve) => {
      let startTime: number | null = null;
      let startOpacity = 1.0;
      let captured = false;

      forEachMaterial(object, (mat: any) => {
        if (!captured) {
          startOpacity = (typeof mat.opacity === "number") ? mat.opacity : 1.0;
          captured = true;
        }
        mat.transparent = true;
      });

      function animate(timestamp: number) {
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

  async function glowEmissiveTemporarily(
    object: THREE.Object3D,
    durationMs = CONFIG.GLOW_DURATION_MS,
    intensity = CONFIG.GLOW_INTENSITY
  ) {
    const originalStates: { material: any; color: THREE.Color; intensity: number }[] = [];

    forEachMaterial(object, (mat: any) => {
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
  function findBoxInGrid(boxName: string) {
    for (let row = 0; row < boxGrid.length; row++) {
      for (let col = 0; col < boxGrid[row].length; col++) {
        if (boxGrid[row][col].name === boxName) {
          return { data: boxGrid[row][col], row, col };
        }
      }
    }
    return null;
  }

  function getPayloadColor(payload: string) {
    const colors: Record<string, number> = {
      "full": 0x00ff00,
      "partially full": 0x808080,
      "empty": 0xff0000
    };
    return colors[payload] ?? 0xffffff;
  }

  // ============================================================================
  // POSITION CALCULATORS
  // ============================================================================
  function calculateCraneStoragePosition(row: number, col: number) {
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

  function calculateBoxDeliveryPosition(row: number, col: number) {
    return {
      x: CONFIG.POST_OUT_X,
      y: CONFIG.GATE_Y_BASE + (CONFIG.ROW_SPACING * row),
      z: CONFIG.BASE_Z + (CONFIG.ENTRY_GATE_Z_OFFSET - CONFIG.BASE_Z) + (-CONFIG.COL_SPACING * col)
    };
  }

  function calculateRoutingY(row: number) {
    return CONFIG.GATE_Y_BASE + (CONFIG.ROW_SPACING * row);
  }

  function calculateRoutingZ(col: number, gateZOffset: number) {
    return CONFIG.BASE_Z + (gateZOffset - CONFIG.BASE_Z) + (-CONFIG.COL_SPACING * col);
  }

  function calculateExitRoutingPosition(row: number, col: number) {
    return {
      x: CONFIG.INTERMEDIATE_X,
      y: calculateRoutingY(row),
      z: calculateRoutingZ(col, CONFIG.EXIT_GATE_Z_OFFSET)
    };
  }

  function calculateEntryRoutingPosition(row: number, col: number) {
    return {
      x: CONFIG.INTERMEDIATE_X,
      y: calculateRoutingY(row),
      z: calculateRoutingZ(col, CONFIG.ENTRY_GATE_Z_OFFSET)
    };
  }

  // ============================================================================
  // TRAVEL TIME CALCULATOR
  // ============================================================================
  function calculateTravelTime(fromPos: THREE.Vector3, toPos: { x: number; y: number; z: number }) {
    const distance = fromPos.distanceTo(new THREE.Vector3(toPos.x, toPos.y, toPos.z));
    return Math.max(1, (distance / CONFIG.CRANE_SPEED) * 1000);
  }

  // ============================================================================
  // VALIDATION
  // ============================================================================
  function validateBoxOperation(boxName: string, expectedStatus: "In" | "Out") {
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
  async function moveCraneToStorageCell(boxName: string) {
    const boxData = findBoxInGrid(boxName);
    if (!boxData) throw new Error(`Box ${boxName} not found`);
    const targetPos = calculateCraneStoragePosition(boxData.row, boxData.col);
    await movementController.moveObject(controllableCrane as any, targetPos);
  }

  async function moveCraneToExitGate() {
    const targetPos = {
      x: (controllableCrane as any).position.x,
      y: CONFIG.GATE_Y,
      z: CONFIG.EXIT_GATE_Z
    };
    await movementController.moveObject(controllableCrane as any, targetPos);
  }

  async function moveCraneToEntryGate() {
    const targetPos = {
      x: (controllableCrane as any).position.x,
      y: CONFIG.GATE_Y,
      z: CONFIG.ENTRY_GATE_Z
    };
    await movementController.moveObject(controllableCrane as any, targetPos);
  }

  // ============================================================================
  // UI FUNCTIONS (use Svelte refs, not document.getElementById)
  // ============================================================================
  function showToast(message: string, type: 'info' | 'success' = 'info') {
    if (!toastContainerEl) return;
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    toastContainerEl.appendChild(toast);

    setTimeout(() => {
      toast.classList.add('removing');
      setTimeout(() => {
        toastContainerEl.removeChild(toast);
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

    if (fullCountEl) fullCountEl.textContent = String(fullCount);
    if (partialCountEl) partialCountEl.textContent = String(partialCount);
    if (emptyCountEl) emptyCountEl.textContent = String(emptyCount);
  }

  function updateButtonStates() {
    const selectedBox = systemState.selectedBox;
    const isOperating = systemState.isOperationInProgress();

    if (!getBoxOutBtnEl || !putBoxInBtnEl) return;

    if (!selectedBox || isOperating) {
      getBoxOutBtnEl.disabled = true;
      putBoxInBtnEl.disabled = true;
    } else {
      const boxData = findBoxInGrid(selectedBox);
      if (boxData) {
        getBoxOutBtnEl.disabled = boxData.data.status !== "In";
        putBoxInBtnEl.disabled = boxData.data.status !== "Out";
      }
    }
  }

  function populateBoxList() {
    if (!boxListEl) return;
    boxListEl.innerHTML = '';

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
          boxListEl.querySelectorAll('.box-item').forEach(el => el.classList.remove('selected'));
          item.classList.add('selected');
          systemState.setSelectedBox(box.name);
          updateButtonStates();
        });

        boxListEl.appendChild(item);
      });
    });
  }

  function updateBoxListUI() {
    if (!boxListEl) return;
    boxGrid.forEach(row => {
      row.forEach(box => {
        const item = boxListEl.querySelector<HTMLElement>(`[data-box-name="${box.name}"]`);
        if (item) {
          const statusSpan = item.querySelector<HTMLSpanElement>('.box-status');
          if (statusSpan) {
            statusSpan.textContent = box.status.toUpperCase();
            statusSpan.className = `box-status ${box.status.toLowerCase()}`;
          }
        }
      });
    });
  }

  // ============================================================================
  // BOX RETRIEVAL
  // ============================================================================
  async function retrieveBoxFromStorage(boxName: string) {
    const { boxData, boxMesh } = validateBoxOperation(boxName, "In");
    systemState.setOperation(boxName);
    updateButtonStates();

    const routingPos = calculateExitRoutingPosition(boxData.row, boxData.col);

    showToast(`Box ${boxName} get out in progress…`, 'info');

    try {
      await moveCraneToStorageCell(boxName);

      await movementController.moveObject(boxMesh as any, {
        x: CONFIG.INTERMEDIATE_X,
        y: (boxMesh as any).position.y,
        z: (boxMesh as any).position.z
      });

      await Promise.all([
        movementController.moveObject(boxMesh as any, {
          x: CONFIG.INTERMEDIATE_X,
          y: routingPos.y,
          z: routingPos.z
        }),
        moveCraneToExitGate()
      ]);

      await movementController.moveObject(boxMesh as any, {
        x: CONFIG.FINAL_OUT_X,
        y: routingPos.y,
        z: routingPos.z
      });

      await glowEmissiveTemporarily(boxMesh);

      const deliveryPos = { x: CONFIG.POST_OUT_X, y: routingPos.y, z: routingPos.z };
      const travelTime = calculateTravelTime((boxMesh as any).position, deliveryPos);

      await Promise.all([
        movementController.moveObject(boxMesh as any, deliveryPos),
        fadeOpacity(boxMesh, 0.0, travelTime)
      ]);

      boxData.data.status = "Out";
      systemState.clearOperation();

      showToast(`Box ${boxName} got out completed.`, 'success');
      updateStatusCounts();
      updateBoxListUI();
      updateButtonStates();

    } catch (error) {
      console.error(error);
      systemState.clearOperation();
      updateButtonStates();
    }
  }

  // ============================================================================
  // BOX INSERTION
  // ============================================================================
  async function insertBoxToStorage(boxName: string) {
    const { boxData, boxMesh } = validateBoxOperation(boxName, "Out");
    systemState.setOperation(boxName);
    updateButtonStates();

    const storagePos = calculateBoxCellPosition();
    const routingPos = calculateEntryRoutingPosition(boxData.row, boxData.col);
    const cranePos = calculateCraneStoragePosition(boxData.row, boxData.col);

    showToast(`Box ${boxName} put in in progress…`, 'info');

    try {
      (boxMesh as any).position.set(CONFIG.POST_OUT_X, routingPos.y, routingPos.z);
      const prestagePos = { x: CONFIG.FINAL_OUT_X, y: routingPos.y, z: routingPos.z };
      const prestageTime = calculateTravelTime((boxMesh as any).position, prestagePos);

      await Promise.all([
        movementController.moveObject(boxMesh as any, prestagePos),
        fadeOpacity(boxMesh, 1.0, prestageTime)
      ]);

      await moveCraneToEntryGate();

      await movementController.moveObject(boxMesh as any, {
        x: CONFIG.INTERMEDIATE_X,
        y: routingPos.y,
        z: routingPos.z
      });

      await Promise.all([
        movementController.moveObject(boxMesh as any, {
          x: CONFIG.INTERMEDIATE_X,
          y: storagePos.y,
          z: storagePos.z
        }),
        movementController.moveObject(controllableCrane as any, cranePos)
      ]);

      await movementController.moveObject(boxMesh as any, {
        x: CONFIG.STORAGE_X,
        y: storagePos.y,
        z: storagePos.z
      });

      await glowEmissiveTemporarily(boxMesh);

      boxData.data.status = "In";
      systemState.clearOperation();

      showToast(`Box ${boxName} put in completed.`, 'success');
      updateStatusCounts();
      updateBoxListUI();
      updateButtonStates();

    } catch (error) {
      console.error(error);
      systemState.clearOperation();
      updateButtonStates();
    }
  }

  // ============================================================================
  // OBJECT LOOKUP HELPER
  // ============================================================================
  function findObjectByNames(parent: THREE.Object3D, nameList: string[]) {
    for (const name of nameList) {
      const obj = parent.getObjectByName(name);
      if (obj) return obj;
    }
    return null;
  }

  // ============================================================================
  // THREE.JS SCENE INITIALIZATION
  // ============================================================================
  function getRenderDimensions() {
    if (container3DEl) {
      const width = container3DEl.clientWidth || window.innerWidth;
      const height = container3DEl.clientHeight || window.innerHeight;
      return { width, height };
    }
    return { width: window.innerWidth, height: window.innerHeight };
  }

  function initScene() {
    if (!container3DEl) {
      throw new Error('3D container element not mounted yet');
    }

    scene = new THREE.Scene();
    scene.background = new THREE.Color(0xEBEBEB);

    const { width, height } = getRenderDimensions();

    camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000);
    camera.position.set(CAMERA_PRESETS.front.x, CAMERA_PRESETS.front.y, CAMERA_PRESETS.front.z);
    camera.lookAt(CAMERA_LOOK_TARGET);

    renderer = new THREE.WebGLRenderer({
      alpha: true,
      antialias: true,
      powerPreference: "high-performance"
    });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.2;
    container3DEl.appendChild(renderer.domElement);

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
    controls.minDistance = CAMERA_MIN_DISTANCE;
    controls.maxDistance = CAMERA_MAX_DISTANCE;
    controls.maxPolarAngle = Math.PI;
    controls.target.copy(CAMERA_LOOK_TARGET);
    controls.update();

    clock = new THREE.Clock();
  }

  // ============================================================================
  // MODEL LOADING
  // ============================================================================
  function loadModel() {
    const loader = new GLTFLoader();

    loader.load(
      CONFIG.BOX_MODEL_URL,
      function (gltf) {
        sceneRoot = gltf.scene;

        sceneRoot.traverse((child: any) => {
          if (child.isMesh) {
            child.castShadow = true;
            child.receiveShadow = true;
          }
        });

        decorativeCrane = findObjectByNames(sceneRoot, CONFIG.CRANE_NAMES.decorative);
        controllableCrane = findObjectByNames(sceneRoot, CONFIG.CRANE_NAMES.controllable);

        boxGrid.forEach((row, rowIndex) => {
          row.forEach((boxData, colIndex) => {
            const boxMesh = sceneRoot.getObjectByName(boxData.name);

            if (boxMesh) {
              const color = getPayloadColor(boxData.payload);
              boxMesh.traverse((child: any) => {
                if (child.isMesh) {
                  child.material = new THREE.MeshStandardMaterial({ color });
                }
              });

              const initialPos = (boxData.status === "In")
                ? calculateBoxCellPosition()
                : calculateBoxDeliveryPosition(rowIndex, colIndex);

              (boxMesh as any).position.set(initialPos.x, initialPos.y, initialPos.z);
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
      (decorativeCrane as any).position.z = (controllableCrane as any).position.z;
    }

    movementController.update(delta);
    cameraController.update();

    controls.update();
    renderer.render(scene, camera);
  }

  // ============================================================================
  // COMPASS CAMERA CONTROLS
  // ============================================================================
  const CAMERA_DISTANCE = 320;
  const CAMERA_HEIGHT = 125;
  const CAMERA_MIN_DISTANCE = 220;
  const CAMERA_MAX_DISTANCE = 520;
  const CAMERA_LOOK_TARGET = new THREE.Vector3(10, 35, -20);

  const CAMERA_PRESETS = {
    front: {
      x: CAMERA_LOOK_TARGET.x + CAMERA_DISTANCE,
      y: CAMERA_HEIGHT,
      z: CAMERA_LOOK_TARGET.z
    },
    right: {
      x: CAMERA_LOOK_TARGET.x,
      y: CAMERA_HEIGHT,
      z: CAMERA_LOOK_TARGET.z + CAMERA_DISTANCE
    },
    back: {
      x: CAMERA_LOOK_TARGET.x - CAMERA_DISTANCE,
      y: CAMERA_HEIGHT,
      z: CAMERA_LOOK_TARGET.z
    },
    left: {
      x: CAMERA_LOOK_TARGET.x,
      y: CAMERA_HEIGHT,
      z: CAMERA_LOOK_TARGET.z - CAMERA_DISTANCE
    }
  };

  async function rotateCameraTo(direction: 'front' | 'right' | 'back' | 'left') {
    if (cameraController.isAnimating()) return;
    const targetPos = CAMERA_PRESETS[direction];
    await cameraController.moveCameraToPreset(targetPos);
  }

  // ============================================================================
  // SVELTE LIFECYCLE
  // ============================================================================
  onMount(() => {
    populateBoxList();
    updateStatusCounts();
    updateButtonStates();

    initScene();
    loadModel();
    animate();

    const handleGetOut = () => {
      const selectedBox = systemState.selectedBox;
      if (selectedBox) {
        retrieveBoxFromStorage(selectedBox);
      }
    };

    const handlePutIn = () => {
      const selectedBox = systemState.selectedBox;
      if (selectedBox) {
        insertBoxToStorage(selectedBox);
      }
    };

    getBoxOutBtnEl.addEventListener('click', handleGetOut);
    putBoxInBtnEl.addEventListener('click', handlePutIn);

    const handleResize = () => {
      const { width, height } = getRenderDimensions();
      camera.aspect = width / height;
      camera.updateProjectionMatrix();
      renderer.setSize(width, height);
    };

    window.addEventListener('resize', handleResize);

    return () => {
      getBoxOutBtnEl.removeEventListener('click', handleGetOut);
      putBoxInBtnEl.removeEventListener('click', handlePutIn);
      window.removeEventListener('resize', handleResize);
      movementController.stopAll();
      if (renderer) {
        renderer.dispose();
        const canvas = renderer.domElement;
        canvas.parentNode?.removeChild(canvas);
      }
    };
  });
</script>

<!-- MARKUP -->

<div class="digital-twin-root">
  <div id="container3D" bind:this={container3DEl}></div>

  <!-- Compass UI -->
  <div class="compass-ui">
    <button class="compass-btn front" on:click={() => rotateCameraTo('front')} title="Front View">
      Front
    </button>
    <div class="compass-row">
      <button class="compass-btn left" on:click={() => rotateCameraTo('left')} title="Left View">
        Left
      </button>
      <div class="compass-center"></div>
      <button class="compass-btn right" on:click={() => rotateCameraTo('right')} title="Right View">
        Right
      </button>
    </div>
    <button class="compass-btn back" on:click={() => rotateCameraTo('back')} title="Back View">
      Back
    </button>
  </div>

  <div class="control-panel" class:hidden={systemState.hideUI}>
    <div class="panel-title">Select Box</div>
    <div class="box-list" bind:this={boxListEl}></div>
    <div class="action-buttons">
      <button id="getBoxOutBtn" bind:this={getBoxOutBtnEl} disabled>Out</button>
      <button id="putBoxInBtn" bind:this={putBoxInBtnEl} disabled>In</button>
    </div>
  </div>

  <div class="status-label" class:hidden={systemState.hideUI}>
    <div class="status-item">
      <div class="color1"></div>
      <div class="status-count full" bind:this={fullCountEl}>0</div>
      <div class="status-text">: Full</div>
    </div>
    <div class="status-item">
      <div class="color2"></div>
      <div class="status-count partial" bind:this={partialCountEl}>0</div>
      <div class="status-text">: Partially full.</div>
    </div>
    <div class="status-item">
      <div class="color3"></div>
      <div class="status-count empty" bind:this={emptyCountEl}>0</div>
      <div class="status-text">Empty</div>
    </div>
  </div>

  <div class="toast-container" bind:this={toastContainerEl}></div>
</div>

<style>
  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }

  .digital-twin-root {
    position: relative;
    width: 100%;
    height: calc(100vh - 180px);
    min-height: 520px;
    background: #EBEBEB;
    border-radius: 24px;
    overflow: hidden;
  }

  #container3D {
    width: 100%;
    height: 100%;
    background: #EBEBEB;
  }

  #container3D canvas {
    width: 100% !important;
    height: 100% !important;
    display: block;
    background: #EBEBEB;
  }

  /* Compass UI Styles */
  .compass-ui {
    position: absolute;
    top: 20px;
    right: 20px;
    z-index: 150;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 14px;
    background: transparent;
    padding: 0;
    transition: opacity 0.3s ease, visibility 0.3s ease;
  }

  .compass-ui.hidden {
    opacity: 0;
    visibility: hidden;
    pointer-events: none;
  }

  .compass-row {
    display: flex;
    align-items: center;
    gap: 18px;
  }

  .compass-center {
    width: 18px;
    height: 18px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(255, 198, 126, 0.85) 0%, rgba(255, 198, 126, 0) 70%);
    box-shadow: 0 0 12px rgba(255, 198, 126, 0.7);
  }

  .compass-btn {
    width: 64px;
    height: 64px;
    border-radius: 50%;
    border: 1.5px solid rgba(0, 0, 0, 0.2);
    background: #fff;
    color: #1f1f1f;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    cursor: pointer;
    transition: transform 0.15s ease, box-shadow 0.15s ease, background 0.15s ease;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 6px 18px rgba(0, 0, 0, 0.15);
  }

  .compass-btn:hover {
    background: linear-gradient(135deg, #ff6b35 0%, #ffb347 100%);
    color: #fff;
    transform: translateY(-2px);
    box-shadow: 0 10px 25px rgba(255, 107, 53, 0.4);
  }

  .compass-btn:active {
    transform: translateY(0);
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.25);
  }

  @media (max-width: 1200px), (max-height: 700px) {
    .compass-ui {
      top: 12px;
      right: 12px;
      gap: 10px;
    }

    .compass-row {
      gap: 12px;
    }

    .compass-btn {
      width: 50px;
      height: 50px;
      font-size: 9px;
      letter-spacing: 0.04em;
    }

    .compass-center {
      width: 14px;
      height: 14px;
    }
  }

  .control-panel {
    position: absolute;
    top: 147px;
    left: 0px;
    transform: translateY(-50%);
    background: rgba(255, 255, 255, 0.16);
    padding: 20px;
    border-radius: 12px;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(0, 0, 0, 0.32);
    width: 232px;
    z-index: 100;
    transition: opacity 0.3s ease, visibility 0.3s ease;
  }

  .control-panel.hidden {
    opacity: 0;
    visibility: hidden;
    pointer-events: none;
  }

  .panel-title {
    font-size: 14px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: #666;
    margin-bottom: 12px;
  }

  .box-list {
    max-height: 164px;
    overflow-y: auto;
    background: rgba(0, 0, 0, 0.05);
    border-radius: 8px;
    margin-bottom: 16px;
  }

  .box-item {
    padding: 10px 14px;
    border-bottom: 1px solid rgba(0, 0, 0, 0.1);
    cursor: pointer;
    transition: background 0.2s;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .box-item:last-child {
    border-bottom: none;
  }

  .box-item:hover {
    background: rgba(0, 0, 0, 0.05);
  }

  .box-item.selected {
    background: rgba(255, 171, 60, 0.378);
    border-left: 4px solid #FF5622;
  }

  .box-name {
    font-weight: 600;
    font-size: 14px;
    color: #000;
  }

  .box-status {
    font-size: 14px;
    padding: 4px 12px;
    border-radius: 12px;
    font-weight: 500;
  }

  .box-status.in {
    background: rgba(132, 200, 255, 0.221);
    color: #09518c;
  }

  .box-status.out {
    background: rgba(255, 153, 0, 0.153);
    color: #b77715;
  }

  .action-buttons {
    display: flex;
    gap: 8px;
  }

  button {
    flex: 1;
    height: 40px;
    padding: 8px 8px;
    border: none;
    border-radius: 8px;
    color: white;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  button:disabled {
    opacity: 0.4;
    cursor: not-allowed;
    transform: none !important;
  }

  button:not(:disabled):hover {
    transform: translateY(-2px);
  }

  button:not(:disabled):active {
    transform: translateY(0);
  }

  #getBoxOutBtn {
    background: #000000DE;
  }

  #getBoxOutBtn:not(:disabled):hover {
    background: #00000052;
  }

  #putBoxInBtn {
    background: #000000DE;
  }

  #putBoxInBtn:not(:disabled):hover {
    background: #00000052;
  }

  .status-label {
    position: absolute;
    bottom: 132px;
    left: 0px;
    background: transparent;
    padding: 0;
    border-radius: 0;
    box-shadow: none;
    backdrop-filter: none;
    border: none;
    z-index: 100;
    display: flex;
    flex-direction: column;
    gap: 12px;
    transition: opacity 0.3s ease, visibility 0.3s ease;
  }

  .status-label.hidden {
    opacity: 0;
    visibility: hidden;
    pointer-events: none;
  }

  .status-item {
    display: flex;
    flex-direction: row;
    align-items: center;
    gap: 12px;
  }

  .status-count {
    font-size: 16px;
    font-weight: 700;
    line-height: 1;
    min-width: 35px;
  }

  .color1,
  .color2,
  .color3 {
    width: 16px;
    height: 16px;
    border-radius: 50%;
  }

  .color1 { background-color: #00ff00; }
  .color2 { background-color: #808080; }
  .color3 { background-color: #ff0000; }

  .status-text {
    font-size: 14px;
    color: #333;
    font-weight: 400;
  }

  .toast-container {
    position: absolute;
    bottom: 240px;
    left: 0px;
    z-index: 1000;
    display: flex;
    flex-direction: column;
    gap: 12px;
    width: 280px;
  }

  .toast {
    background: rgba(255, 255, 255, 0.95);
    padding: 16px 16px;
    border-radius: 8px;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(0, 0, 0, 0.1);
    animation: slideIn 0.2s linear;
    width: 232px;
    color: #000;
    font-size: 14px;
  }

  .toast.success {
    border-left: 4px solid #4CAF50;
  }

  .toast.info {
    border-left: 4px solid #2196F3;
  }

  @keyframes slideIn {
    from {
      transform: translateY(20px);
    }
    to {
      transform: translateY(0);
    }
  }

  @keyframes slideOut {
    from {
      transform: translateY(0);
      opacity: 1;
    }

    to {
      transform: translateY(40px);
      opacity: 0;
    }
  }

  .toast.removing {
    animation: slideOut 0.4s linear;
  }
</style>

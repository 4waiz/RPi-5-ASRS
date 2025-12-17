<script lang="ts">
  import { onMount } from "svelte";
  import * as THREE from "three";
  import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
  import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";
  import { t } from "../../lib/i18n";
  import { get } from "svelte/store";

  // ---------- DOM refs (Svelte 5-friendly, no document.getElementById) ----------
  let container3DEl: HTMLDivElement;
  let boxListEl: HTMLDivElement;
  let getBoxOutBtnEl: HTMLButtonElement;
  let putBoxInBtnEl: HTMLButtonElement;
  let fullCountEl: HTMLDivElement;
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
    CRANE_NAMES: {
      decorative: ["crane", "Crane", "CRANE"],
      controllable: [
        "crane.002",
        "crane002",
        "Crane.002",
        "Crane002",
        "crane_002",
      ],
    },
    BOX_MODEL_URL: "/Static/Models/Box/full2.glb",
  };

  // ============================================================================
  // BOX DATA - 6x4 Grid (24 boxes)
  // ============================================================================
  const boxGrid = [
    [
      { name: "box_1", status: "Out", payload: "full" },
      { name: "box_2", status: "Out", payload: "empty" },
      { name: "box_3", status: "In", payload: "partially full" },
      { name: "box_4", status: "Out", payload: "full" },
    ],
    [
      { name: "box_5", status: "In", payload: "empty" },
      { name: "box_6", status: "In", payload: "full" },
      { name: "box_7", status: "In", payload: "full" },
      { name: "box_8", status: "In", payload: "partially full" },
    ],
    [
      { name: "box_9", status: "In", payload: "empty" },
      { name: "box_10", status: "In", payload: "full" },
      { name: "box_11", status: "In", payload: "full" },
      { name: "box_12", status: "In", payload: "empty" },
    ],
    [
      { name: "box_13", status: "In", payload: "empty" },
      { name: "box_14", status: "In", payload: "partially full" },
      { name: "box_15", status: "In", payload: "full" },
      { name: "box_16", status: "In", payload: "full" },
    ],
    [
      { name: "box_17", status: "In", payload: "partially full" },
      { name: "box_18", status: "In", payload: "empty" },
      { name: "box_19", status: "In", payload: "full" },
      { name: "box_20", status: "In", payload: "empty" },
    ],
    [
      { name: "box_21", status: "In", payload: "partially full" },
      { name: "box_22", status: "In", payload: "full" },
      { name: "box_23", status: "In", payload: "empty" },
      { name: "box_24", status: "In", payload: "full" },
    ],
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
  // CAMERA COORDINATES STATE
  // ============================================================================
  let cameraCoords = $state({ x: 0, y: 0, z: 0 });

  function updateCameraCoords() {
    if (camera) {
      cameraCoords = {
        x: Math.round(camera.position.x * 10) / 10,
        y: Math.round(camera.position.y * 10) / 10,
        z: Math.round(camera.position.z * 10) / 10,
      };
    }
  }

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
      speed = CONFIG.CRANE_SPEED,
    ) {
      if (!object.name) {
        throw new Error(
          "Object must have a name property for movement tracking",
        );
      }

      return new Promise<void>((resolve) => {
        const movementData: MovementData = {
          object,
          target: new THREE.Vector3(targetPos.x, targetPos.y, targetPos.z),
          speed,
          onComplete: resolve,
        };
        this.activeMovements.set(object.name, movementData);
      });
    }

    update(delta: number) {
      this.activeMovements.forEach((movement, objectName) => {
        const { object, target, speed, onComplete } = movement;

        const direction = new THREE.Vector3().subVectors(
          target,
          object.position,
        );
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
      this.activeMovements.forEach((movement) => {
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
      duration = 1000,
    ) {
      return new Promise<void>((resolve) => {
        this.activeAnimation = {
          startPos: camera.position.clone(),
          targetPos: new THREE.Vector3(targetPos.x, targetPos.y, targetPos.z),
          startTime: performance.now(),
          duration,
          onComplete: resolve,
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
      const eased =
        progress < 0.5
          ? 4 * progress * progress * progress
          : 1 - Math.pow(-2 * progress + 2, 3) / 2;

      // Use spherical interpolation to orbit around the target
      const startVec = this.activeAnimation.startPos
        .clone()
        .sub(CAMERA_LOOK_TARGET);
      const endVec = this.activeAnimation.targetPos
        .clone()
        .sub(CAMERA_LOOK_TARGET);

      // Convert to spherical coordinates
      const startSpherical = new THREE.Spherical().setFromVector3(startVec);
      const endSpherical = new THREE.Spherical().setFromVector3(endVec);

      // Interpolate angles - choose shortest path
      let deltaTheta = endSpherical.theta - startSpherical.theta;
      if (deltaTheta > Math.PI) deltaTheta -= Math.PI * 2;
      if (deltaTheta < -Math.PI) deltaTheta += Math.PI * 2;

      const currentRadius = THREE.MathUtils.lerp(
        startSpherical.radius,
        endSpherical.radius,
        eased,
      );
      const currentPhi = THREE.MathUtils.lerp(
        startSpherical.phi,
        endSpherical.phi,
        eased,
      );
      const currentTheta = startSpherical.theta + deltaTheta * eased;

      // Convert back to Cartesian and apply to camera
      const newPos = new THREE.Vector3()
        .setFromSpherical(
          new THREE.Spherical(currentRadius, currentPhi, currentTheta),
        )
        .add(CAMERA_LOOK_TARGET);

      camera.position.copy(newPos);

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
  function forEachMaterial(
    object: THREE.Object3D,
    callback: (mat: THREE.Material) => void,
  ) {
    object.traverse((child: any) => {
      if (child.isMesh && child.material) {
        const materials = Array.isArray(child.material)
          ? child.material
          : [child.material];
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

  function fadeOpacity(
    object: THREE.Object3D,
    toOpacity: number,
    durationMs: number,
  ) {
    return new Promise<void>((resolve) => {
      let startTime: number | null = null;
      let startOpacity = 1.0;
      let captured = false;

      forEachMaterial(object, (mat: any) => {
        if (!captured) {
          startOpacity = typeof mat.opacity === "number" ? mat.opacity : 1.0;
          captured = true;
        }
        mat.transparent = true;
      });

      function animate(timestamp: number) {
        if (!startTime) startTime = timestamp;
        const progress = Math.min(1, (timestamp - startTime) / durationMs);
        const currentOpacity =
          startOpacity + (toOpacity - startOpacity) * progress;
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
    switch (payload) {
      case "empty":
        return 0xff0000; // Red for empty
      case "full":
        return 0x00ff00; // Green for full
      case "partially full":
        return 0x808080; // Gray for partially full
      default:
        return 0x808080; // Default gray
    }
  }

  // ============================================================================
  // POSITION CALCULATORS
  // ============================================================================
  function calculateCraneStoragePosition(row: number, col: number) {
    return {
      x: CONFIG.STORAGE_X,
      y: 9.2 + 19.8 * (5 - row),
      z: 119.6 - CONFIG.COL_SPACING * (3 - col),
    };
  }

  function calculateBoxCellPosition() {
    return {
      x: CONFIG.STORAGE_X,
      y: CONFIG.BASE_Y,
      z: CONFIG.BASE_Z,
    };
  }

  function calculateBoxDeliveryPosition(row: number, col: number) {
    return {
      x: CONFIG.POST_OUT_X,
      y: CONFIG.GATE_Y_BASE + CONFIG.ROW_SPACING * row,
      z:
        CONFIG.BASE_Z +
        (CONFIG.ENTRY_GATE_Z_OFFSET - CONFIG.BASE_Z) +
        -CONFIG.COL_SPACING * col,
    };
  }

  function calculateRoutingY(row: number) {
    return CONFIG.GATE_Y_BASE + CONFIG.ROW_SPACING * row;
  }

  function calculateRoutingZ(col: number, gateZOffset: number) {
    return (
      CONFIG.BASE_Z + (gateZOffset - CONFIG.BASE_Z) + -CONFIG.COL_SPACING * col
    );
  }

  function calculateExitRoutingPosition(row: number, col: number) {
    return {
      x: CONFIG.INTERMEDIATE_X,
      y: calculateRoutingY(row),
      z: calculateRoutingZ(col, CONFIG.EXIT_GATE_Z_OFFSET),
    };
  }

  function calculateEntryRoutingPosition(row: number, col: number) {
    return {
      x: CONFIG.INTERMEDIATE_X,
      y: calculateRoutingY(row),
      z: calculateRoutingZ(col, CONFIG.ENTRY_GATE_Z_OFFSET),
    };
  }

  // ============================================================================
  // TRAVEL TIME CALCULATOR
  // ============================================================================
  function calculateTravelTime(
    fromPos: THREE.Vector3,
    toPos: { x: number; y: number; z: number },
  ) {
    const distance = fromPos.distanceTo(
      new THREE.Vector3(toPos.x, toPos.y, toPos.z),
    );
    return Math.max(1, (distance / CONFIG.CRANE_SPEED) * 1000);
  }

  // ============================================================================
  // VALIDATION
  // ============================================================================
  function validateBoxOperation(boxName: string, expectedStatus: "In" | "Out") {
    if (!systemState.ready) {
      throw new Error("System not ready");
    }

    if (systemState.isOperationInProgress()) {
      throw new Error(
        `Operation already in progress: ${systemState.currentOperation}`,
      );
    }

    const boxData = findBoxInGrid(boxName);
    if (!boxData) {
      throw new Error(`Box ${boxName} not found in grid`);
    }

    if (boxData.data.status !== expectedStatus) {
      throw new Error(
        `Box ${boxName} has invalid status: ${boxData.data.status} (expected: ${expectedStatus})`,
      );
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
      z: CONFIG.EXIT_GATE_Z,
    };
    await movementController.moveObject(controllableCrane as any, targetPos);
  }

  async function moveCraneToEntryGate() {
    const targetPos = {
      x: (controllableCrane as any).position.x,
      y: CONFIG.GATE_Y,
      z: CONFIG.ENTRY_GATE_Z,
    };
    await movementController.moveObject(controllableCrane as any, targetPos);
  }

  // ============================================================================
  // UI FUNCTIONS (use Svelte refs, not document.getElementById)
  // ============================================================================
  function showToast(message: string, type: "info" | "success" = "info") {
    if (!toastContainerEl) return;
    const toast = document.createElement("div");
    toast.className = `toast ${type}`;
    toast.textContent = message;
    toastContainerEl.appendChild(toast);

    setTimeout(() => {
      toast.classList.add("removing");
      setTimeout(() => {
        toastContainerEl.removeChild(toast);
      }, 300);
    }, 6000);
  }

  function updateStatusCounts() {
    let totalInStorage = 0;

    boxGrid.forEach((row) => {
      row.forEach((box) => {
        if (box.status === "In") totalInStorage++;
      });
    });

    if (fullCountEl) fullCountEl.textContent = String(totalInStorage);
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

  function markSelectedBox(boxName: string | null) {
    if (!boxListEl) return;
    boxListEl.querySelectorAll<HTMLElement>(".box-item").forEach((el) => {
      const isMatch = boxName !== null && el.dataset.boxName === boxName;
      el.classList.toggle("selected", isMatch);
    });
  }

  // Helper function to translate box name (box_1 -> صندوق_1 in Arabic)
  function translateBoxName(boxName: string): string {
    const match = boxName.match(/box_(\d+)/);
    if (match) {
      const number = match[1];
      return get(t)("digitalTwin.boxName").replace("{number}", number);
    }
    return boxName;
  }

  // Helper function to translate status (In/Out -> إدخال/إخراج in Arabic)
  function translateStatus(status: string): string {
    const statusLower = status.toLowerCase();
    if (statusLower === "in") {
      return get(t)("digitalTwin.statusIn");
    } else if (statusLower === "out") {
      return get(t)("digitalTwin.statusOut");
    }
    return status.toUpperCase();
  }

  function populateBoxList() {
    if (!boxListEl) return;
    boxListEl.innerHTML = "";

    boxGrid.forEach((row) => {
      row.forEach((box) => {
        const item = document.createElement("div");
        item.className = "box-item";
        item.dataset.boxName = box.name;

        const nameSpan = document.createElement("span");
        nameSpan.className = "box-name";
        nameSpan.textContent = translateBoxName(box.name);

        const statusSpan = document.createElement("span");
        statusSpan.className = `box-status ${box.status.toLowerCase()}`;
        statusSpan.textContent = translateStatus(box.status);

        item.appendChild(nameSpan);
        item.appendChild(statusSpan);

        item.addEventListener("click", () => {
          systemState.setSelectedBox(box.name);
          markSelectedBox(box.name);
          updateButtonStates();
        });

        boxListEl.appendChild(item);
      });
    });
  }

  function updateBoxListUI() {
    if (!boxListEl) return;
    boxGrid.forEach((row) => {
      row.forEach((box) => {
        const item = boxListEl.querySelector<HTMLElement>(
          `[data-box-name="${box.name}"]`,
        );
        if (item) {
          const nameSpan = item.querySelector<HTMLSpanElement>(".box-name");
          const statusSpan = item.querySelector<HTMLSpanElement>(".box-status");

          if (nameSpan) {
            nameSpan.textContent = translateBoxName(box.name);
          }

          if (statusSpan) {
            statusSpan.textContent = translateStatus(box.status);
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

    showToast(
      get(t)("digitalTwin.getOutInProgress").replace("{box}", boxName),
      "info",
    );

    try {
      await moveCraneToStorageCell(boxName);

      await movementController.moveObject(boxMesh as any, {
        x: CONFIG.INTERMEDIATE_X,
        y: (boxMesh as any).position.y,
        z: (boxMesh as any).position.z,
      });

      await Promise.all([
        movementController.moveObject(boxMesh as any, {
          x: CONFIG.INTERMEDIATE_X,
          y: routingPos.y,
          z: routingPos.z,
        }),
        moveCraneToExitGate(),
      ]);

      await movementController.moveObject(boxMesh as any, {
        x: CONFIG.FINAL_OUT_X,
        y: routingPos.y,
        z: routingPos.z,
      });

      const deliveryPos = {
        x: CONFIG.POST_OUT_X,
        y: routingPos.y,
        z: routingPos.z,
      };
      const travelTime = calculateTravelTime(
        (boxMesh as any).position,
        deliveryPos,
      );

      await Promise.all([
        movementController.moveObject(boxMesh as any, deliveryPos),
        fadeOpacity(boxMesh, 0.0, travelTime),
      ]);

      boxData.data.status = "Out";
      systemState.clearOperation();

      showToast(
        get(t)("digitalTwin.getOutCompleted").replace("{box}", boxName),
        "success",
      );
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

    showToast(
      get(t)("digitalTwin.putInInProgress").replace("{box}", boxName),
      "info",
    );

    try {
      (boxMesh as any).position.set(
        CONFIG.POST_OUT_X,
        routingPos.y,
        routingPos.z,
      );
      const prestagePos = {
        x: CONFIG.FINAL_OUT_X,
        y: routingPos.y,
        z: routingPos.z,
      };
      const prestageTime = calculateTravelTime(
        (boxMesh as any).position,
        prestagePos,
      );

      await Promise.all([
        movementController.moveObject(boxMesh as any, prestagePos),
        fadeOpacity(boxMesh, 1.0, prestageTime),
      ]);

      await moveCraneToEntryGate();

      await movementController.moveObject(boxMesh as any, {
        x: CONFIG.INTERMEDIATE_X,
        y: routingPos.y,
        z: routingPos.z,
      });

      await Promise.all([
        movementController.moveObject(boxMesh as any, {
          x: CONFIG.INTERMEDIATE_X,
          y: storagePos.y,
          z: storagePos.z,
        }),
        movementController.moveObject(controllableCrane as any, cranePos),
      ]);

      await movementController.moveObject(boxMesh as any, {
        x: CONFIG.STORAGE_X,
        y: storagePos.y,
        z: storagePos.z,
      });

      boxData.data.status = "In";
      systemState.clearOperation();

      showToast(
        get(t)("digitalTwin.putInCompleted").replace("{box}", boxName),
        "success",
      );
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
      throw new Error("3D container element not mounted yet");
    }

    scene = new THREE.Scene();

    const { width, height } = getRenderDimensions();

    camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000);
    camera.position.set(304.9, 72.4, -162.7);
    camera.lookAt(CAMERA_LOOK_TARGET);

    renderer = new THREE.WebGLRenderer({
      alpha: true,
      antialias: false, // Disable for faster initialization
      powerPreference: "high-performance",
      stencil: false, // Disable unused features
      depth: true,
    });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.5));
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.BasicShadowMap;
    renderer.shadowMap.autoUpdate = false; // Manual updates for better performance
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
    mainLight.shadow.mapSize.width = 1024;
    mainLight.shadow.mapSize.height = 1024;
    mainLight.shadow.bias = -0.0005;
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
  // MODEL LOADING WITH CACHING AND OPTIMIZATION
  // ============================================================================
  let cachedModel: any = null;
  let isLoading = false;

  function loadModel() {
    // If model is already cached, use it immediately
    if (cachedModel) {
      setupScene(cachedModel.scene.clone());
      return Promise.resolve();
    }

    // If already loading, wait for it
    if (isLoading) {
      return Promise.resolve();
    }

    isLoading = true;
    const loader = new GLTFLoader();

    return new Promise<void>((resolve, reject) => {
      // Use fetch with cache for faster subsequent loads
      fetch(CONFIG.BOX_MODEL_URL)
        .then((response) => response.arrayBuffer())
        .then((buffer) => {
          loader.parse(
            buffer,
            "",
            (gltf) => {
              cachedModel = gltf;
              isLoading = false;
              // Use requestAnimationFrame to avoid blocking
              requestAnimationFrame(() => {
                setupScene(gltf.scene);
                resolve();
              });
            },
            (error) => {
              console.error("Model parse error:", error);
              isLoading = false;
              reject(error);
            },
          );
        })
        .catch((error) => {
          console.error("Model fetch error:", error);
          isLoading = false;
          reject(error);
        });
    });
  }

  function setupScene(loadedScene: THREE.Object3D) {
    sceneRoot = loadedScene;

    sceneRoot.traverse((child: any) => {
      if (child.isMesh) {
        child.castShadow = true;
        child.receiveShadow = true;
      }
    });

    decorativeCrane = findObjectByNames(
      sceneRoot,
      CONFIG.CRANE_NAMES.decorative,
    );
    controllableCrane = findObjectByNames(
      sceneRoot,
      CONFIG.CRANE_NAMES.controllable,
    );

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

          const initialPos =
            boxData.status === "In"
              ? calculateBoxCellPosition()
              : calculateBoxDeliveryPosition(rowIndex, colIndex);

          (boxMesh as any).position.set(
            initialPos.x,
            initialPos.y,
            initialPos.z,
          );
          setMeshOpacity(boxMesh, boxData.status === "In" ? 1.0 : 0.0);
        }
      });
    });

    scene.add(sceneRoot);

    // Update shadow map once after adding model
    if (renderer) {
      renderer.shadowMap.needsUpdate = true;
    }

    systemState.setReady(true);

    populateBoxList();
    updateStatusCounts();
    updateButtonStates();
  }

  // ============================================================================
  // ANIMATION LOOP WITH VISIBILITY DETECTION
  // ============================================================================
  let isPageVisible = true;
  let animationFrameId: number | null = null;

  function animate() {
    if (!isPageVisible) {
      animationFrameId = null;
      return;
    }

    animationFrameId = requestAnimationFrame(animate);

    const delta = clock.getDelta();

    if (decorativeCrane && controllableCrane) {
      (decorativeCrane as any).position.z = (
        controllableCrane as any
      ).position.z;
    }

    movementController.update(delta);
    cameraController.update();

    controls.update();
    updateCameraCoords();
    renderer.render(scene, camera);
  }

  function startAnimation() {
    if (isPageVisible && !animationFrameId) {
      animate();
    }
  }

  function stopAnimation() {
    if (animationFrameId) {
      cancelAnimationFrame(animationFrameId);
      animationFrameId = null;
    }
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
      z: CAMERA_LOOK_TARGET.z,
    },
    right: {
      x: CAMERA_LOOK_TARGET.x,
      y: CAMERA_HEIGHT,
      z: CAMERA_LOOK_TARGET.z + CAMERA_DISTANCE,
    },
    back: {
      x: CAMERA_LOOK_TARGET.x - CAMERA_DISTANCE,
      y: CAMERA_HEIGHT,
      z: CAMERA_LOOK_TARGET.z,
    },
    left: {
      x: CAMERA_LOOK_TARGET.x,
      y: CAMERA_HEIGHT,
      z: CAMERA_LOOK_TARGET.z - CAMERA_DISTANCE,
    },
  };

  async function rotateCameraTo(
    direction: "front" | "right" | "back" | "left",
  ) {
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

    // Start animation immediately so scene is visible
    startAnimation();

    // Load model in parallel (non-blocking)
    loadModel().catch((err) => {
      console.error("Failed to load model:", err);
    });

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

    getBoxOutBtnEl.addEventListener("click", handleGetOut);
    putBoxInBtnEl.addEventListener("click", handlePutIn);

    const handleResize = () => {
      const { width, height } = getRenderDimensions();
      camera.aspect = width / height;
      camera.updateProjectionMatrix();
      renderer.setSize(width, height);
    };

    window.addEventListener("resize", handleResize);

    // Pause animation when page/tab is not visible
    const handleVisibilityChange = () => {
      if (document.hidden) {
        isPageVisible = false;
        stopAnimation();
      } else {
        isPageVisible = true;
        startAnimation();
      }
    };

    document.addEventListener("visibilitychange", handleVisibilityChange);

    return () => {
      getBoxOutBtnEl.removeEventListener("click", handleGetOut);
      putBoxInBtnEl.removeEventListener("click", handlePutIn);
      window.removeEventListener("resize", handleResize);
      document.removeEventListener("visibilitychange", handleVisibilityChange);
      stopAnimation();
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
  <div class="compass-ui" class:hidden={systemState.hideUI}>
    <div class="gizmo-container">
      <div class="gizmo-center"></div>

      <!-- Axis lines -->
      <div class="axis-line axis-x"></div>
      <div class="axis-line axis-y"></div>
      <div class="axis-line axis-z-top"></div>
      <div class="axis-line axis-z-bottom"></div>

      <!-- Axis buttons -->
      <button
        class="axis-btn axis-btn-front"
        onclick={() => rotateCameraTo("front")}
        title={$t("digitalTwin.frontView")}
      >
        <span class="axis-label">F</span>
      </button>

      <button
        class="axis-btn axis-btn-left"
        onclick={() => rotateCameraTo("left")}
        title={$t("digitalTwin.leftView")}
      >
        <span class="axis-label">L</span>
      </button>

      <button
        class="axis-btn axis-btn-right"
        onclick={() => rotateCameraTo("right")}
        title={$t("digitalTwin.rightView")}
      >
        <span class="axis-label">R</span>
      </button>

      <button
        class="axis-btn axis-btn-back"
        onclick={() => rotateCameraTo("back")}
        title={$t("digitalTwin.backView")}
      >
        <span class="axis-label">B</span>
      </button>
    </div>
  </div>

  <!-- Camera Coordinates Display -->
  <div class="camera-coords" class:hidden={systemState.hideUI}>
    <div class="coords-title">Camera Position</div>
    <div class="coord-row">
      <span class="coord-label x">X</span>
      <span class="coord-value">{cameraCoords.x}</span>
    </div>
    <div class="coord-row">
      <span class="coord-label y">Y</span>
      <span class="coord-value">{cameraCoords.y}</span>
    </div>
    <div class="coord-row">
      <span class="coord-label z">Z</span>
      <span class="coord-value">{cameraCoords.z}</span>
    </div>
  </div>

  <div class="control-panel" class:hidden={systemState.hideUI}>
    <div class="panel-title">{$t("digitalTwin.selectBox")}</div>
    <div class="box-list" bind:this={boxListEl}></div>
    <div class="action-buttons">
      <button id="getBoxOutBtn" bind:this={getBoxOutBtnEl} disabled
        >{$t("digitalTwin.out")}</button
      >
      <button id="putBoxInBtn" bind:this={putBoxInBtnEl} disabled
        >{$t("digitalTwin.in")}</button
      >
    </div>
  </div>

  <div class="status-label" class:hidden={systemState.hideUI}>
    <div class="status-item">
      <div class="color-blue"></div>
      <div class="status-count" bind:this={fullCountEl}>0</div>
      <div class="status-text">: {$t("digitalTwin.total")}</div>
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
    top: -34px;
    left: -29px;
    width: 830px;
    height: 100%;
    max-height: 434px;
    overflow: hidden;
  }

  #container3D {
    width: 100%;
    height: 100%;
    max-height: 530px;
  }

  .compass-ui {
    position: absolute;
    top: 10px;
    right: 10px;
    z-index: 150;
  }

  .compass-ui.hidden {
    display: none;
  }

  .gizmo-container {
    position: relative;
    width: 80px;
    height: 80px;
    display: flex;
    align-items: center;
    justify-content: center;
    top: 20px;
    right: 20px;
  }

  .gizmo-center {
    position: absolute;
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: #fff;
    border: 1px solid #ccc;
    z-index: 10;
  }

  .axis-line {
    position: absolute;
    background: #ddd;
    pointer-events: none;
    z-index: 1;
  }

  .axis-x {
    width: 100%;
    height: 1px;
    top: 50%;
    left: 0;
  }

  .axis-y {
    width: 1px;
    height: 100%;
    left: 50%;
    top: 0;
  }

  .axis-z-top,
  .axis-z-bottom {
    display: none;
  }

  .axis-btn {
    position: absolute;
    width: 24px;
    height: 24px;
    border-radius: 50%;
    border: none;
    color: #fff;
    font-size: 10px;
    font-weight: bold;
    cursor: pointer;
    z-index: 5;
  }

  .axis-btn .axis-label {
    font-weight: bold;
  }

  .axis-btn-front {
    top: 0;
    left: 50%;
    transform: translateX(-50%);
    background: #3b82f6;
  }

  .axis-btn-left {
    left: 0;
    top: 50%;
    transform: translateY(-50%);
    background: #ef4444;
  }

  .axis-btn-right {
    right: 0;
    top: 50%;
    transform: translateY(-50%);
    background: #ef4444;
  }

  .axis-btn-back {
    bottom: 0;
    left: 50%;
    transform: translateX(-50%);
    background: #3b82f6;
  }

  .camera-coords {
    position: absolute;
    top: 140px;
    right: 20px;
    background: #fff;
    padding: 8px;
    border: 1px solid #ccc;
    z-index: 150;
    font-size: 11px;
  }

  .camera-coords.hidden {
    display: none;
  }

  .coords-title {
    font-size: 10px;
    font-weight: bold;
    margin-bottom: 4px;
  }

  .coord-row {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 2px 0;
  }

  .coord-label {
    width: 16px;
    height: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 9px;
    font-weight: bold;
    color: #fff;
  }

  .coord-label.x {
    background: #ef4444;
  }

  .coord-label.y {
    background: #22c55e;
  }

  .coord-label.z {
    background: #3b82f6;
  }

  .coord-value {
    font-family: monospace;
    font-size: 11px;
  }

  .control-panel {
    position: absolute;
    top: 24px;
    left: 24px;
    background: #fff;
    padding: 10px;
    border: 1px solid #ccc;
    width: 180px;
    z-index: 100;
  }

  .control-panel.hidden {
    display: none;
  }

  .panel-title {
    font-size: 12px;
    font-weight: bold;
    margin-bottom: 8px;
    color: #333;
  }

  .box-list {
    max-height: 150px;
    overflow-y: auto;
    margin-bottom: 8px;
    border: 1px solid #ddd;
  }

  :global(.box-item) {
    padding: 6px 8px;
    cursor: pointer;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid #eee;
  }

  :global(.box-item:last-child) {
    border-bottom: none;
  }

  :global(.box-item.selected) {
    background: #333 !important;
  }

  :global(.box-item.selected .box-name) {
    color: #fff !important;
  }

  :global(.box-item.selected .box-status) {
    color: #fff !important;
  }

  :global(.box-name) {
    font-size: 11px;
    color: #333;
  }

  :global(.box-status) {
    font-size: 10px;
    padding: 2px 6px;
    font-weight: bold;
  }

  :global(.box-status.in) {
    background: #3b82f6;
    color: #fff;
  }

  :global(.box-status.out) {
    background: #ef4444;
    color: #fff;
  }

  .action-buttons {
    display: flex;
    gap: 6px;
  }

  .action-buttons button {
    flex: 1;
    padding: 6px;
    border: none;
    color: #fff;
    font-size: 11px;
    font-weight: bold;
    cursor: pointer;
  }

  .action-buttons button:disabled {
    opacity: 0.4;
    cursor: not-allowed;
  }

  #getBoxOutBtn {
    background: #ef4444;
  }

  #putBoxInBtn {
    background: #3b82f6;
  }

  .status-label {
    position: absolute;
    bottom: 24px;
    left: 24px;
    background: #fff;
    padding: 8px;
    border: 1px solid #ccc;
    z-index: 100;
  }

  .status-label.hidden {
    display: none;
  }

  .status-item {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .status-count {
    font-size: 14px;
    font-weight: bold;
    color: #333;
  }

  .color-blue {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background: #3b82f6;
  }

  .status-text {
    font-size: 12px;
    color: #333;
  }

  .toast-container {
    position: absolute;
    bottom: 60px;
    left: 10px;
    z-index: 1000;
    display: flex;
    flex-direction: column;
    gap: 6px;
  }

  :global(.toast) {
    background: #fff;
    padding: 8px 12px;
    border: 1px solid #ccc;
    font-size: 11px;
    color: #333;
  }

  :global(.toast.success) {
    border-left: 3px solid #22c55e;
  }

  :global(.toast.info) {
    border-left: 3px solid #3b82f6;
  }

  :global(.toast.removing) {
    opacity: 0;
  }
</style>

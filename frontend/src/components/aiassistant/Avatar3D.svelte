<script>
  import { onMount, onDestroy } from "svelte";
  import * as THREE from "three";
  import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";

  export let isTalking = false;

  const BASE_URL = "http://localhost:8001/static/avatar";
  const MODEL_URL = `${BASE_URL}/models/muhammad.glb`;
  const ANIM_NEUTRAL_URL = `${BASE_URL}/animations/m_neutral.glb`;
  const ANIM_TALKING_URL = `${BASE_URL}/animations/m_waiting.glb`; 

  let container;
  let scene, camera, renderer, mixer, clock;
  let model, faceMesh, headBone; // Added headBone
  let actions = {};
  let activeAction;
  let animationFrameId;
  
  // --- TALKING VARIABLES ---
  let currentMouthOpen = 0;
  let mouthTarget = 0; // The "target" openness we want to reach
  let lastMouthUpdate = 0; // Timer for changing mouth shape

  // --- BLINKING VARIABLES ---
  let isBlinking = false;
  let blinkStartTime = 0;
  let nextBlinkTime = 0;
  const BLINK_DURATION = 0.15; // Fast blink (seconds)

  // --- IDLE HEAD MOVEMENT ---
  let headNoiseOffset = Math.random() * 100;

  $: if (mixer && actions["neutral"] && actions["talking"]) {
    const toAction = isTalking ? actions["talking"] : actions["neutral"];
    if (activeAction !== toAction) {
      if (activeAction) activeAction.fadeOut(0.5);
      toAction.reset().fadeIn(0.5).play();
      activeAction = toAction;
    }
  }

  onMount(() => {
    initScene();
    loadAssets();
    animate();
    window.addEventListener("resize", onWindowResize);
  });

  onDestroy(() => {
    if (animationFrameId) cancelAnimationFrame(animationFrameId);
    window.removeEventListener("resize", onWindowResize);
    if (renderer) renderer.dispose();
  });

  function initScene() {
    clock = new THREE.Clock();
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0xffffff); 

    // Standard Camera
    camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 100);
    camera.position.set(0, 1.6, 0.8); // Close-up

    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.outputColorSpace = THREE.SRGBColorSpace; 
    container.appendChild(renderer.domElement);

    // Professional Lighting Setup (3-Point Light)
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6); // Soft fill
    scene.add(ambientLight);

    const keyLight = new THREE.DirectionalLight(0xffffff, 1.0);
    keyLight.position.set(1, 2, 2); // Top-right
    scene.add(keyLight);
    
    const rimLight = new THREE.DirectionalLight(0xffffff, 0.5);
    rimLight.position.set(-2, 2, -2); // Back-left (adds depth)
    scene.add(rimLight);
  }

  function loadAssets() {
    const loader = new GLTFLoader();

    loader.load(MODEL_URL, (gltf) => {
      model = gltf.scene;
      scene.add(model);

      // --- SEARCH FOR PARTS ---
      model.traverse((child) => {
        // 1. Find Face Mesh
        if (child.isMesh && child.morphTargetDictionary) {
             if (child.name === "Wolf3D_Head") {
                 faceMesh = child;
             }
        }
        // 2. Find Head Bone (for subtle rotation)
        if (child.isBone && (child.name === "Head" || child.name === "Neck")) {
            headBone = child;
        }
      });

      // Fallback if specific name not found
      if (!faceMesh) {
          model.traverse((child) => {
            if (child.isMesh && child.morphTargetDictionary && !faceMesh) {
                if (child.name.includes("Head")) faceMesh = child;
            }
          });
      }

      mixer = new THREE.AnimationMixer(model);
      
      loader.load(ANIM_NEUTRAL_URL, (animGltf) => {
        const clip = animGltf.animations[0];
        actions["neutral"] = mixer.clipAction(clip);
        actions["neutral"].play();
        activeAction = actions["neutral"];
      });

      loader.load(ANIM_TALKING_URL, (animGltf) => {
        const clip = animGltf.animations[0];
        actions["talking"] = mixer.clipAction(clip);
      });

    }, undefined, (err) => console.error("Error loading model:", err));
  }

  function animate() {
    animationFrameId = requestAnimationFrame(animate);
    const dt = clock.getDelta();
    const now = clock.elapsedTime;

    if (mixer) mixer.update(dt);

    if (faceMesh) {
        updateBlinking(dt);
        updateTalking(dt, now);
    }

    if (headBone) {
        updateHeadMovement(now);
    }

    renderer.render(scene, camera);
  }

  // --- 1. NATURAL BLINKING LOGIC ---
  function updateBlinking(dt) {
    // Initialize next blink time if 0
    if (nextBlinkTime === 0) nextBlinkTime = clock.elapsedTime + Math.random() * 3 + 2;

    if (isBlinking) {
        const blinkProgress = (clock.elapsedTime - blinkStartTime) / BLINK_DURATION;
        
        // Bell curve: 0 -> 1 -> 0
        let value = Math.sin(Math.PI * blinkProgress); 
        value = Math.max(0, Math.min(1, value));

        setMorph("eyeBlinkLeft", value);
        setMorph("eyeBlinkRight", value);

        if (blinkProgress >= 1) {
            isBlinking = false;
            setMorph("eyeBlinkLeft", 0);
            setMorph("eyeBlinkRight", 0);
            // Schedule next blink (random 2-5 seconds)
            nextBlinkTime = clock.elapsedTime + Math.random() * 3 + 2;
        }
    } else if (clock.elapsedTime >= nextBlinkTime) {
        isBlinking = true;
        blinkStartTime = clock.elapsedTime;
    }
  }

  // --- 2. PROFESSIONAL TALKING LOGIC ---
  function updateTalking(dt, now) {
    const jawIndex = faceMesh.morphTargetDictionary["jawOpen"];
    if (jawIndex === undefined) return;

    if (isTalking) {
        // Change target every 0.1s roughly (simulate syllables)
        if (now - lastMouthUpdate > 0.1) {
            // Pick a random open amount (0.1 to 0.7) - never fully 1.0 (too unnatural)
            // Occasionally close almost fully (0.0)
            mouthTarget = Math.random() < 0.2 ? 0 : 0.1 + Math.random() * 0.6;
            lastMouthUpdate = now;
        }
        
        // Smoothly move current jaw to target (Lerp)
        // Speed 15 gives a snappy but smooth "speaking" motion
        currentMouthOpen += (mouthTarget - currentMouthOpen) * dt * 15;
    } else {
        // Close mouth smoothly
        currentMouthOpen += (0 - currentMouthOpen) * dt * 10;
    }

    faceMesh.morphTargetInfluences[jawIndex] = currentMouthOpen;
  }

  // --- 3. SUBTLE HEAD IDLE ---
  function updateHeadMovement(now) {
    // Combine two slow sine waves to make a non-repeating "drift"
    // X rotation (Nod): very subtle
    // Y rotation (Turn): subtle
    
    // We keep the base animation's rotation and ADD our subtle noise
    // Note: This might conflict if the animation clip rotates the head a lot.
    // But usually "Neutral/Waiting" loops have stiff necks, so this helps.
    
    const noiseX = Math.sin(now * 0.5 + headNoiseOffset) * 0.05; // Up/Down drift
    const noiseY = Math.cos(now * 0.3 + headNoiseOffset) * 0.05; // Left/Right drift
    
    // We use .rotation.set (or modify directly) - be careful not to override animation completely
    // Ideally, we add to the animation result, but accessing that is hard in ThreeJS simple setup.
    // A safe way is to modulate the result slightly AFTER the mixer update (which we are doing).
    
    // Using '0.1' multiplier to keep it very subtle
    headBone.rotation.x += noiseX * 0.03; 
    headBone.rotation.y += noiseY * 0.03;
  }

  function setMorph(name, value) {
      const index = faceMesh.morphTargetDictionary[name];
      if (index !== undefined) {
          faceMesh.morphTargetInfluences[index] = value;
      }
  }

  function onWindowResize() {
    if (!container || !camera || !renderer) return;
    camera.aspect = container.clientWidth / container.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(container.clientWidth, container.clientHeight);
  }
</script>

<div class="avatar-3d-container" bind:this={container}></div>

<style>
  .avatar-3d-container {
    width: 100%;
    height: 100%;
    overflow: hidden;
    border-radius: 50%;
  }
</style>
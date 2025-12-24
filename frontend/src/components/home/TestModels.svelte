<script lang="ts">
    import { onMount } from "svelte";
    import * as THREE from "three";
    import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
    import { DRACOLoader } from "three/examples/jsm/loaders/DRACOLoader.js";
    import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";
    let container: HTMLDivElement;
    let scene: THREE.Scene;
    let camera: THREE.PerspectiveCamera;
    let renderer: THREE.WebGLRenderer;
    let controls: OrbitControls;

    // Boxes data
    const boxes = [
        { boxId: "box_1", x: 0, y: 0, position: "in" },
        { boxId: "box_2", x: 1, y: 0, position: "in" },
        { boxId: "box_3", x: 2, y: 0, position: "in" },
        { boxId: "box_4", x: 3, y: 0, position: "in" },

        { boxId: "box_5", x: 0, y: 1, position: "in" },
        { boxId: "box_6", x: 1, y: 1, position: "in" },
        { boxId: "box_7", x: 2, y: 1, position: "in" },
        { boxId: "box_8", x: 3, y: 1, position: "in" },

        { boxId: "box_9", x: 0, y: 2, position: "in" },
        { boxId: "box_10", x: 1, y: 2, position: "in" },
        { boxId: "box_11", x: 2, y: 2, position: "in" },
        { boxId: "box_12", x: 3, y: 2, position: "in" },

        { boxId: "box_13", x: 0, y: 3, position: "in" },
        { boxId: "box_14", x: 1, y: 3, position: "in" },
        { boxId: "box_15", x: 2, y: 3, position: "in" },
        { boxId: "box_16", x: 3, y: 3, position: "in" },

        { boxId: "box_17", x: 0, y: 4, position: "in" },
        { boxId: "box_18", x: 1, y: 4, position: "in" },
        { boxId: "box_19", x: 2, y: 4, position: "in" },
        { boxId: "box_20", x: 3, y: 4, position: "in" },

        { boxId: "box_21", x: 0, y: 5, position: "in" },
        { boxId: "box_22", x: 1, y: 5, position: "in" },
        { boxId: "box_23", x: 2, y: 5, position: "in" },
        { boxId: "box_24", x: 3, y: 5, position: "in" },
    ];

    // Input for crane control
    let craneBoxID = "box_1";
    let selectedAction = "moveCrane"; // "moveCrane" or "moveBox"

    // API polling interval
    let apiPollingInterval: ReturnType<typeof setInterval>;

    // Animation state tracking
    let isAnimating = false;

    // Poll for API commands
    async function pollForCommands() {
        // Skip if animation is already in progress
        if (isAnimating) return;

        try {
            const response = await fetch('/api/models/pending-command');
            const data = await response.json();

            if (data.hasCommand && data.command) {
                const { boxId, action } = data.command;
                isAnimating = true;

                const onComplete = () => {
                    isAnimating = false;
                };

                // Call the matching function with onComplete callback
                if (action === "MoveArmToBoxInitialPosition") {
                    MoveArmToBoxInitialPosition(boxId, onComplete);
                } else if (action === "moveBoxOutOfShelf") {
                    moveBoxOutOfShelf(boxId, onComplete);
                } else if (action === "moveBoxAndArmToOutput") {
                    moveBoxAndArmToOutput(boxId, onComplete);
                } else if (action === "moveBoxToOutput") {
                    moveBoxToOutput(boxId, onComplete);
                } else if (action === "MoveBoxOutOfASRS") {
                    MoveBoxOutOfASRS(boxId, onComplete);
                } else if (action === "moveBoxToInput") {
                    moveBoxToInput(boxId, onComplete);
                } else if (action === "moveBoxFromInputToArm") {
                    moveBoxFromInputToArm(boxId, onComplete);
                } else if (action === "moveArmToInput") {
                    moveArmToInput(boxId, onComplete);
                } else if (action === "moveBoxAndArmToBoxPosition") {
                    moveBoxAndArmToBoxPosition(boxId, onComplete);
                } else if (action === "putBoxOnShelf") {
                    putBoxOnShelf(boxId, onComplete);
                } else {
                    // Unknown action, reset flag
                    isAnimating = false;
                }
            }
        } catch (error) {
            console.error('API polling error:', error);
            isAnimating = false;  // Reset on error
        }
    }

    // Execute selected action
    function executeAction() {
        // Skip if animation is already in progress
        if (isAnimating) {
            console.log("Animation in progress, please wait...");
            return;
        }

        isAnimating = true;

        const onComplete = () => {
            isAnimating = false;
        };

        if (selectedAction === "moveCrane") {
            MoveArmToBoxInitialPosition(craneBoxID, onComplete);
        } else if (selectedAction === "moveBox") {
            moveBoxOutOfShelf(craneBoxID, onComplete);
        } else if (selectedAction === "moveToOutput") {
            moveBoxAndArmToOutput(craneBoxID, onComplete);
        } else if (selectedAction === "moveBoxToOutput") {
            moveBoxToOutput(craneBoxID, onComplete);
        } else if (selectedAction === "moveBoxOutOfASRS") {
            MoveBoxOutOfASRS(craneBoxID, onComplete);
        } else if (selectedAction === "moveBoxToInput") {
            moveBoxToInput(craneBoxID, onComplete);
        } else if (selectedAction === "moveBoxFromInputToArm") {
            moveBoxFromInputToArm(craneBoxID, onComplete);
        } else if (selectedAction === "moveArmToInput") {
            moveArmToInput(craneBoxID, onComplete);
        } else if (selectedAction === "moveBoxAndArmToBoxPosition") {
            moveBoxAndArmToBoxPosition(craneBoxID, onComplete);
        } else if (selectedAction === "putBoxOnShelf") {
            putBoxOnShelf(craneBoxID, onComplete);
        } else {
            isAnimating = false;
        }
    }

    // Function to get initial box position based on boxID (e.g., "box_1")
    function getInitialBoxPosition(boxID: string) {
        const box = boxes.find((b) => b.boxId === boxID);
        if (!box) {
            console.warn(`Box '${boxID}' not found`);
            return { x: 0, y: 0, z: 0 };
        }
        const x = -70.892;
        const y = 174.3234 - 38 * box.x;
        const z = 60.8608 - 21 * box.y;
        return { x, y, z };
    }

    // Animation speed (units per second)
    const CRANE_SPEED = 50;
    const BOX_SPEED = 50;

    // Output position for boxes with position = "out"
    const OUTPUT_POSITION = { x: 91, y: 49, z: 22.5 };

    // Initialization function to position all boxes based on their position attribute
    function initializeBoxPositions() {
        boxes.forEach((box) => {
            const boxObject = scene?.getObjectByName(box.boxId);

            if (!boxObject) {
                console.warn(`Box object '${box.boxId}' not found in scene`);
                return;
            }

            if (box.position === "in") {
                // Keep box at its current position (do nothing)
                console.log(`Box '${box.boxId}' position is "in" - keeping current position`);
            } else if (box.position === "out") {
                // Move box to output position
                boxObject.position.set(OUTPUT_POSITION.x, OUTPUT_POSITION.y, OUTPUT_POSITION.z);
                console.log(`Box '${box.boxId}' position is "out" - moved to output position`);
            }
        });
    }

    // Function to move box out of shelf (animate X position)
    function moveBoxOutOfShelf(boxID: string, onComplete?: () => void) {
        // Check if box is already out
        const box = boxes.find((b) => b.boxId === boxID);
        if (box && box.position === "out") {
            console.log("The box is out, I cannot move it.");
            if (onComplete) onComplete();
            return;
        }

        const initialPos = getInitialBoxPosition(boxID);
        const boxObject = scene?.getObjectByName(boxID);

        if (!boxObject) {
            console.warn(`Box object '${boxID}' not found in scene`);
            if (onComplete) onComplete();
            return;
        }

        const targetX = initialPos.x + 46.74;
        const targetY = initialPos.y;
        const targetZ = initialPos.z;

        let lastTime = performance.now();

        function animateBox() {
            const currentTime = performance.now();
            const deltaTime = (currentTime - lastTime) / 1000;
            lastTime = currentTime;

            const moveAmount = BOX_SPEED * deltaTime;

            const diffX = targetX - boxObject.position.x;

            if (Math.abs(diffX) > 0.01) {
                const moveX = Math.sign(diffX) * Math.min(moveAmount, Math.abs(diffX));
                boxObject.position.x += moveX;
                requestAnimationFrame(animateBox);
            } else {
                boxObject.position.x = targetX;
                boxObject.position.y = targetY;
                boxObject.position.z = targetZ;
                console.log(`Box '${boxID}' moved out of shelf. X: ${targetX}`);
                if (onComplete) onComplete();
            }
        }

        animateBox();
    }

    // Function to put box back on shelf (return to initial position)
    function putBoxOnShelf(boxID: string, onComplete?: () => void) {
        // Check if box is NOT out
        const box = boxes.find((b) => b.boxId === boxID);
        if (!box || box.position !== "out") {
            console.log("The box is not out, I cannot put it on the shelf.");
            if (onComplete) onComplete();
            return;
        }

        const boxObject = scene?.getObjectByName(boxID);

        if (!boxObject) {
            console.warn(`Box object '${boxID}' not found in scene`);
            if (onComplete) onComplete();
            return;
        }

        // Get the box's initial position
        const initialPos = getInitialBoxPosition(boxID);
        const targetX = initialPos.x;
        const targetY = initialPos.y;
        const targetZ = initialPos.z;

        let lastTime = performance.now();

        function animateBox() {
            const currentTime = performance.now();
            const deltaTime = (currentTime - lastTime) / 1000;
            lastTime = currentTime;

            const moveAmount = BOX_SPEED * deltaTime;
            let stillMoving = false;

            const diffX = targetX - boxObject.position.x;
            const diffY = targetY - boxObject.position.y;
            const diffZ = targetZ - boxObject.position.z;

            if (Math.abs(diffX) > 0.01) {
                const moveX = Math.sign(diffX) * Math.min(moveAmount, Math.abs(diffX));
                boxObject.position.x += moveX;
                stillMoving = true;
            } else {
                boxObject.position.x = targetX;
            }

            if (Math.abs(diffY) > 0.01) {
                const moveY = Math.sign(diffY) * Math.min(moveAmount, Math.abs(diffY));
                boxObject.position.y += moveY;
                stillMoving = true;
            } else {
                boxObject.position.y = targetY;
            }

            if (Math.abs(diffZ) > 0.01) {
                const moveZ = Math.sign(diffZ) * Math.min(moveAmount, Math.abs(diffZ));
                boxObject.position.z += moveZ;
                stillMoving = true;
            } else {
                boxObject.position.z = targetZ;
            }

            if (stillMoving) {
                requestAnimationFrame(animateBox);
            } else {
                // Update box position attribute from "out" to "in"
                box.position = "in";
                console.log(`Box '${boxID}' put back on shelf. X: ${targetX}, Y: ${targetY}, Z: ${targetZ}. Position changed to "in".`);
                if (onComplete) onComplete();
            }
        }

        animateBox();
    }

    // Function to move box out of ASRS (add 56 to current X position) with fade out
    function MoveBoxOutOfASRS(boxID: string, onComplete?: () => void) {
        // Check if box is already out
        const boxData = boxes.find((b) => b.boxId === boxID);
        if (boxData && boxData.position === "out") {
            console.log("The box is out, I cannot move it.");
            if (onComplete) onComplete();
            return;
        }

        const boxObject = scene?.getObjectByName(boxID);

        if (!boxObject) {
            console.warn(`Box object '${boxID}' not found in scene`);
            if (onComplete) onComplete();
            return;
        }

        const startX = boxObject.position.x;
        const targetX = startX + 56;
        const totalDistance = 56;

        // Clone materials to avoid affecting other boxes that share the same material
        boxObject.traverse((child) => {
            if (child instanceof THREE.Mesh && child.material) {
                if (Array.isArray(child.material)) {
                    child.material = child.material.map((mat) => {
                        const clonedMat = mat.clone();
                        clonedMat.transparent = true;
                        clonedMat.opacity = 1;
                        return clonedMat;
                    });
                } else {
                    child.material = child.material.clone();
                    child.material.transparent = true;
                    child.material.opacity = 1;
                }
            }
        });

        let lastTime = performance.now();

        function animateBox() {
            const currentTime = performance.now();
            const deltaTime = (currentTime - lastTime) / 1000;
            lastTime = currentTime;

            const moveAmount = BOX_SPEED * deltaTime;

            const diffX = targetX - boxObject.position.x;

            if (Math.abs(diffX) > 0.01) {
                const moveX = Math.sign(diffX) * Math.min(moveAmount, Math.abs(diffX));
                boxObject.position.x += moveX;

                // Calculate opacity based on progress (1 to 0)
                const progress = (boxObject.position.x - startX) / totalDistance;
                const opacity = 1 - progress;

                // Update opacity for all materials
                boxObject.traverse((child) => {
                    if (child instanceof THREE.Mesh && child.material) {
                        if (Array.isArray(child.material)) {
                            child.material.forEach((mat) => {
                                mat.opacity = Math.max(0, opacity);
                            });
                        } else {
                            child.material.opacity = Math.max(0, opacity);
                        }
                    }
                });

                requestAnimationFrame(animateBox);
            } else {
                boxObject.position.x = targetX;
                // Set final opacity to 0
                boxObject.traverse((child) => {
                    if (child instanceof THREE.Mesh && child.material) {
                        if (Array.isArray(child.material)) {
                            child.material.forEach((mat) => {
                                mat.opacity = 0;
                            });
                        } else {
                            child.material.opacity = 0;
                        }
                    }
                });
                // Update box position attribute from "in" to "out"
                const box = boxes.find((b) => b.boxId === boxID);
                if (box) {
                    box.position = "out";
                    console.log(`Box '${boxID}' position attribute changed to "out"`);
                }

                // Move box to output position
                boxObject.position.set(91, 49, 22.5);
                console.log(`Box '${boxID}' moved to output position. X: 91, Y: 49, Z: 22.5`);
                if (onComplete) onComplete();
            }
        }

        animateBox();
    }

    // Function to move box back to input (subtract 56 from X position) with fade in
    function moveBoxToInput(boxID: string, onComplete?: () => void) {
        // Check if box is NOT out
        const box = boxes.find((b) => b.boxId === boxID);
        if (!box || box.position !== "out") {
            console.log("The box is not out, I cannot move it to input.");
            if (onComplete) onComplete();
            return;
        }

        const boxObject = scene?.getObjectByName(boxID);

        if (!boxObject) {
            console.warn(`Box object '${boxID}' not found in scene`);
            if (onComplete) onComplete();
            return;
        }

        const startX = boxObject.position.x;
        const targetX = startX - 56;
        const totalDistance = 56;

        // Ensure materials are set up for transparency and start at opacity 0
        boxObject.traverse((child) => {
            if (child instanceof THREE.Mesh && child.material) {
                if (Array.isArray(child.material)) {
                    child.material = child.material.map((mat) => {
                        const clonedMat = mat.clone();
                        clonedMat.transparent = true;
                        clonedMat.opacity = 0;
                        return clonedMat;
                    });
                } else {
                    child.material = child.material.clone();
                    child.material.transparent = true;
                    child.material.opacity = 0;
                }
            }
        });

        let lastTime = performance.now();

        function animateBox() {
            const currentTime = performance.now();
            const deltaTime = (currentTime - lastTime) / 1000;
            lastTime = currentTime;

            const moveAmount = BOX_SPEED * deltaTime;

            const diffX = targetX - boxObject.position.x;

            if (Math.abs(diffX) > 0.01) {
                const moveX = Math.sign(diffX) * Math.min(moveAmount, Math.abs(diffX));
                boxObject.position.x += moveX;

                // Calculate opacity based on progress (0 to 1)
                const progress = (startX - boxObject.position.x) / totalDistance;
                const opacity = progress;

                // Update opacity for all materials
                boxObject.traverse((child) => {
                    if (child instanceof THREE.Mesh && child.material) {
                        if (Array.isArray(child.material)) {
                            child.material.forEach((mat) => {
                                mat.opacity = Math.min(1, opacity);
                            });
                        } else {
                            child.material.opacity = Math.min(1, opacity);
                        }
                    }
                });

                requestAnimationFrame(animateBox);
            } else {
                boxObject.position.x = targetX;
                // Set final opacity to 1
                boxObject.traverse((child) => {
                    if (child instanceof THREE.Mesh && child.material) {
                        if (Array.isArray(child.material)) {
                            child.material.forEach((mat) => {
                                mat.opacity = 1;
                            });
                        } else {
                            child.material.opacity = 1;
                        }
                    }
                });
                if (onComplete) onComplete();
            }
        }

        animateBox();
    }

    // Function to move box from input to arm (subtract 56 from X position)
    function moveBoxFromInputToArm(boxID: string, onComplete?: () => void) {
        // Check if box is NOT out
        const box = boxes.find((b) => b.boxId === boxID);
        if (!box || box.position !== "out") {
            console.log("The box is not out, I cannot move it.");
            if (onComplete) onComplete();
            return;
        }

        const boxObject = scene?.getObjectByName(boxID);

        if (!boxObject) {
            console.warn(`Box object '${boxID}' not found in scene`);
            if (onComplete) onComplete();
            return;
        }

        const startX = boxObject.position.x;
        const targetX = startX - 56;

        let lastTime = performance.now();

        function animateBox() {
            const currentTime = performance.now();
            const deltaTime = (currentTime - lastTime) / 1000;
            lastTime = currentTime;

            const moveAmount = BOX_SPEED * deltaTime;

            const diffX = targetX - boxObject.position.x;

            if (Math.abs(diffX) > 0.01) {
                const moveX = Math.sign(diffX) * Math.min(moveAmount, Math.abs(diffX));
                boxObject.position.x += moveX;
                requestAnimationFrame(animateBox);
            } else {
                boxObject.position.x = targetX;
                console.log(`Box '${boxID}' moved from input to arm. X: ${targetX}`);
                if (onComplete) onComplete();
            }
        }

        animateBox();
    }

    // Function to move box to output (add 55.78 to current X position)
    function moveBoxToOutput(boxID: string, onComplete?: () => void) {
        // Check if box is already out
        const box = boxes.find((b) => b.boxId === boxID);
        if (box && box.position === "out") {
            console.log("The box is out, I cannot move it.");
            if (onComplete) onComplete();
            return;
        }

        const boxObject = scene?.getObjectByName(boxID);

        if (!boxObject) {
            console.warn(`Box object '${boxID}' not found in scene`);
            if (onComplete) onComplete();
            return;
        }

        const targetX = boxObject.position.x + 55.78;

        let lastTime = performance.now();

        function animateBox() {
            const currentTime = performance.now();
            const deltaTime = (currentTime - lastTime) / 1000;
            lastTime = currentTime;

            const moveAmount = BOX_SPEED * deltaTime;

            const diffX = targetX - boxObject.position.x;

            if (Math.abs(diffX) > 0.01) {
                const moveX = Math.sign(diffX) * Math.min(moveAmount, Math.abs(diffX));
                boxObject.position.x += moveX;
                requestAnimationFrame(animateBox);
            } else {
                boxObject.position.x = targetX;
                console.log(`Box '${boxID}' moved to output. X: ${targetX}`);
                if (onComplete) onComplete();
            }
        }

        animateBox();
    }

    // Function to move crane to box initial position with animation
    function MoveArmToBoxInitialPosition(boxID: string, onComplete?: () => void) {
        // Check if box is already out
        const box = boxes.find((b) => b.boxId === boxID);
        if (box && box.position === "out") {
            console.log("The box is out, I cannot move it.");
            if (onComplete) onComplete();
            return;
        }

        const boxPos = getInitialBoxPosition(boxID);
        const crane = scene?.getObjectByName("crane");
        const crane002 = scene?.getObjectByName("crane_002");

        if (!crane && !crane002) {
            console.warn("Crane objects not found in scene");
            if (onComplete) onComplete();
            return;
        }

        const targetY = boxPos.y;
        const targetZ = boxPos.z - 9;

        let lastTime = performance.now();

        function animateCrane() {
            const currentTime = performance.now();
            const deltaTime = (currentTime - lastTime) / 1000; // Convert to seconds
            lastTime = currentTime;

            const moveAmount = CRANE_SPEED * deltaTime;
            let stillMoving = false;

            // Animate crane Y position
            if (crane) {
                const diffY = targetY - crane.position.y;
                if (Math.abs(diffY) > 0.01) {
                    const moveY = Math.sign(diffY) * Math.min(moveAmount, Math.abs(diffY));
                    crane.position.y += moveY;
                    stillMoving = true;
                } else {
                    crane.position.y = targetY;
                }
            }

            // Animate crane_002 Y and Z positions
            if (crane002) {
                const diffY = targetY - crane002.position.y;
                const diffZ = targetZ - crane002.position.z;

                if (Math.abs(diffY) > 0.01) {
                    const moveY = Math.sign(diffY) * Math.min(moveAmount, Math.abs(diffY));
                    crane002.position.y += moveY;
                    stillMoving = true;
                } else {
                    crane002.position.y = targetY;
                }

                if (Math.abs(diffZ) > 0.01) {
                    const moveZ = Math.sign(diffZ) * Math.min(moveAmount, Math.abs(diffZ));
                    crane002.position.z += moveZ;
                    stillMoving = true;
                } else {
                    crane002.position.z = targetZ;
                }
            }

            if (stillMoving) {
                requestAnimationFrame(animateCrane);
            } else {
                console.log(`Crane animation complete. Y: ${targetY}, Z: ${targetZ}`);
                if (onComplete) onComplete();
            }
        }

        animateCrane();
    }

    // Function to move box and arm back to box's initial position
    function moveBoxAndArmToBoxPosition(boxID: string, onComplete?: () => void) {
        // Check if box is NOT out
        const box = boxes.find((b) => b.boxId === boxID);
        if (!box || box.position !== "out") {
            console.log("The box is not out, I cannot move it.");
            if (onComplete) onComplete();
            return;
        }

        const boxObject = scene?.getObjectByName(boxID);
        const crane = scene?.getObjectByName("crane");
        const crane002 = scene?.getObjectByName("crane_002");

        if (!boxObject) {
            console.warn(`Box object '${boxID}' not found in scene`);
            if (onComplete) onComplete();
            return;
        }

        if (!crane && !crane002) {
            console.warn("Crane objects not found in scene");
            if (onComplete) onComplete();
            return;
        }

        // Get the box's initial position (keep X as current position)
        const boxInitialPos = getInitialBoxPosition(boxID);
        const boxTargetY = boxInitialPos.y;
        const boxTargetZ = boxInitialPos.z;

        // Crane targets based on box initial position
        const craneTargetY = boxInitialPos.y;
        const crane002TargetY = boxInitialPos.y;
        const crane002TargetZ = boxInitialPos.z - 9;

        let lastTime = performance.now();

        function animateAll() {
            const currentTime = performance.now();
            const deltaTime = (currentTime - lastTime) / 1000;
            lastTime = currentTime;

            const moveAmount = CRANE_SPEED * deltaTime;
            let stillMoving = false;

            // Animate box Y and Z positions (keep X as is)
            if (boxObject) {
                const diffY = boxTargetY - boxObject.position.y;
                const diffZ = boxTargetZ - boxObject.position.z;

                if (Math.abs(diffY) > 0.01) {
                    const moveY = Math.sign(diffY) * Math.min(moveAmount, Math.abs(diffY));
                    boxObject.position.y += moveY;
                    stillMoving = true;
                } else {
                    boxObject.position.y = boxTargetY;
                }

                if (Math.abs(diffZ) > 0.01) {
                    const moveZ = Math.sign(diffZ) * Math.min(moveAmount, Math.abs(diffZ));
                    boxObject.position.z += moveZ;
                    stillMoving = true;
                } else {
                    boxObject.position.z = boxTargetZ;
                }
            }

            // Animate crane Y position
            if (crane) {
                const diffY = craneTargetY - crane.position.y;
                if (Math.abs(diffY) > 0.01) {
                    const moveY = Math.sign(diffY) * Math.min(moveAmount, Math.abs(diffY));
                    crane.position.y += moveY;
                    stillMoving = true;
                } else {
                    crane.position.y = craneTargetY;
                }
            }

            // Animate crane_002 Y and Z positions
            if (crane002) {
                const diffY = crane002TargetY - crane002.position.y;
                const diffZ = crane002TargetZ - crane002.position.z;

                if (Math.abs(diffY) > 0.01) {
                    const moveY = Math.sign(diffY) * Math.min(moveAmount, Math.abs(diffY));
                    crane002.position.y += moveY;
                    stillMoving = true;
                } else {
                    crane002.position.y = crane002TargetY;
                }

                if (Math.abs(diffZ) > 0.01) {
                    const moveZ = Math.sign(diffZ) * Math.min(moveAmount, Math.abs(diffZ));
                    crane002.position.z += moveZ;
                    stillMoving = true;
                } else {
                    crane002.position.z = crane002TargetZ;
                }
            }

            if (stillMoving) {
                requestAnimationFrame(animateAll);
            } else {
                console.log(`Box '${boxID}' and arm moved to box initial position. Box: Y=${boxTargetY}, Z=${boxTargetZ}.`);
                if (onComplete) onComplete();
            }
        }

        animateAll();
    }

    // Function to move arm to input position (y = 49, z = 13.5)
    function moveArmToInput(boxID: string, onComplete?: () => void) {
        // Check if box is NOT out
        const box = boxes.find((b) => b.boxId === boxID);
        if (!box || box.position !== "out") {
            console.log("The box is not out, I cannot move it.");
            if (onComplete) onComplete();
            return;
        }

        const crane = scene?.getObjectByName("crane");
        const crane002 = scene?.getObjectByName("crane_002");

        if (!crane && !crane002) {
            console.warn("Crane objects not found in scene");
            if (onComplete) onComplete();
            return;
        }

        const targetY = 49;
        const targetZ = 13.5;

        let lastTime = performance.now();

        function animateCrane() {
            const currentTime = performance.now();
            const deltaTime = (currentTime - lastTime) / 1000;
            lastTime = currentTime;

            const moveAmount = CRANE_SPEED * deltaTime;
            let stillMoving = false;

            // Animate crane Y position
            if (crane) {
                const diffY = targetY - crane.position.y;
                if (Math.abs(diffY) > 0.01) {
                    const moveY = Math.sign(diffY) * Math.min(moveAmount, Math.abs(diffY));
                    crane.position.y += moveY;
                    stillMoving = true;
                } else {
                    crane.position.y = targetY;
                }
            }

            // Animate crane_002 Y and Z positions
            if (crane002) {
                const diffY = targetY - crane002.position.y;
                const diffZ = targetZ - crane002.position.z;

                if (Math.abs(diffY) > 0.01) {
                    const moveY = Math.sign(diffY) * Math.min(moveAmount, Math.abs(diffY));
                    crane002.position.y += moveY;
                    stillMoving = true;
                } else {
                    crane002.position.y = targetY;
                }

                if (Math.abs(diffZ) > 0.01) {
                    const moveZ = Math.sign(diffZ) * Math.min(moveAmount, Math.abs(diffZ));
                    crane002.position.z += moveZ;
                    stillMoving = true;
                } else {
                    crane002.position.z = targetZ;
                }
            }

            if (stillMoving) {
                requestAnimationFrame(animateCrane);
            } else {
                console.log(`Arm moved to input position. Y: ${targetY}, Z: ${targetZ}`);
                if (onComplete) onComplete();
            }
        }

        animateCrane();
    }

    // Function to move box and arm to output position simultaneously
    function moveBoxAndArmToOutput(boxID: string, onComplete?: () => void) {
        // Check if box is already out
        const box = boxes.find((b) => b.boxId === boxID);
        if (box && box.position === "out") {
            console.log("The box is out, I cannot move it.");
            if (onComplete) onComplete();
            return;
        }

        const boxObject = scene?.getObjectByName(boxID);
        const crane = scene?.getObjectByName("crane");
        const crane002 = scene?.getObjectByName("crane_002");

        if (!boxObject) {
            console.warn(`Box object '${boxID}' not found in scene`);
            if (onComplete) onComplete();
            return;
        }

        if (!crane && !crane002) {
            console.warn("Crane objects not found in scene");
            if (onComplete) onComplete();
            return;
        }

        // Target positions
        const boxTargetY = 185.5;
        const boxTargetZ = 22.5;
        const craneTargetY = 185.5;
        const crane002TargetY = 185.5;
        const crane002TargetZ = 13.5;

        let lastTime = performance.now();

        function animateAll() {
            const currentTime = performance.now();
            const deltaTime = (currentTime - lastTime) / 1000;
            lastTime = currentTime;

            const moveAmount = CRANE_SPEED * deltaTime;
            let stillMoving = false;

            // Animate box Y and Z positions
            if (boxObject) {
                const diffY = boxTargetY - boxObject.position.y;
                const diffZ = boxTargetZ - boxObject.position.z;

                if (Math.abs(diffY) > 0.01) {
                    const moveY = Math.sign(diffY) * Math.min(moveAmount, Math.abs(diffY));
                    boxObject.position.y += moveY;
                    stillMoving = true;
                } else {
                    boxObject.position.y = boxTargetY;
                }

                if (Math.abs(diffZ) > 0.01) {
                    const moveZ = Math.sign(diffZ) * Math.min(moveAmount, Math.abs(diffZ));
                    boxObject.position.z += moveZ;
                    stillMoving = true;
                } else {
                    boxObject.position.z = boxTargetZ;
                }
            }

            // Animate crane Y position
            if (crane) {
                const diffY = craneTargetY - crane.position.y;
                if (Math.abs(diffY) > 0.01) {
                    const moveY = Math.sign(diffY) * Math.min(moveAmount, Math.abs(diffY));
                    crane.position.y += moveY;
                    stillMoving = true;
                } else {
                    crane.position.y = craneTargetY;
                }
            }

            // Animate crane_002 Y and Z positions
            if (crane002) {
                const diffY = crane002TargetY - crane002.position.y;
                const diffZ = crane002TargetZ - crane002.position.z;

                if (Math.abs(diffY) > 0.01) {
                    const moveY = Math.sign(diffY) * Math.min(moveAmount, Math.abs(diffY));
                    crane002.position.y += moveY;
                    stillMoving = true;
                } else {
                    crane002.position.y = crane002TargetY;
                }

                if (Math.abs(diffZ) > 0.01) {
                    const moveZ = Math.sign(diffZ) * Math.min(moveAmount, Math.abs(diffZ));
                    crane002.position.z += moveZ;
                    stillMoving = true;
                } else {
                    crane002.position.z = crane002TargetZ;
                }
            }

            if (stillMoving) {
                requestAnimationFrame(animateAll);
            } else {
                console.log(`Box and Arm moved to output. Box Y: ${boxTargetY}, Z: ${boxTargetZ}`);
                if (onComplete) onComplete();
            }
        }

        animateAll();
    }

    function initScene() {
        scene = new THREE.Scene();

        const width = container.clientWidth || 800;
        const height = container.clientHeight || 600;

        camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 10000);
        camera.position.set(0, 0, 5); // Temporary position, will be adjusted after model loads

        renderer = new THREE.WebGLRenderer({ antialias: false, alpha: true, powerPreference: "low-power" });
        renderer.setSize(width, height);
        renderer.setPixelRatio(1);
        renderer.shadowMap.enabled = false; // No shadow calculations
        container.appendChild(renderer.domElement);

        // Lighting for PBR materials
        const ambientLight = new THREE.AmbientLight(0xffffff, 1.5);
        scene.add(ambientLight);

        const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
        directionalLight.position.set(150, 150, 150);
        scene.add(directionalLight);

        const directionalLight2 = new THREE.DirectionalLight(0xffffff, 1);
        directionalLight2.position.set(-100, -100, -100);
        scene.add(directionalLight2);

        // Controls
        controls = new OrbitControls(camera, renderer.domElement);
        controls.enableDamping = false; // Disable for better performance

        // Load model
        const dracoLoader = new DRACOLoader();
        dracoLoader.setDecoderPath("https://www.gstatic.com/draco/versioned/decoders/1.5.6/");
        const loader = new GLTFLoader();
        loader.setDRACOLoader(dracoLoader);
        loader.load(
            "/Static/Models/Box/New_4.glb",
            (gltf) => {
                const model = gltf.scene;
                scene.add(model);


                // Calculate bounding box to fit camera
                const box = new THREE.Box3().setFromObject(model);
                const center = box.getCenter(new THREE.Vector3());
                const size = box.getSize(new THREE.Vector3());

                // Get the max dimension to determine camera distance
                const maxDim = Math.max(size.x, size.y, size.z);
                const fov = camera.fov * (Math.PI / 180);
                let cameraDistance = maxDim / (2 * Math.tan(fov / 2));
                cameraDistance *= 1.5; // Add some padding

                // Position camera
                camera.position.set(
                    center.x + cameraDistance * 0.5,
                    center.y + cameraDistance * 0.3,
                    center.z + cameraDistance,
                );
                camera.lookAt(center);

                // Update controls target to model center
                controls.target.copy(center);
                controls.update();

                // Initialize box positions based on their position attribute
                initializeBoxPositions();
            },
            undefined,
            (error) => {
                console.error("Error loading model:", error);
            },
        );

        animate();
    }

    function animate() {
        requestAnimationFrame(animate);
        controls.update();
        renderer.render(scene, camera);
    }

    function handleResize() {
        if (!container || !camera || !renderer) return;
        const width = container.clientWidth;
        const height = container.clientHeight;
        camera.aspect = width / height;
        camera.updateProjectionMatrix();
        renderer.setSize(width, height);
    }

    onMount(() => {
        initScene();
        window.addEventListener("resize", handleResize);

        // Start polling for API commands every 500ms
        apiPollingInterval = setInterval(pollForCommands, 500);

        return () => {
            window.removeEventListener("resize", handleResize);
            clearInterval(apiPollingInterval);
            renderer?.dispose();
        };
    });
</script>

<div class="wrapper">
    <div class="container" bind:this={container}></div>
    <div class="crane-controls">
        <h4>Crane & Box Control</h4>
        <div class="input-group">
            <label
                >Box ID: <input
                    type="text"
                    bind:value={craneBoxID}
                    placeholder="box_1"
                /></label
            >
            <label
                >Action:
                <select bind:value={selectedAction}>
                    <option value="moveCrane">Move Crane to Box</option>
                    <option value="moveBox">Move Box Out of Shelf</option>
                    <option value="moveToOutput">Move Box & Arm to Output</option>
                    <option value="moveBoxToOutput">Move Box to Output (+55.78 X)</option>
                    <option value="moveBoxOutOfASRS">Move Box Out of ASRS (+56 X)</option>
                    <option value="moveBoxToInput">Move Box To Input (-56 X)</option>
                    <option value="moveBoxFromInputToArm">Move Box From Input To Arm (-56 X)</option>
                    <option value="moveArmToInput">Move Arm To Input (Y=49, Z=13.5)</option>
                    <option value="moveBoxAndArmToBoxPosition">Move Box & Arm To Box Position</option>
                    <option value="putBoxOnShelf">Put Box On Shelf</option>
                </select>
            </label>
        </div>
        <button on:click={executeAction}>Execute</button>
    </div>
</div>

<style>
    .wrapper {
        position: relative;
        width: 100%;
        height: 100%;
    }

    .container {
        width: 100%;
        height: 100%;
        min-height: 400px;
    }

    .input-group {
        display: flex;
        flex-direction: column;
        gap: 6px;
    }

    .input-group label {
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .input-group input {
        width: 80px;
        padding: 4px 8px;
        border: 1px solid #555;
        border-radius: 4px;
        background: #333;
        color: white;
        font-family: monospace;
    }

    .input-group select {
        padding: 4px 8px;
        border: 1px solid #555;
        border-radius: 4px;
        background: #333;
        color: white;
        font-family: monospace;
        cursor: pointer;
    }

    .crane-controls {
        position: absolute;
        top: 10px;
        right: 10px;
        background: rgba(0, 0, 0, 0.7);
        color: white;
        padding: 10px 15px;
        border-radius: 8px;
        font-family: monospace;
        font-size: 14px;
    }

    .crane-controls h4 {
        margin: 0 0 8px 0;
        color: #ffd93d;
    }

    .crane-controls button {
        margin-top: 10px;
        width: 100%;
        padding: 8px;
        background: #ffd93d;
        color: black;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-weight: bold;
    }

    .crane-controls button:hover {
        background: #f0c830;
    }
</style>
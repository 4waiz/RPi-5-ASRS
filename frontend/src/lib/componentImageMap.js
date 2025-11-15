// Component Image Mapping Configuration
// Maps ALL component names from your Excel to the 10 images you have
const componentImageModules = import.meta.glob('../assets/alertsPage/*', {
  eager: true,
  import: 'default'
});

const componentImageUrls = Object.fromEntries(
  Object.entries(componentImageModules).map(([path, url]) => {
    const segments = path.split('/');
    return [segments[segments.length - 1], url];
  })
);

function resolveImageUrl(filename) {
  return componentImageUrls[filename] || null;
}

export const componentImageMap = {
  // ======================
  // MOTORS & DRIVES (motor-driver.png, stepper-motor.png)
  // ======================
  'vfd1 belt': 'motor-driver.png',
  'vfd': 'motor-driver.png',
  'drive': 'motor-driver.png',
  'motor driver': 'motor-driver.png',
  'servo drive': 'motor-driver.png',
  'ac motor': 'stepper-motor.png',
  'dc motor': 'stepper-motor.png',
  'z axis hoist': 'stepper-motor.png',
  'z axis': 'stepper-motor.png',
  'x axis': 'stepper-motor.png',
  'y axis': 'stepper-motor.png',
  'hoist motor': 'stepper-motor.png',
  'conveyor motor': 'stepper-motor.png',
  'motor': 'stepper-motor.png',
  'servo': 'stepper-motor.png',
  'agv': 'stepper-motor.png',
  'cartesian': 'stepper-motor.png',
  
  // ======================
  // SENSORS (photoelectric-sensor.png, proximity-sensor.png, reed-switch.png)
  // ======================
  // Photoelectric sensors
  'pe1 exit box': 'photoelectric-sensor.png',
  'pe1': 'photoelectric-sensor.png',
  'photoeye': 'photoelectric-sensor.png',
  'photoelectric sensor': 'photoelectric-sensor.png',
  'bin sensor': 'photoelectric-sensor.png',
  'photo sensor': 'photoelectric-sensor.png',
  'camera1': 'photoelectric-sensor.png',
  'camera2': 'photoelectric-sensor.png',
  'camera': 'photoelectric-sensor.png',
  'vision': 'photoelectric-sensor.png',
  'barcode': 'photoelectric-sensor.png',
  'scanner': 'photoelectric-sensor.png',
  'laser': 'photoelectric-sensor.png',
  'lighting': 'photoelectric-sensor.png',
  
  // Proximity & Position sensors
  'x encoder': 'proximity-sensor.png',
  'z encoder': 'proximity-sensor.png',
  'encoder': 'proximity-sensor.png',
  'position sensor': 'proximity-sensor.png',
  'proximity sensor': 'proximity-sensor.png',
  'inductive sensor': 'proximity-sensor.png',
  'asr1 sensor': 'proximity-sensor.png',
  
  // Switches
  'limit switch': 'reed-switch.png',
  'reed switch': 'reed-switch.png',
  'magnetic switch': 'reed-switch.png',
  'door interlock': 'reed-switch.png',
  
  // ======================
  // BUTTONS & E-STOPS (push-button.png)
  // ======================
  'e-stop loop': 'push-button.png',
  'emergency stop': 'push-button.png',
  'e-stop': 'push-button.png',
  'estop': 'push-button.png',
  'button': 'push-button.png',
  'reset button': 'push-button.png',
  'push button': 'push-button.png',
  
  // ======================
  // ACTUATORS (solenoid.png)
  // ======================
  'cylinder': 'solenoid.png',
  'hydraulic cylinder': 'solenoid.png',
  'pneumatic cylinder': 'solenoid.png',
  'valve': 'solenoid.png',
  'solenoid': 'solenoid.png',
  'gripper': 'solenoid.png',
  'actuator': 'solenoid.png',
  'fil': 'solenoid.png', // From "FIL unit"
  'recipe': 'solenoid.png',
  
  // ======================
  // CONTROLLERS & COMPUTERS (raspberry-pi.png)
  // ======================
  'plc': 'raspberry-pi.png',
  'controller': 'raspberry-pi.png',
  'hmi': 'raspberry-pi.png',
  'touchscreen': 'raspberry-pi.png',
  'display': 'raspberry-pi.png',
  'wcs': 'raspberry-pi.png',
  'wms': 'raspberry-pi.png',
  'scada': 'raspberry-pi.png',
  'ptp master': 'raspberry-pi.png',
  'ethernet': 'raspberry-pi.png',
  'network': 'raspberry-pi.png',
  'system': 'raspberry-pi.png',
  'box': 'raspberry-pi.png',
  'workstation': 'raspberry-pi.png',
  
  // ======================
  // POWER & ELECTRICAL (power-supply.png, power-distribution-board.png)
  // ======================
  'power supply': 'power-supply.png',
  'ups': 'power-supply.png',
  'battery': 'power-supply.png',
  'generator': 'power-supply.png',
  'backup': 'power-supply.png',
  'dc bus': 'power-supply.png',
  
  // Distribution & Wiring
  'safety relay': 'power-distribution-board.png',
  'terminal': 'power-distribution-board.png',
  'asi bus': 'power-distribution-board.png',
  'wiring': 'power-distribution-board.png',
  'cable': 'power-distribution-board.png',
  
  // ======================
  // CONVEYORS & BELTS (motor-driver.png - best match)
  // ======================
  'belt': 'motor-driver.png',
  'conveyor': 'motor-driver.png',
  'roller': 'motor-driver.png',
  
  // ======================
  // STORAGE & MECHANICAL (use motor/controller images)
  // ======================
  'buffer ram wcs': 'raspberry-pi.png',
  'buffer': 'raspberry-pi.png',
  'bin': 'proximity-sensor.png',
  'rack': 'stepper-motor.png',
  'tray': 'stepper-motor.png',
  'pallet': 'stepper-motor.png',
  'stacker': 'stepper-motor.png',
  'shuttle': 'stepper-motor.png',
  'lift': 'stepper-motor.png',
  'storage': 'stepper-motor.png',
  'vertical lift': 'stepper-motor.png',
  'amr': 'stepper-motor.png',
  'pod': 'stepper-motor.png',
  'mast': 'stepper-motor.png',
  'telescopic': 'stepper-motor.png',
  'high bay': 'stepper-motor.png',
  
  // ======================
  // SPECIFIC EXCEL COMPONENTS
  // ======================
  'rfid': 'proximity-sensor.png',
  'tag': 'proximity-sensor.png',
  'linear rail': 'stepper-motor.png',
  'gantry': 'stepper-motor.png',
  'spreader': 'solenoid.png',
  'incline': 'motor-driver.png',
  'cross belt': 'motor-driver.png',
  'dust prone': 'photoelectric-sensor.png',
  'erp': 'raspberry-pi.png',
  'pick station': 'raspberry-pi.png',
  'new install': 'power-supply.png',
  'vacuum': 'solenoid.png',
  'transac': 'raspberry-pi.png',
  'material': 'stepper-motor.png',
  'cube': 'stepper-motor.png',
  
  // ======================
  // SAFETY (use appropriate images)
  // ======================
  'safety curtain': 'photoelectric-sensor.png',
  'light curtain': 'photoelectric-sensor.png',
  'safety': 'push-button.png',
  'door': 'reed-switch.png',
  'gate': 'reed-switch.png',
  
  // ======================
  // SUBSYSTEMS (general mapping)
  // ======================
  'qc_vision': 'photoelectric-sensor.png',
  'motion': 'stepper-motor.png',
  'cyber': 'raspberry-pi.png',
  'environmental': 'power-supply.png',
  'power': 'power-supply.png',
  'commissioning': 'raspberry-pi.png',
  'scale': 'proximity-sensor.png',
  'environment': 'power-supply.png'
};

/**
 * Get component image path based on component name
 * Uses smart matching to find the best image from your 10 available images
 */
export function getComponentImage(componentName) {
  if (!componentName) return null;
  
  const normalized = componentName.toLowerCase().trim();

  const resolveFromMap = (key) => {
    const filename = componentImageMap[key];
    return filename ? resolveImageUrl(filename) : null;
  };
  
  // 1. Try direct exact match first
  const directMatch = resolveFromMap(normalized);
  if (directMatch) {
    return directMatch;
  }
  
  // 2. Try partial word matching
  const words = normalized.split(/[\s\-_]+/);
  for (const word of words) {
    const wordMatch = resolveFromMap(word);
    if (wordMatch) {
      return wordMatch;
    }
  }
  
  // 3. Try substring matching (component name contains key or vice versa)
  for (const [key, value] of Object.entries(componentImageMap)) {
    if (normalized.includes(key) || key.includes(normalized)) {
      const fuzzyMatch = resolveImageUrl(value);
      if (fuzzyMatch) {
        return fuzzyMatch;
      }
    }
  }
  
  // 4. Smart fallback based on common patterns
  if (normalized.includes('motor') || normalized.includes('drive') || normalized.includes('axis')) {
    const motorImage = resolveImageUrl('stepper-motor.png');
    if (motorImage) return motorImage;
  }
  if (normalized.includes('sensor') || normalized.includes('camera') || normalized.includes('vision')) {
    const sensorImage = resolveImageUrl('photoelectric-sensor.png');
    if (sensorImage) return sensorImage;
  }
  if (normalized.includes('power') || normalized.includes('supply') || normalized.includes('ups')) {
    const powerImage = resolveImageUrl('power-supply.png');
    if (powerImage) return powerImage;
  }
  if (normalized.includes('plc') || normalized.includes('controller') || normalized.includes('hmi') || normalized.includes('wcs')) {
    const controllerImage = resolveImageUrl('raspberry-pi.png');
    if (controllerImage) return controllerImage;
  }
  if (normalized.includes('button') || normalized.includes('stop') || normalized.includes('switch')) {
    const buttonImage = resolveImageUrl('push-button.png');
    if (buttonImage) return buttonImage;
  }
  
  // 5. No match found - return null (component will handle this gracefully)
  return null;
}

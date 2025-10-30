import conveyorRealFallback from "../assets/inverntory/Conveyor_Unit _1.png?url";
import conveyorPartialFallback from "../assets/inverntory/Partial.svg?url";
import conveyorEmptyFallback from "../assets/inverntory/Empty.svg?url";
import stepperImg from "../assets/inverntory/Stepper Motor 57x56mm.png?url";
import proximityImg from "../assets/inverntory/Proximity Sensor.png?url";
import jetsonImg from "../assets/inverntory/Jetson Orin Nano.png?url";
import dcImg from "../assets/inverntory/Greartisan DC 24V.png?url";

const inventoryImages = import.meta.glob("../assets/inverntory/*.png", {
  eager: true,
  query: "?url",
  import: "default",
});

const resolveUnitImage = (fileName, fallback) =>
  inventoryImages[`../assets/inverntory/${fileName}`] ?? fallback;

// Static catalog that defines the dashboard layout. Hardware names, images,
// and ordering live here so the UI renders even when the backend is offline.
export const units = [
  {
    id: "CV1",
    name: "Conveyor_Unit _1",
    image: resolveUnitImage("CV1.png", conveyorRealFallback),
    subcomponents: [
      {
        id: "SM1",
        name: "Stepper Motor 57x56mm",
        image: stepperImg,
        defaultStatus: "Unknown",
      },
      {
        id: "PS1",
        name: "Proximity Sensor",
        image: proximityImg,
        defaultStatus: "Unknown",
      },
      {
        id: "PS2",
        name: "Proximity Sensor",
        image: proximityImg,
        defaultStatus: "Unknown",
      },
      {
        id: "JO1",
        name: "Jetson Orin Nano",
        image: jetsonImg,
        defaultStatus: "Unknown",
      },
      {
        id: "GD1",
        name: "Greartisan DC 24V",
        image: dcImg,
        defaultStatus: "Unknown",
      },
    ],
  },
  {
    id: "CV1B",
    name: "Conveyor_Unit _1",
    image: resolveUnitImage("CV1B.png", conveyorPartialFallback),
    subcomponents: [
      {
        id: "SM2",
        name: "Stepper Motor 57x56mm",
        image: stepperImg,
        defaultStatus: "Unknown",
      },
      {
        id: "GD2",
        name: "Greartisan DC 24V",
        image: dcImg,
        defaultStatus: "Unknown",
      },
      {
        id: "PS3",
        name: "Proximity Sensor",
        image: proximityImg,
        defaultStatus: "Unknown",
      },
    ],
  },
  {
    id: "CV2",
    name: "Conveyor_Unit _2",
    image: resolveUnitImage("CV2.png", conveyorEmptyFallback),
    subcomponents: [
      {
        id: "SM3",
        name: "Stepper Motor 57x56mm",
        image: stepperImg,
        defaultStatus: "Unknown",
      },
      {
        id: "PS4",
        name: "Proximity Sensor",
        image: proximityImg,
        defaultStatus: "Unknown",
      },
    ],
  },
];

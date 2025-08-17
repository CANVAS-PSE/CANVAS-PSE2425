import {
  HeaderInspectorComponent,
  InspectorComponent,
  MultiFieldInspectorComponent,
  SelectFieldInspectorComponent,
  SingleFieldInspectorComponent,
} from "inspectorComponents";
import * as THREE from "three";
import { Vector3, Object3D } from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { UndoRedoHandler } from "undoRedoHandler";
import {
  UpdateHeliostatCommand,
  UpdateLightsourceCommand,
  UpdateReceiverCommand,
} from "updateCommands";
import {
  DuplicateHeliostatCommand,
  DuplicateReceiverCommand,
  DuplicateLightSourceCommand,
} from "duplicateCommands";
import {
  DeleteHeliostatCommand,
  DeleteLightSourceCommand,
  DeleteReceiverCommand,
} from "deleteCommands";

/**
 * Represents a Object in CANVAS
 */
export class CanvasObject extends Object3D {
  #objectName;

  /**
   * Creates a new selectable object
   * @param {string} name the name of the object
   */
  constructor(name) {
    super();
    this.#objectName = name;
  }

  /**
   * Get the name of the object
   * @returns {string} the name of the object
   */
  get objectName() {
    return this.#objectName;
  }

  /**
   * Set the name of the object
   */
  set objectName(name) {
    this.#objectName = name;
  }

  /**
   * Get a list of inspector components used for this object
   * @abstract
   * @throws {Error}  Throws an error if the method is not implemented in subclasses.
   * @returns {InspectorComponent[]} an array of the inspector components
   */
  get inspectorComponents() {
    throw new Error("This method must be implemented in all subclasses");
  }

  /**
   * Updates and saves the new name through a command
   * @param {string} name the new name you want to save and update
   */
  // eslint-disable-next-line no-unused-vars -- required for interface compatibility
  updateAndSaveObjectName(name) {
    throw new Error("This method must be implemented in all subclasses");
  }

  /**
   * Updates and saves the new position through a command
   * @param {Vector3} position - the new position you want to save and update
   */
  // eslint-disable-next-line no-unused-vars -- required for interface compatibility
  updateAndSaveObjectPosition(position) {
    throw new Error("This method must be implemented in all subclasses");
  }

  /**
   * Updates and saves the new rotation through a command
   * @param {THREE.Quaternion} rotation - the new rotation you want to save and update
   */
  // eslint-disable-next-line no-unused-vars -- required for interface compatibility
  updateAndSaveObjectRotation(rotation) {
    throw new Error("This method must be implemented in all subclasses");
  }

  /**
   * Duplicates the object
   */
  duplicate() {
    throw new Error("This method must be implemented in all subclasses");
  }
  /**
   * Deletes the object
   */
  delete() {
    throw new Error("This method must be implemented in all subclasses");
  }

  /**
   * Updates the position of the object
   * @param {THREE.Vector3} position - the new position of the object
   */
  // eslint-disable-next-line no-unused-vars -- required for interface compatibility
  updatePosition(position) {
    throw new Error("This method must be implemented in all subclasses");
  }

  /**
   * Updates the rotation of the object
   * @param {THREE.Quaternion} rotation - the new rotation of the object
   */
  // eslint-disable-next-line no-unused-vars -- required for interface compatibility
  updateRotation(rotation) {
    throw new Error("This method must be implemented in all subclasses");
  }

  /**
   * Returns the axis on which the object is rotatable
   * @abstract
   * @throws {Error} - Throws an error if the method is not implemented in subclasses.
   * @returns {string[]} array containing all reotable axis.
   */
  get rotatableAxis() {
    throw new Error("This method must be implemented in all subclasses");
  }

  /**
   * Returns whether the object is movable or not
   * @abstract
   * @throws {Error} - Throws an error if the method is not implemented in subclasses.
   * @returns {boolean} wether the object is movable
   */
  get isMovable() {
    throw new Error("This method must be implemented in all subclasses");
  }

  /**
   * Returns whether an object is selectable or not
   * @abstract
   * @throws {Error} - Throws an error if the method is not implemented in subclasses.
   * @returns {boolean} wether the object is selectable
   */
  get isSelectable() {
    throw new Error("This method must be implemented in all subclasses");
  }

  /**
   * Returns the old position of the heliostat
   * @abstract
   * @throws {Error} - Throws an error if the method is not implemented in subclasses.
   * @returns {THREE.Vector3} the old position of the object
   */
  get currentPosition() {
    throw new Error("This method must be implemented in all subclasses");
  }
}

/**
 * Class that represents the Heliostat object
 */
export class Heliostat extends CanvasObject {
  #apiID;
  #headerComponent;
  #positionComponent;
  #undoRedoHandler = UndoRedoHandler.getInstance();
  #isMovable = true;
  /**
   * @type { string[] }
   */
  #rotatableAxis = null;
  #currentPosition;

  /**
   * Creates a Heliostat object
   * @param {string} heliostatName the name of the heliostat
   * @param {THREE.Vector3} position The position of the heliostat.
   * @param {number} [apiID] The id for api usage
   */
  constructor(heliostatName, position, apiID = null) {
    super(heliostatName);
    this.loader = new GLTFLoader();
    this.loader.load("/static/models/heliostat.glb", (gltf) => {
      this.mesh = gltf.scene;
      this.mesh.traverse((child) => {
        if (child.isMesh) {
          child.castShadow = true;
        }
      });
      this.add(this.mesh);
    });
    this.position.copy(position);
    this.#currentPosition = new Vector3(position.x, position.y, position.z);
    this.#apiID = apiID;

    // create components for inspector
    this.#headerComponent = new HeaderInspectorComponent(
      () =>
        this.objectName !== "" && this.objectName
          ? this.objectName
          : "Heliostat",
      (name) => this.updateAndSaveObjectName(name),
      this,
    );

    const nCoordinate = new SingleFieldInspectorComponent(
      "N",
      "number",
      () => this.position.x,
      (newValue) => {
        this.#undoRedoHandler.executeCommand(
          new UpdateHeliostatCommand(
            this,
            "position",
            new Vector3(newValue, this.position.y, this.position.z),
          ),
        );
      },
      -Infinity,
    );

    const uCoordinate = new SingleFieldInspectorComponent(
      "U",
      "number",
      () => this.position.y,
      (newValue) => {
        this.#undoRedoHandler.executeCommand(
          new UpdateHeliostatCommand(
            this,
            "position",
            new Vector3(this.position.x, newValue, this.position.z),
          ),
        );
      },
      0,
    );

    const eCoordinate = new SingleFieldInspectorComponent(
      "E",
      "number",
      () => this.position.z,
      (newValue) => {
        this.#undoRedoHandler.executeCommand(
          new UpdateHeliostatCommand(
            this,
            "position",
            new Vector3(this.position.x, this.position.y, newValue),
          ),
        );
      },
      -Infinity,
    );

    this.#positionComponent = new MultiFieldInspectorComponent("Position", [
      nCoordinate,
      uCoordinate,
      eCoordinate,
    ]);
  }

  /**
   * Get an array containing all rotatable axis
   * @returns {string[]} containing all rotatable axis
   */
  get rotatableAxis() {
    return this.#rotatableAxis;
  }

  /**
   * Get wether the object is selectable
   * @returns {boolean} wether the object is selectable
   */
  get isSelectable() {
    return true;
  }

  /**
   * Get wether the object is movable
   * @returns {boolean} wether the object is movable
   */
  get isMovable() {
    return this.#isMovable;
  }

  /**
   * Get the current position of the object
   * @returns {THREE.Vector3} the positon of the object
   */
  get currentPosition() {
    return this.#currentPosition;
  }

  /**
   * Updates the position of the heliostat
   * @param {THREE.Vector3} position the new position
   */
  updatePosition(position) {
    this.position.copy(position);
    this.#currentPosition = new Vector3(position.x, position.y, position.z);
  }

  /**
   * Update and save the name of the object
   * @param {string} name the new name for the object
   */
  updateAndSaveObjectName(name) {
    this.#undoRedoHandler.executeCommand(
      new UpdateHeliostatCommand(this, "heliostatName", name),
    );
  }

  /**
   * Duplicate the object
   */
  duplicate() {
    this.#undoRedoHandler.executeCommand(new DuplicateHeliostatCommand(this));
  }

  /**
   * Delete the object
   */
  delete() {
    this.#undoRedoHandler.executeCommand(new DeleteHeliostatCommand(this));
  }

  /**
   * Updates the position of the heliostat
   * @param {Vector3} position - the new position of the heliostat
   */
  updateAndSaveObjectPosition(position) {
    this.#undoRedoHandler.executeCommand(
      new UpdateHeliostatCommand(this, "position", position),
    );
  }
  /**
   * Get the api id used for this object
   * @returns {number} the api id
   */
  get apiID() {
    return this.#apiID;
  }

  /**
   * Set the api id used for this object
   */
  set apiID(value) {
    this.#apiID = value;
  }

  /**
   * Get an array of all inspectorComponents for this object
   * @returns {InspectorComponent[]} array of inspectorComponents
   */
  get inspectorComponents() {
    return [this.#headerComponent, this.#positionComponent];
  }
}

/**
 * Class that represents the receiver object
 */
export class Receiver extends CanvasObject {
  #apiID;
  #towerType;
  #normalVector;
  #planeE;
  #planeU;
  #resolutionE;
  #resolutionU;
  #curvatureE;
  #curvatureU;
  #undoRedoHandler = UndoRedoHandler.getInstance();

  #top;
  #base;

  #headerComponent;
  #positionComponent;
  #normalVectorComponent;
  #towerTypeComponent;
  #curvatureComponent;
  #planeComponent;
  #resolutionComponent;
  #isMovable = true;
  #rotatableAxis = ["Y"];
  #currentPosition;

  /**
   * Creates a Receiver object
   * @param {string} receiverName the name of the receiver
   * @param {THREE.Vector3} position Is the position of the receiver
   * @param {THREE.Vector3} normalVector the normal vector of the receiver
   * @param {string} towerType the type of the tower
   * @param {number} planeE the plane E of the receiver
   * @param {number} planeU the plane U of the receiver
   * @param {number} resolutionE the resolution E of the receiver
   * @param {number} resolutionU the resolution U of the receiver
   * @param {number} curvatureE the curvature E of the receiver
   * @param {number} curvatureU the curvature U of the receiver
   * @param {number} [apiID] The id for api usage
   */
  constructor(
    receiverName,
    position,
    normalVector,
    towerType,
    planeE,
    planeU,
    resolutionE,
    resolutionU,
    curvatureE,
    curvatureU,
    apiID = null,
  ) {
    super(receiverName);
    // place the 3D object
    this.#base = new ReceiverBase();
    this.add(this.#base);

    this.#top = new ReceiverTop();
    this.add(this.#top);

    this.updatePosition(position);

    this.#apiID = apiID;
    this.#towerType = towerType;
    this.#normalVector = normalVector;
    this.#planeE = planeE;
    this.#planeU = planeU;
    this.#resolutionE = resolutionE;
    this.#resolutionU = resolutionU;
    this.#curvatureE = curvatureE;
    this.#curvatureU = curvatureU;
    this.#currentPosition = new Vector3(position.x, position.y, position.z);

    // create components for the inspector
    this.#headerComponent = new HeaderInspectorComponent(
      () =>
        this.objectName !== "" && this.objectName
          ? this.objectName
          : "Receiver",
      (name) => this.updateAndSaveObjectName(name),
      this,
    );

    const nCoordinate = new SingleFieldInspectorComponent(
      "N",
      "number",
      () => this.currentPosition.x,
      (newValue) => {
        this.#undoRedoHandler.executeCommand(
          new UpdateReceiverCommand(
            this,
            "position",
            new Vector3(newValue, this.position.y, this.position.z),
          ),
        );
      },
      -Infinity,
    );

    const uCoordinate = new SingleFieldInspectorComponent(
      "U",
      "number",
      () => this.currentPosition.y,
      (newValue) => {
        this.#undoRedoHandler.executeCommand(
          new UpdateReceiverCommand(
            this,
            "position",
            new Vector3(this.position.x, newValue, this.position.z),
          ),
        );
      },
      0,
    );

    const eCoordinate = new SingleFieldInspectorComponent(
      "E",
      "number",
      () => this.currentPosition.z,
      (newValue) => {
        this.#undoRedoHandler.executeCommand(
          new UpdateReceiverCommand(
            this,
            "position",
            new Vector3(this.position.x, this.position.y, newValue),
          ),
        );
      },
      -Infinity,
    );

    this.#positionComponent = new MultiFieldInspectorComponent("Position", [
      nCoordinate,
      uCoordinate,
      eCoordinate,
    ]);

    const nNormalVector = new SingleFieldInspectorComponent(
      "N",
      "number",
      () => this.#normalVector.x,
      (newValue) => {
        this.#undoRedoHandler.executeCommand(
          new UpdateReceiverCommand(
            this,
            "normalVector",
            new Vector3(newValue, this.#normalVector.y, this.#normalVector.z),
          ),
        );
      },
      -Infinity,
    );

    const uNormalVector = new SingleFieldInspectorComponent(
      "U",
      "number",
      () => this.#normalVector.y,
      (newValue) => {
        this.#undoRedoHandler.executeCommand(
          new UpdateReceiverCommand(
            this,
            "normalVector",
            new Vector3(this.#normalVector.x, newValue, this.#normalVector.z),
          ),
        );
      },
      -Infinity,
    );

    const eNormalVector = new SingleFieldInspectorComponent(
      "E",
      "number",
      () => this.#normalVector.z,
      (newValue) => {
        this.#undoRedoHandler.executeCommand(
          new UpdateReceiverCommand(
            this,
            "normalVector",
            new Vector3(this.#normalVector.x, this.#normalVector.y, newValue),
          ),
        );
      },
      -Infinity,
    );

    this.#normalVectorComponent = new MultiFieldInspectorComponent(
      "Normal Vector",
      [nNormalVector, uNormalVector, eNormalVector],
    );

    this.#towerTypeComponent = new SelectFieldInspectorComponent(
      "Type",
      [{ label: "planar", value: "planar" }],
      () => this.#towerType,
      (newValue) => {
        this.#undoRedoHandler.executeCommand(
          new UpdateReceiverCommand(this, "towerType", newValue),
        );
      },
    );

    const eCurvature = new SingleFieldInspectorComponent(
      "E",
      "number",
      () => this.#curvatureE,
      (newValue) => {
        this.#undoRedoHandler.executeCommand(
          new UpdateReceiverCommand(this, "curvatureE", newValue),
        );
      },
      -Infinity,
    );

    const uCurvature = new SingleFieldInspectorComponent(
      "U",
      "number",
      () => this.#curvatureU,
      (newValue) => {
        this.#undoRedoHandler.executeCommand(
          new UpdateReceiverCommand(this, "curvatureU", newValue),
        );
      },
      -Infinity,
    );

    this.#curvatureComponent = new MultiFieldInspectorComponent("Curvature", [
      eCurvature,
      uCurvature,
    ]);

    const ePlane = new SingleFieldInspectorComponent(
      "E",
      "number",
      () => this.#planeE,
      (newValue) => {
        this.#undoRedoHandler.executeCommand(
          new UpdateReceiverCommand(this, "planeE", newValue),
        );
      },
      -Infinity,
    );

    const uPlane = new SingleFieldInspectorComponent(
      "U",
      "number",
      () => this.#planeU,
      (newValue) => {
        this.#undoRedoHandler.executeCommand(
          new UpdateReceiverCommand(this, "planeU", newValue),
        );
      },
      -Infinity,
    );

    this.#planeComponent = new MultiFieldInspectorComponent("Plane", [
      ePlane,
      uPlane,
    ]);

    const eResolution = new SingleFieldInspectorComponent(
      "E",
      "number",
      () => this.#resolutionE,
      (newValue) => {
        this.#undoRedoHandler.executeCommand(
          new UpdateReceiverCommand(this, "resolutionE", newValue),
        );
      },
      -Infinity,
    );

    const uResolution = new SingleFieldInspectorComponent(
      "U",
      "number",
      () => this.#resolutionU,
      (newValue) => {
        this.#undoRedoHandler.executeCommand(
          new UpdateReceiverCommand(this, "resolutionU", newValue),
        );
      },
      -Infinity,
    );

    this.#resolutionComponent = new MultiFieldInspectorComponent("Resolution", [
      eResolution,
      uResolution,
    ]);
  }

  /**
   * Set the position of the base to the desired height
   * @param {number} y the desired height
   */
  setBaseHeight(y) {
    this.#base.position.y = y;
  }

  /**
   * Get all rotable axis
   * @returns {string[]} containing all rotable axis
   */
  get rotatableAxis() {
    return this.#rotatableAxis;
  }

  /**
   * Get wether the object is movable or notjh
   * @returns {boolean} wether the object is movable
   */
  get isMovable() {
    return this.#isMovable;
  }

  /**
   * Get wether the object is selectable
   * @returns {boolean} wether the object is selectable
   */
  get isSelectable() {
    return true;
  }

  /**
   * Get the current position of the object
   * @returns {THREE.Vector3} the current position
   */
  get currentPosition() {
    return this.#currentPosition;
  }

  /**
   * Updates the position of the receiver
   * @param {Vector3} position - the new position of the receiver
   */
  updateAndSaveObjectPosition(position) {
    this.#undoRedoHandler.executeCommand(
      new UpdateReceiverCommand(this, "position", position),
    );
  }

  /**
   * Updates the receiver’s position by adjusting both the base and the top, ensuring that the base remains on the ground.
   * @param {THREE.Vector3} position the new position of the receiver
   */
  updatePosition(position) {
    this.position.copy(position);
    this.#currentPosition = new Vector3(position.x, position.y, position.z);
    this.#base.position.y = -position.y;
  }

  /**
   * Update and save the name of the object
   * @param {string} name the new name
   */
  updateAndSaveObjectName(name) {
    this.#undoRedoHandler.executeCommand(
      new UpdateReceiverCommand(this, "receiverName", name),
    );
  }

  /**
   * Deletes the receiver
   */
  delete() {
    this.#undoRedoHandler.executeCommand(new DeleteReceiverCommand(this));
  }

  /**
   * Duplicates the receiver
   */
  duplicate() {
    this.#undoRedoHandler.executeCommand(new DuplicateReceiverCommand(this));
  }

  /**
   * Get the api Id used for this object
   * @returns {number} the api id
   */
  get apiID() {
    return this.#apiID;
  }

  /**
   * Set the api id of the object
   */
  set apiID(value) {
    this.#apiID = value;
  }

  /**
   * Get the type of the receiver
   * @returns {string} the type of the receiver
   */
  get towerType() {
    return this.#towerType;
  }

  /**
   * Set the type of the receiver
   */
  set towerType(value) {
    this.#towerType = value;
  }

  /**
   * Get the normal vector of the target area
   * @returns {THREE.Vector3} the normal vector
   */
  get normalVector() {
    return this.#normalVector;
  }

  /**
   * Set the normal vector of the target area
   */
  set normalVector(value) {
    this.#normalVector = value;
  }

  /**
   * Get the size of the target areay in east direction
   * @returns {number} the size
   */
  get planeE() {
    return this.#planeE;
  }

  /**
   * Set the size of the target areay in east direction
   */
  set planeE(value) {
    this.#planeE = value;
  }

  /**
   * Get the size of the target areay in up direction
   * @returns {number} the size
   */
  get planeU() {
    return this.#planeU;
  }

  /**
   * Set the size of the target areay in east direction
   */
  set planeU(value) {
    this.#planeU = value;
  }

  /**
   * Get the resoultion of the target area in east direction
   * @returns {number} the resolution
   */
  get resolutionE() {
    return this.#resolutionE;
  }

  /**
   * Set the resoultion of the target area in east direction
   */
  set resolutionE(value) {
    this.#resolutionE = value;
  }

  /**
   * Get the resoultion of the target area in up direction
   * @returns {number} the resolution
   */
  get resolutionU() {
    return this.#resolutionU;
  }

  /**
   * Set the resoultion of the target area in up direction
   */
  set resolutionU(value) {
    this.#resolutionU = value;
  }

  /**
   * Get the curvature of the target area in east direction
   * @returns {number} the curvature
   */
  get curvatureE() {
    return this.#curvatureE;
  }

  /**
   * Set the curvature of the target area in east direction
   */
  set curvatureE(value) {
    this.#curvatureE = value;
  }

  /**
   * Get the curvature of the target area in up direction
   * @returns {number} the curvature
   */
  get curvatureU() {
    return this.#curvatureU;
  }

  /**
   * Set the curvature of the target area in east direction
   */
  set curvatureU(value) {
    this.#curvatureU = value;
  }

  /**
   * Get the inspectorComponents used for this object
   * @returns {InspectorComponent[]} array of the inspectorComponents used
   */
  get inspectorComponents() {
    return [
      this.#headerComponent,
      this.#positionComponent,
      this.#normalVectorComponent,
      this.#towerTypeComponent,
      this.#curvatureComponent,
      this.#planeComponent,
      this.#resolutionComponent,
    ];
  }
}

/**
 * Class that builds the base of the receiver
 */
export class ReceiverBase extends Object3D {
  /**
   * Create the receiver base
   */
  constructor() {
    super();
    this.loader = new GLTFLoader();
    this.loader.load("/static/models/towerBase.glb", (gltf) => {
      this.base = gltf.scene;
      this.add(this.base);
      this.base.traverse((child) => {
        if (child.type == "Mesh") {
          child.castShadow = true;
        }
      });
    });
  }
}

/**
 * Class that builds the top of the receiver
 */
export class ReceiverTop extends Object3D {
  /**
   * Create the top of the receiver
   */
  constructor() {
    super();
    this.loader = new GLTFLoader();
    this.loader.load("/static/models/towerTop.glb", (gltf) => {
      this.top = gltf.scene;
      this.add(this.top);
      this.top.traverse((child) => {
        if (child.type == "Mesh") {
          child.castShadow = true;
        }
      });
    });
  }
}

/**
 * Class that represents the light source object
 */
export class LightSource extends CanvasObject {
  #apiID;
  #numberOfRays;
  #lightSourceType;
  #distributionType;
  #distributionMean;
  #distributionCovariance;

  #header;
  #numberOfRaysComponent;
  #lightsourceTypeComponent;
  #distributionTypeComponent;
  #distributionMeanComponent;
  #distributionCovarianceComponent;

  #undoRedoHandler = UndoRedoHandler.getInstance();
  #isMovable = false;
  #rotatableAxis = null;

  /**
   * Create the light source object
   * @param {string} lightSourceName the name of the lightsource
   * @param {number} numberOfRays the number of rays the light source has
   * @param {string} lightSourceType the type of the light source
   * @param {string} distributionType the type of the distribution
   * @param {number} distributionMean the mean of the distribution
   * @param {number} distributionCovariance the covariance of the distribution
   * @param {number} [apiID] the id for api usage
   */
  constructor(
    lightSourceName,
    numberOfRays,
    lightSourceType,
    distributionType,
    distributionMean,
    distributionCovariance,
    apiID = null,
  ) {
    super(lightSourceName);
    this.#apiID = apiID;
    this.#numberOfRays = numberOfRays;
    this.#lightSourceType = lightSourceType;
    this.#distributionType = distributionType;
    this.#distributionMean = distributionMean;
    this.#distributionCovariance = distributionCovariance;

    this.#header = new HeaderInspectorComponent(
      () =>
        this.objectName !== "" && this.objectName
          ? this.objectName
          : "Light source",
      (newValue) => this.updateAndSaveObjectName(newValue),
      this,
    );

    this.#numberOfRaysComponent = new SingleFieldInspectorComponent(
      "Number of rays",
      "number",
      () => this.#numberOfRays,
      (newValue) => {
        this.#undoRedoHandler.executeCommand(
          new UpdateLightsourceCommand(this, "numberOfRays", newValue),
        );
      },
      -Infinity,
    );

    this.#lightsourceTypeComponent = new SelectFieldInspectorComponent(
      "Lightsource Type",
      [{ label: "sun", value: "sun" }],
      () => this.#lightSourceType,
      (newValue) => {
        this.#undoRedoHandler.executeCommand(
          new UpdateLightsourceCommand(this, "lightSourceType", newValue),
        );
      },
    );

    this.#distributionTypeComponent = new SelectFieldInspectorComponent(
      "Distribution Type",
      [{ label: "normal", value: "normal" }],
      () => this.#distributionType,
      (newValue) => {
        this.#undoRedoHandler.executeCommand(
          new UpdateLightsourceCommand(this, "distributionType", newValue),
        );
      },
    );

    this.#distributionMeanComponent = new SingleFieldInspectorComponent(
      "Mean",
      "number",
      () => this.#distributionMean,
      (newValue) => {
        this.#undoRedoHandler.executeCommand(
          new UpdateLightsourceCommand(this, "distributionMean", newValue),
        );
      },
      -Infinity,
    );

    this.#distributionCovarianceComponent = new SingleFieldInspectorComponent(
      "Covariance",
      "number",
      () => this.#distributionCovariance,
      (newValue) => {
        this.#undoRedoHandler.executeCommand(
          new UpdateLightsourceCommand(
            this,
            "distributionCovariance",
            newValue,
          ),
        );
      },
      -Infinity,
    );
  }

  /**
   * Returns whether the lightsource is rotatable or not
   * @returns {string[]} false, as the lightsource is not rotatable
   */
  get rotatableAxis() {
    return this.#rotatableAxis;
  }

  /**
   * Returns whether the lightsource is movable or not
   * @returns {boolean} false, as the lightsource is movable
   */
  get isMovable() {
    return this.#isMovable;
  }

  /**
   * Get wether the object is selectable
   * @returns {boolean} if the object is selectable
   */
  get isSelectable() {
    return false;
  }

  /**
   * Update and save the name of the object
   * @param {string} name the new name
   */
  updateAndSaveObjectName(name) {
    this.#undoRedoHandler.executeCommand(
      new UpdateLightsourceCommand(this, "lightSourceName", name),
    );
  }

  /**
   * Duplicate the object
   */
  duplicate() {
    this.#undoRedoHandler.executeCommand(new DuplicateLightSourceCommand(this));
  }
  /**
   * Delete the object
   */
  delete() {
    this.#undoRedoHandler.executeCommand(new DeleteLightSourceCommand(this));
  }

  /**
   * Get the api ID used for this object
   * @returns {number} the api id
   */
  get apiID() {
    return this.#apiID;
  }

  /**
   * Set the api id of the object
   */
  set apiID(id) {
    this.#apiID = id;
  }

  /**
   * Get the number of rays for this light source
   * @returns {number} the number of rays
   */
  get numberOfRays() {
    return this.#numberOfRays;
  }

  /**
   * Set the number of rays the light source uses
   */
  set numberOfRays(number) {
    this.#numberOfRays = number;
  }

  /**
   * Get the type of the light source
   * @returns {string} the type of the light source
   */
  get lightSourceType() {
    return this.#lightSourceType;
  }

  /**
   * Set the type of the light source
   */
  set lightSourceType(type) {
    this.#lightSourceType = type;
  }

  /**
   * Get the distributionType of the light source
   * @returns {string} the distributionType
   */
  get distributionType() {
    return this.#distributionType;
  }

  /**
   * Set the distributionType of the light source
   */
  set distributionType(type) {
    this.#distributionType = type;
  }

  /**
   * Get the distributionMean of the light source
   * @returns {number} the distributionMean
   */
  get distributionMean() {
    return this.#distributionMean;
  }

  /**
   * Set the distributionMean of the light source
   */
  set distributionMean(number) {
    this.#distributionMean = number;
  }

  /**
   * Get the distributionCovariance of the light source
   * @returns {number} the distributionCovariance
   */
  get distributionCovariance() {
    return this.#distributionCovariance;
  }

  /**
   * Set the distributionCovariance of the light source
   */
  set distributionCovariance(number) {
    this.#distributionCovariance = number;
  }

  /**
   * Get an array of all inspectorComponents used for this object
   * @returns {InspectorComponent[]} array of all inspectorComponents
   */
  get inspectorComponents() {
    return [
      this.#header,
      this.#numberOfRaysComponent,
      this.#lightsourceTypeComponent,
      this.#distributionTypeComponent,
      this.#distributionMeanComponent,
      this.#distributionCovarianceComponent,
    ];
  }
}

/**
 * Creates the terrain for the scene
 */
export class Terrain extends Object3D {
  /**
   * Creates a new terrain.
   * @param {number} size the size of the terrain.
   */
  constructor(size) {
    super();

    this.terrain = new THREE.Mesh(
      new THREE.CircleGeometry(size / 2),
      new THREE.MeshStandardMaterial({
        color: 0x5fd159,
      }),
    );
    this.terrain.receiveShadow = true;
    this.terrain.rotateX((3 * Math.PI) / 2);
    this.add(this.terrain);

    this.mountains = new THREE.Group();
    this.add(this.mountains);
    for (let i = 0; i < 100; i++) {
      const sphere = new THREE.Mesh(
        new THREE.SphereGeometry(THREE.MathUtils.randFloat(20, 100)),
        new THREE.MeshStandardMaterial({
          color: 0x50ba78,
        }),
      );
      sphere.position.set(
        (size / 2) * Math.sin((i / 100) * 2 * Math.PI),
        0,
        (size / 2) * Math.cos((i / 100) * 2 * Math.PI),
      );
      this.mountains.add(sphere);
    }
  }
}

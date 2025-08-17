import {
  HeaderInspectorComponent,
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
 *
 */
export class SelectableObject extends Object3D {
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
   *
   */
  get objectName() {
    return this.#objectName;
  }

  /**
   *
   */
  set objectName(name) {
    this.#objectName = name;
  }

  /**
   * @throws {Error} - Throws an error if the method is not implemented in subclasses.
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
   * @throws {Error} - Throws an error if the method is not implemented in subclasses.
   */
  get rotatableAxis() {
    throw new Error("This method must be implemented in all subclasses");
  }

  /**
   * Returns whether the object is movable or not
   * @throws {Error} - Throws an error if the method is not implemented in subclasses.
   */
  get isMovable() {
    throw new Error("This method must be implemented in all subclasses");
  }

  /**
   * Returns whether an object is selectable or not
   * @throws {Error} - Throws an error if the method is not implemented in subclasses.
   */
  get isSelectable() {
    throw new Error("This method must be implemented in all subclasses");
  }

  /**
   * Returns the old position of the heliostat
   * @throws {Error} - Throws an error if the method is not implemented in subclasses.
   */
  get oldPosition() {
    throw new Error("This method must be implemented in all subclasses");
  }
}

/**
 * Class that represents the Heliostat object
 */
export class Heliostat extends SelectableObject {
  #apiID;
  #headerComponent;
  #positionComponent;
  #undoRedoHandler = UndoRedoHandler.getInstance();
  #isMovable = true;
  /**
   * @type { string[] }
   */
  #rotatableAxis = null;
  #oldPosition;

  /**
   * Creates a Heliostat object
   * @param {number} [apiID=null] The id for api usage
   * @param {string} heliostatName the name of the heliostat
   * @param {THREE.Vector3} position The position of the heliostat.
   */

  /**
   *
   * @param heliostatName
   * @param position
   * @param apiID
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
    this.#oldPosition = new Vector3(position.x, position.y, position.z);
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
   *
   */
  get rotatableAxis() {
    return this.#rotatableAxis;
  }

  /**
   *
   */
  get isSelectable() {
    return true;
  }

  /**
   *
   */
  get isMovable() {
    return this.#isMovable;
  }

  /**
   *
   */
  get oldPosition() {
    return this.#oldPosition;
  }

  /**
   * Updates the position of the heliostat
   * @param {THREE.Vector3} position the new position
   */
  updatePosition(position) {
    this.position.copy(position);
    this.#oldPosition = new Vector3(position.x, position.y, position.z);
  }

  /**
   * @param {string} name the new name for the object
   */
  updateAndSaveObjectName(name) {
    this.#undoRedoHandler.executeCommand(
      new UpdateHeliostatCommand(this, "objectName", name),
    );
  }

  /**
   *
   */
  duplicate() {
    this.#undoRedoHandler.executeCommand(new DuplicateHeliostatCommand(this));
  }

  /**
   *
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
   *
   */
  get apiID() {
    return this.#apiID;
  }

  /**
   *
   */
  set apiID(value) {
    this.#apiID = value;
  }
  /**
   *
   */
  get inspectorComponents() {
    return [this.#headerComponent, this.#positionComponent];
  }
}

/**
 * Class that represents the receiver object
 */
export class Receiver extends SelectableObject {
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
  #oldPosition;

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
      () => this.getPosition().x,
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
      () => this.getPosition().y,
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
      () => this.getPosition().z,
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
   *
   * @param y
   */
  lockPositionY(y) {
    this.#base.position.y = y;
  }

  /**
   *
   */
  get rotatableAxis() {
    return this.#rotatableAxis;
  }

  /**
   *
   */
  get isMovable() {
    return this.#isMovable;
  }

  /**
   *
   */
  get isSelectable() {
    return true;
  }

  /**
   *
   */
  get oldPosition() {
    return this.#oldPosition;
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
    this.#oldPosition = new Vector3(position.x, position.y, position.z);
    this.#base.position.y = -position.y;
  }

  /**
   *
   */
  getPosition() {
    return this.position;
  }

  /**
   * @param {string} name the new name
   */
  updateAndSaveObjectName(name) {
    this.#undoRedoHandler.executeCommand(
      new UpdateReceiverCommand(this, "objectName", name),
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
   *
   */
  get apiID() {
    return this.#apiID;
  }

  /**
   *
   */
  set apiID(value) {
    this.#apiID = value;
  }

  /**
   *
   */
  get towerType() {
    return this.#towerType;
  }

  /**
   *
   */
  set towerType(value) {
    this.#towerType = value;
  }

  /**
   *
   */
  get normalVector() {
    return this.#normalVector;
  }

  /**
   *
   */
  set normalVector(value) {
    this.#normalVector = value;
  }

  /**
   *
   */
  get planeE() {
    return this.#planeE;
  }

  /**
   *
   */
  set planeE(value) {
    this.#planeE = value;
  }

  /**
   *
   */
  get planeU() {
    return this.#planeU;
  }

  /**
   *
   */
  set planeU(value) {
    this.#planeU = value;
  }

  /**
   *
   */
  get resolutionE() {
    return this.#resolutionE;
  }

  /**
   *
   */
  set resolutionE(value) {
    this.#resolutionE = value;
  }

  /**
   *
   */
  get resolutionU() {
    return this.#resolutionU;
  }

  /**
   *
   */
  set resolutionU(value) {
    this.#resolutionU = value;
  }

  /**
   *
   */
  get curvatureE() {
    return this.#curvatureE;
  }

  /**
   *
   */
  set curvatureE(value) {
    this.#curvatureE = value;
  }

  /**
   *
   */
  get curvatureU() {
    return this.#curvatureU;
  }

  /**
   *
   */
  set curvatureU(value) {
    this.#curvatureU = value;
  }

  /**
   *
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
   *
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
   *
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
export class LightSource extends SelectableObject {
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
   * @param {string} lightsourceName the name of the lightsource
   * @param {number} numberOfRays the number of rays the light source has
   * @param {string} lightSourceType the type of the light source
   * @param {string} distributionType the type of the distribution
   * @param {number} distributionMean the mean of the distribution
   * @param {number} distributionCovariance the covariance of the distribution
   * @param {number} [apiID] the id for api usage
   */
  constructor(
    lightsourceName,
    numberOfRays,
    lightSourceType,
    distributionType,
    distributionMean,
    distributionCovariance,
    apiID = null,
  ) {
    super(lightsourceName);
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
   *
   */
  get isSelectable() {
    return false;
  }

  /**
   * @param {string} name the new name
   */
  updateAndSaveObjectName(name) {
    this.#undoRedoHandler.executeCommand(
      new UpdateLightsourceCommand(this, "objectName", name),
    );
  }

  /**
   *
   */
  duplicate() {
    this.#undoRedoHandler.executeCommand(new DuplicateLightSourceCommand(this));
  }
  /**
   *
   */
  delete() {
    this.#undoRedoHandler.executeCommand(new DeleteLightSourceCommand(this));
  }

  /**
   *
   */
  get apiID() {
    return this.#apiID;
  }

  /**
   *
   */
  set apiID(id) {
    this.#apiID = id;
  }

  /**
   *
   */
  get numberOfRays() {
    return this.#numberOfRays;
  }

  /**
   *
   */
  set numberOfRays(number) {
    this.#numberOfRays = number;
  }

  /**
   *
   */
  get lightSourceType() {
    return this.#lightSourceType;
  }

  /**
   *
   */
  set lightSourceType(type) {
    this.#lightSourceType = type;
  }

  /**
   *
   */
  get distributionType() {
    return this.#distributionType;
  }

  /**
   *
   */
  set distributionType(type) {
    this.#distributionType = type;
  }

  /**
   *
   */
  get distributionMean() {
    return this.#distributionMean;
  }

  /**
   *
   */
  set distributionMean(number) {
    this.#distributionMean = number;
  }

  /**
   *
   */
  get distributionCovariance() {
    return this.#distributionCovariance;
  }

  /**
   *
   */
  set distributionCovariance(number) {
    this.#distributionCovariance = number;
  }

  /**
   *
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

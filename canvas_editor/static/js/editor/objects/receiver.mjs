import { CanvasObject, loadGltf } from "canvasObject";
import { DeleteReceiverCommand } from "deleteCommands";
import { DuplicateReceiverCommand } from "duplicateCommands";
import {
  HeaderInspectorComponent,
  SingleFieldInspectorComponent,
  MultiFieldInspectorComponent,
  SelectFieldInspectorComponent,
  InspectorComponent,
} from "inspectorComponents";
import { Object3D, Vector3 } from "three";
import { UndoRedoHandler } from "undoRedoHandler";
import { UpdateReceiverCommand } from "updateCommands";
import * as THREE from "three";

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
  #rotatableAxis = null;
  #lastPosition;

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
    this.#lastPosition = new Vector3(position.x, position.y, position.z);

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
      () => this.lastPosition.x,
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
      () => this.lastPosition.y,
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
      () => this.lastPosition.z,
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
  get lastPosition() {
    return this.#lastPosition;
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
    this.#lastPosition = new Vector3(position.x, position.y, position.z);
    this.#base.position.y = -position.y;
  }

  /**
   * Update and save the name of the object
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
    loadGltf("/static/models/towerBase.glb", this, true);
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
    loadGltf("/static/models/towerTop.glb", this, true);
  }
}

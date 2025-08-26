import { CanvasObject } from "canvasObject";
import { DeleteLightSourceCommand } from "deleteCommands";
import { DuplicateLightSourceCommand } from "duplicateCommands";
import {
  HeaderInspectorComponent,
  SingleFieldInspectorComponent,
  SelectFieldInspectorComponent,
  InspectorComponent,
} from "inspectorComponents";
import { UndoRedoHandler } from "undoRedoHandler";
import { UpdateLightsourceCommand } from "updateCommands";

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
      new UpdateLightsourceCommand(this, "objectName", name),
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

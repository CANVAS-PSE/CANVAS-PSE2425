import { Command } from "command";
import { SelectableObject } from "objects";

/**
 * This class is designed for operations that target multiple 'SelectableObject' instances.
 * It serves as a base class for commands that modify multiple objects in the scene.
 */
export class BulkObjectCommand extends Command {
  /**
   * An array of objects on which the command operates.
   * @type {Array<SelectableObject>}
   */
  #objects;

  /**
   * Initializes a new BulkObjectCommand with the specified 'SelectableObject' instances.
   * @param {Array<SelectableObject>} objects - The 'SelectableObject' instances that this command will target.
   */
  constructor(objects) {
    super();
    this.#objects = objects;
    if (new.target === BulkObjectCommand) {
      throw new Error(
        "Cannot instantiate abstract class BulkObjectCommand directly"
      );
    }
  }
  /**
   * Getter for the objects property.
   * Temporary getter to avoid ESLint warnings for unused private field.
   * Will be used properly in future subclasses.
   * @returns {Array<SelectableObject>} - Returns the array of 'SelectableObject' instances that this command operates on.
   */
  getObjects() {
    return this.#objects;
  }
}

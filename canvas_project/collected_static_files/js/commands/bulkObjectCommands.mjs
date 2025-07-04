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
  #objects; // eslint-disable-line no-unused-private-class-members -- required for future implementations

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
}

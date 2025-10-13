import { ICommand } from "./ICommand.mjs";

/**
 * Implements undo redo functionality for property changes.
 * @template {{}} T
 * @template {Exclude<keyof T, Function>} K
 */
export class PropertyCommand extends ICommand {
  #target;
  #key;
  #oldValue;
  #newValue;

  /**
   * Create a new command instance.
   * @param {T} target the target of the command.
   * @param {K} key the key of the property you want to change.
   * @param {T[K]} newValue the new value for the property.
   */
  constructor(target, key, newValue) {
    super();
    this.#target = target;
    this.#key = key;
    this.#oldValue = target[key];
    this.#newValue = newValue;
  }

  /**
   * Executes the command, setting the property to the new value.
   */
  execute() {
    Reflect.set(this.#target, this.#key, this.#newValue);
  }

  /**
   * Undoes the command, reverting the property to its old value.
   */
  undo() {
    Reflect.set(this.#target, this.#key, this.#oldValue);
  }
}

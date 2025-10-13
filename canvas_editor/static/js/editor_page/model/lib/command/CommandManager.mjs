import { Observable } from "../Observable.mjs";

/**
 * @import {ICommand} from './commands/ICommand.mjs'
 */

/**
 * @typedef {object} CommandManagerProps
 * @property {boolean} canUndo whether the command manager is able to undo any commands.
 * @property {boolean} canRedo whether the command manager is able to redo any commands.
 */

/**
 * Manager to manage all given commands.
 *
 * Provides undo and redo functionality.
 * @augments {Observable<CommandManagerProps, undefined>}
 */
export class CommandManager extends Observable {
  static MAX_COMMANDS = 100;

  /** @type {ICommand[]} */
  #redoStack = [];
  /** @type {ICommand[]} */
  #undoStack = [];

  canUndo = false;
  canRedo = false;

  /**
   * Create a new CommandManager instance.
   */
  constructor() {
    super();
  }

  /**
   * Execute the given command and add it to the undo stack.
   * @param {ICommand} command the command you want to execute.
   */
  execute(command) {
    command.execute();
    this.#undoStack.push(command);

    if (this.#undoStack.length > CommandManager.MAX_COMMANDS) {
      this.#undoStack.shift();
    }

    this.#redoStack = [];

    this.canUndo = true;
    this.canRedo = false;
  }

  /**
   * Undo the last executed command and move it to the redo stack.
   */
  undo() {
    const command = this.#undoStack.pop();
    if (!command) return;
    command.undo();
    this.#redoStack.push(command);
    if (this.#redoStack.length > CommandManager.MAX_COMMANDS) {
      this.#redoStack.shift();
    }

    this.canUndo = this.#undoStack.length > 0;
    this.canRedo = this.#redoStack.length > 0;
  }

  /**
   * Redo the last undone command and move it back to the undo stack.
   */
  redo() {
    const command = this.#redoStack.pop();
    if (!command) return;
    command.execute();
    this.#undoStack.push(command);
    if (this.#undoStack.length > CommandManager.MAX_COMMANDS) {
      this.#undoStack.shift();
    }

    this.canUndo = this.#undoStack.length > 0;
    this.canRedo = this.#redoStack.length > 0;
  }
}

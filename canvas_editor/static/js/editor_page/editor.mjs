import { CommandManager } from "./model/lib/command/CommandManager.mjs";
import { PropertyCommand } from "./model/lib/command/commands/PropertyCommand.mjs";
import { Observable } from "./model/lib/Observable.mjs";

/**
 * @typedef {object} TestProps
 * @property {string} name f
 */

/**
 * @typedef {"testSignal"} TestSignalsNames
 */

/**
 * test 2 2
 * @augments {Observable<TestProps, TestSignalsNames>}
 */
export class Test extends Observable {
  name;

  /** test */
  constructor() {
    super();
    this.name = "test";
  }

  /** test */
  fight() {
    this.notify("testSignal");
  }
}

/** test */
export class Editor {
  test;

  /** test */
  constructor() {
    document.getElementById("loadingScreen").classList.add("d-none");
    this.test = new Test();

    this.test.subscribe("name", (name) => console.log(name));
    this.test.connect("testSignal", () => console.log("signal"));

    this.test.name = "Paul";
    this.test.fight();

    const command = new PropertyCommand(this.test, "name", "test");
    const manager = new CommandManager();

    manager.subscribe("canUndo", (canUndo) =>
      console.log("canUndo: " + canUndo),
    );
    manager.execute(command);
  }
}

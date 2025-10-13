import { CommandManager } from "./lib/command/CommandManager.mjs";
import { PropertyCommand } from "./lib/command/commands/PropertyCommand.mjs";
import { Observable } from "./lib/Observable.mjs";

/**
 * @typedef {object} TestProps
 * @property {string} name f
 */

/**
 * @typedef {"testSignal"} TestSignalsNames
 */

/**
 * te
 * @augments {Observable<TestProps, TestSignalsNames>}
 */
export class Test extends Observable {
  name;

  constructor() {
    super();
    this.name = "test";
  }

  fight() {
    this.notify("testSignal");
  }
}

export class Editor {
  test;

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

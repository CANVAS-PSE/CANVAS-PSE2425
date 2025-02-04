import { Editor } from "editor";
import { Heliostat, LightSource, Receiver, SelectableObject } from "objects";
import { SingleObjectCommand } from "singleObjectCommands";
import { ItemCreatedEvent } from "createCommands";

export class ItemDeletedEvent extends CustomEvent {
    /**
     * Creates a new item deleted event
     * @param {SelectableObject} item the item that was deleted
     */
    constructor(item) {
        super("itemDeleted", { detail: { item: item } });
    }
}

/**
 * Command to handle the deletion of a heliostat.
 */
export class DeleteHeliostatCommand extends SingleObjectCommand {
    #editor = new Editor();
    #heliostat;

    /**
     * Creates an new delete command
     * @param {Heliostat} heliostat the heliostat you want to delete
     */
    constructor(heliostat) {
        super();
        this.#heliostat = heliostat;
    }

    execute() {
        this.#editor.deleteHeliostat(this.#heliostat);

        document
            .getElementById("canvas")
            .dispatchEvent(new ItemDeletedEvent(this.#heliostat));
    }

    undo() {
        this.#editor.addHeliostat(this.#heliostat);

        document
            .getElementById("canvas")
            .dispatchEvent(new ItemCreatedEvent(this.#heliostat));
    }
}

/**
 * Command to handle the deletion of a receiver.
 */
export class DeleteReceiverCommand extends SingleObjectCommand {
    #editor = new Editor();
    #receiver;

    /**
     * Creates an new delete command
     * @param {Receiver} receiver the receiver you want to delete
     */
    constructor(receiver) {
        super();
        this.#receiver = receiver;
    }

    execute() {
        this.#editor.deleteReceiver(this.#receiver);

        document
            .getElementById("canvas")
            .dispatchEvent(new ItemDeletedEvent(this.#receiver));
    }

    undo() {
        this.#editor.addReceiver(this.#receiver);

        document
            .getElementById("canvas")
            .dispatchEvent(new ItemCreatedEvent(this.#receiver));
    }
}

/**
 * Command to handle the deletion of a lightsource.
 */
export class DeleteLightSourceCommand extends SingleObjectCommand {
    #editor = new Editor();
    #lightsource;

    /**
     * Creates an new delete command
     * @param {LightSource} lightsource the lightsource you want to delete
     */
    constructor(lightsource) {
        super();
        this.#lightsource = lightsource;
    }

    execute() {
        this.#editor.deleteLightsource(this.#lightsource);

        document
            .getElementById("canvas")
            .dispatchEvent(new ItemDeletedEvent(this.#lightsource));
    }

    undo() {
        this.#editor.addLightsource(this.#lightsource);

        document
            .getElementById("canvas")
            .dispatchEvent(new ItemCreatedEvent(this.#lightsource));
    }
}

import { Editor } from "editor";
import { Heliostat, LightSource, Receiver } from "objects";
import { SingleObjectCommand } from "singleObjectCommands";
import { ItemCreatedEvent } from "createCommands";
import { ItemDeletedEvent } from "deleteCommands";
import * as THREE from "three";

/**
 * Command to duplicate a heliostat.
 */
export class DuplicateHeliostatCommand extends SingleObjectCommand {
    #editor = new Editor();
    #heliostat;
    #heliostatCopy;
    #newPosition;

    /**
     * Create the command
     * @param {Heliostat} heliostat the heliostat you want to duplicate
     */
    constructor(heliostat) {
        super();
        this.#heliostat = heliostat;
        this.#newPosition = this.#heliostat.position.clone();
        this.#newPosition.add(new THREE.Vector3(0, 0, -3));
        this.#heliostatCopy = new Heliostat(
            this.#heliostat.objectName == "" || !this.#heliostat.objectName
                ? "Heliostat_Copy"
                : this.#heliostat.objectName + "_Copy",
            this.#newPosition,
            this.#heliostat.aimPoint,
            this.#heliostat.numberOfFacets,
            this.#heliostat.kinematicType
        );

        document.dispatchEvent(new ItemCreatedEvent(this.#heliostatCopy));
    }

    async execute() {
        await this.#editor.addHeliostat(this.#heliostatCopy);

        document
            .getElementById("canvas")
            .dispatchEvent(new ItemCreatedEvent(this.#heliostatCopy));
    }

    undo() {
        this.#editor.deleteHeliostat(this.#heliostatCopy);

        document
            .getElementById("canvas")
            .dispatchEvent(new ItemDeletedEvent(this.#heliostatCopy));
    }
}

/**
 * Command to duplicate a receiver.
 */
export class DuplicateReceiverCommand extends SingleObjectCommand {
    #editor = new Editor();
    #receiver;
    #receiverCopy;
    #newPosition;

    /**
     * Create the command
     * @param {Receiver} receiver the receiver you want to duplicate
     */
    constructor(receiver) {
        super();
        this.#receiver = receiver;
        this.#newPosition = this.#receiver.getPosition().clone();
        this.#newPosition.add(new THREE.Vector3(0, 0, -35));
        this.#receiverCopy = new Receiver(
            this.#receiver.objectName == "" || !this.#receiver.objectName
                ? "Receiver_Copy"
                : this.#receiver.objectName + "_Copy",
            this.#newPosition,
            this.#receiver.quaternionToYDegree(this.#receiver.oldQuaternion),
            this.#receiver.normalVector,
            this.#receiver.towerType,
            this.#receiver.planeE,
            this.#receiver.planeU,
            this.#receiver.resolutionE,
            this.#receiver.resolutionU,
            this.#receiver.curvatureE,
            this.#receiver.curvatureU
        );

        document.dispatchEvent(new ItemCreatedEvent(this.#receiverCopy));
    }

    async execute() {
        await this.#editor.addReceiver(this.#receiverCopy);

        document
            .getElementById("canvas")
            .dispatchEvent(new ItemCreatedEvent(this.#receiverCopy));
    }

    undo() {
        this.#editor.deleteReceiver(this.#receiverCopy);

        document
            .getElementById("canvas")
            .dispatchEvent(new ItemDeletedEvent(this.#receiverCopy));
    }
}

/**
 * Command to duplicate a lightsource.
 */
export class DuplicateLightSourceCommand extends SingleObjectCommand {
    #editor = new Editor();
    #lightsource;
    #lightsourceCopy;

    /**
     * Create the command
     * @param {LightSource} lightsource the lightsource you want to duplicate
     */
    constructor(lightsource) {
        super();
        this.#lightsource = lightsource;
        this.#lightsourceCopy = new LightSource(
            this.#lightsource.objectName == "" || !this.#lightsource.objectName
                ? "lightsource_Copy"
                : this.#lightsource.objectName + "_Copy",
            this.#lightsource.numberOfRays,
            this.#lightsource.lightSourceType,
            this.#lightsource.distributionType,
            this.#lightsource.distributionMean,
            this.#lightsource.distributionCovariance
        );

        document.dispatchEvent(new ItemCreatedEvent(this.#lightsourceCopy));
    }

    async execute() {
        await this.#editor.addLightsource(this.#lightsourceCopy);

        document
            .getElementById("canvas")
            .dispatchEvent(new ItemCreatedEvent(this.#lightsourceCopy));
    }

    undo() {
        this.#editor.deleteLightsource(this.#lightsourceCopy);

        document
            .getElementById("canvas")
            .dispatchEvent(new ItemDeletedEvent(this.#lightsourceCopy));
    }
}

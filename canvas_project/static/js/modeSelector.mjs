import { Mode, Picker } from "picker";
import * as bootstrap from "bootstrap";

/**
 * Class to handle the mode of the picker
 */
export class ModeSelector {
    /** @type {"none" | "rotate" | "move"} */
    #mode = Mode.NONE;
    #picker;

    /**
     * Creates a new mode selector
     * @param {Picker} picker the picker in use for this scene
     */
    constructor(picker) {
        this.#picker = picker;
        this.#addEventListenersModeSelection();
    }

    #addEventListenersModeSelection() {
        //initialize the mode selection buttons
        const modeSelectionButton = document.getElementById("modeSelect");
        const modeMoveButton = document.getElementById("modeMove");
        const modeRotateButton = document.getElementById("modeRotate");

        //add event listeners to the mode selection buttons
        modeSelectionButton.addEventListener("click", () => {
            this.#picker.setMode(Mode.NONE);
        });
        modeMoveButton.addEventListener("click", () => {
            this.#picker.setMode(Mode.MOVE);
        });
        modeRotateButton.addEventListener("click", () => {
            this.#picker.setMode(Mode.ROTATE);
        });

        //add event listener for the keyboard shortcut to change the mode and show the corresponding tab
        window.addEventListener("keydown", (event) => {
            if (
                (event.ctrlKey || event.metaKey) &&
                event.key.toLowerCase() === "m"
            ) {
                event.preventDefault();
                //calculate the next mode
                const modesArray = [Mode.NONE, Mode.MOVE, Mode.ROTATE];
                let currentModeIndex = modesArray.indexOf(this.#mode);
                currentModeIndex = (currentModeIndex + 1) % modesArray.length;
                this.#mode = modesArray[currentModeIndex];
                this.#picker.setMode(this.#mode);

                if (this.#mode === Mode.NONE) {
                    const tabInstance = new bootstrap.Tab(modeSelectionButton);
                    tabInstance.show();
                } else if (this.#mode === Mode.MOVE) {
                    const tabMoveInstance = new bootstrap.Tab(modeMoveButton);
                    tabMoveInstance.show();
                } else if (this.#mode === Mode.ROTATE) {
                    const tabRotateInstance = new bootstrap.Tab(
                        modeRotateButton
                    );
                    tabRotateInstance.show();
                }
            }
        });
    }
}

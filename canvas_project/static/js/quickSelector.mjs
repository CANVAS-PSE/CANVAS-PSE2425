import { ObjectManager } from "objectManager";

export class QuickSelector {
    #objectManager;
    #createHeliostatButton;
    #createReceiverButton;
    #createLightSourceButton;

    /**
     *
     * @param {ObjectManager} objectManager
     */
    constructor(objectManager) {
        this.#objectManager = objectManager;

        this.#addEventlisteners();
    }

    /**
     * Method to add event listeners to the buttons on the Quick Settings bar on the bottom of the page.
     */
    #addEventlisteners() {
        // Buttons on the bottom bar
        this.#createHeliostatButton = document.getElementById(
            "quickSettingsHeliostat"
        );
        this.#createReceiverButton = document.getElementById(
            "quickSettingsReceiver"
        );
        this.#createLightSourceButton = this.#createLightSourceButton =
            document.getElementById("quickSettingsLightsource");
        // Event listeners for the buttons on the bottom bar
        this.#createHeliostatButton.addEventListener("click", () => {
            this.#objectManager.createHeliostat();
        });
        this.#createReceiverButton.addEventListener("click", () => {
            this.#objectManager.createReceiver();
        });
        this.#createLightSourceButton.addEventListener("click", () => {
            this.#objectManager.createLightSource();
        });
    }
}

import { ObjectManager } from "objectManager";

export class Navbar {
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

        this.#setupFullscreen();
        this.#setUpObjectPlacement();
        this.#setupFileOptions();
    }

    #setupFullscreen() {
        let fullscreen = document.getElementById("fullscreen");

        // Safari
        if (navigator.userAgent.indexOf("Safari") > -1) {
            fullscreen.onclick = (_) => {
                if (document.webkitFullscreenElement === null) {
                    document.documentElement.webkitRequestFullscreen();
                } else if (document.webkitExitFullscreen) {
                    document.webkitExitFullscreen();
                }
            };
            return;
        }

        fullscreen.onclick = (_) => {
            if (document.fullscreenElement === null) {
                _ = document.documentElement.requestFullscreen();
            } else if (document.exitFullscreen) {
                _ = document.exitFullscreen();
            }
        };
    }

    #setupFileOptions() {
        let createNewProject = document.getElementById("createNewProject");

        // ensure that the form is reset when the modal is closed
        createNewProject.addEventListener("hidden.bs.modal", function () {
            var form = createNewProject.querySelector("form");
            form.reset();
        });
    }

    /**
     * Method to add event listeners to the buttons on the Navbar
     */
    #setUpObjectPlacement() {
        // Buttons on the bottom bar
        this.#createHeliostatButton = document.getElementById(
            "add-heliostat-nav-bar"
        );
        this.#createReceiverButton = document.getElementById(
            "add-receiver-nav-bar"
        );
        this.#createLightSourceButton = document.getElementById(
            "add-lightSource-nav-bar"
        );

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

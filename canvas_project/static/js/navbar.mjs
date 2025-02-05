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
        let createNewProject = document.getElementById('createNewProject');
        let importButton = document.getElementById('import');
        let exportButton = document.getElementById('export');

        const fileInput = document.createElement('input');
        fileInput.type = 'file';
        // only allows h5 files
        fileInput.accept = '.h5'; 
        fileInput.style.display = 'none';
        document.body.appendChild(fileInput);

        // ensure that the form is reset when the modal is closed
        createNewProject.addEventListener('hidden.bs.modal', function () {
            var form = createNewProject.querySelector('form');
            form.reset();
        });


        importButton.onclick = (_) => {};

        importButton.onclick = (_) => {
            fileInput.click();
        }

        fileInput.onchange = (event) => {
            const file = event.target.files[0];
            if (file) {
                console.log("Ausgewählte Datei:", file.name);
                // TODO: open file as new project
            }
        }

        exportButton.onclick = (_) => {
        }

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
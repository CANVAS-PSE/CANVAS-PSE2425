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
    this.#setUpKeybindings();
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

    function resetModalForm() {
      var form = createNewProject.querySelector("form");
      form.reset();
    }

    // ensure that the form is reset when the modal is closed
    createNewProject.addEventListener("hidden.bs.modal", function () {
      resetModalForm();
    });

    window.addEventListener("load", resetModalForm);
  }

  /**
   * Method to add event listeners to the buttons on the Navbar
   */
  #setUpObjectPlacement() {
    // Buttons on the bottom bar
    this.#createHeliostatButton = document.getElementById(
      "add-heliostat-nav-bar",
    );
    this.#createReceiverButton = document.getElementById(
      "add-receiver-nav-bar",
    );
    this.#createLightSourceButton = document.getElementById(
      "add-lightSource-nav-bar",
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

  #setUpKeybindings() {
    const select = document.getElementById("clientSelect");
    const content = document.getElementById("clientContent");
    const modal = document.getElementById("keyboardModal");

    function resetModalForm() {
      var form = modal.querySelector("form");
      select.value = "";
      content.innerHTML = "";
    }

    window.addEventListener("load", resetModalForm);

    select.addEventListener("change", () => {
      if (select.value === "mac") {
        content.innerHTML = document.getElementById("macKeybindings").innerHTML;
      } else if (select.value === "other") {
        content.innerHTML =
          document.getElementById("windowsKeybindings").innerHTML;
      } else {
        content.innerHTML = "";
      }
    });
  }
}

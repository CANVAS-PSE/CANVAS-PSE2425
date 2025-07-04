import * as THREE from "three";

/**
 * Handles the genertion of project previews of the editor page
 */
export class PreviewHandler {
  #renderer;
  #camera;
  /**
   * @type {THREE.Scene}
   */
  #scene;

  /**
   * Creates a new preview renderer
   * @param {THREE.Scene} scene the scene you want a preview off
   */
  constructor(scene) {
    this.#renderer = new THREE.WebGLRenderer({
      antialias: true,
      preserveDrawingBuffer: true,
    });
    this.#renderer.shadowMap.enabled = true;
    this.#renderer.setSize(640, 360);

    this.#camera = new THREE.PerspectiveCamera(75, 16 / 9, 0.1, 2000);
    this.#camera.position.set(130, 50, 0);
    this.#camera.lookAt(0, 0, 0);
    this.#scene = scene;

    // Save the preview before the user unloads the website
    window.addEventListener("beforeunload", () => this.#savePreview());

    // save preview every 5s for the first 30s and then every 30s
    // using events like 'beforeunload', doesn't really seem to work with the navigation buttons of the browser, and also causes freezing some times
    const shortIntervall = setInterval(() => {
      this.#savePreview();
    }, 5000);

    // deactivate the first intervall and activate the second
    setTimeout(() => {
      clearInterval(shortIntervall);
      setInterval(() => {
        this.#savePreview();
      }, 30000);
    }, 30000);
  }

  /**
   * Renders the scene with a different renderer and camera to get a reliable position, resolution and scale.
   * Not depending on the window size CANVAS is working in
   */
  async #savePreview() {
    this.#renderer.render(this.#scene, this.#camera);

    const preview = await new Promise((resolve) => {
      this.#renderer.domElement.toBlob((blob) => {
        resolve(blob);
      });
    });

    const formData = new FormData();
    formData.append("preview", preview, "preview.png");

    fetch(window.location.href + "/upload", {
      method: "POST",
      body: formData,
      headers: {
        "X-CSRFToken": this.#getCookie("csrftoken"),
      },
    }).catch((error) => {
      console.error("Error uploading file:", error);
    });
  }

  /**
   * Gets the cookie specified by the name
   * @param {string} name The name of the cookie you want to get.
   * @returns {string|null} the cookie or null if it couldn't be found.
   */
  #getCookie(name) {
    if (!document.cookie) {
      return null;
    }

    // document.cookie is a key=value list separated by ';'
    const xsrfCookies = document.cookie
      .split(";")
      .map((c) => c.trim())
      //filter the right cookie name
      .filter((c) => c.startsWith(name + "="));

    if (xsrfCookies.length === 0) {
      return null;
    }
    // return the decoded value of the first cookie found
    return decodeURIComponent(xsrfCookies[0].split("=")[1]);
  }
}

import { Editor } from "editor";
import { SaveAndLoadHandler } from "saveAndLoadHandler";

/**
 * Class to manage project settings such as environment, graphics, and other settings.
 * Right now, it only manages graphics settings like shadows and fog.
 */
export class ProjectSettingsManager {
  #environmentSettingsEntry;
  #graphicsSettingsEntry;
  #otherSettingsEntry;

  #shadowEnabled;
  #fogEnabled;
  #editor;
  #saveAndLoadHandler;

  /**
   * Constructor for the project settings manager
   */
  constructor() {
    this.#editor = new Editor();
    this.#saveAndLoadHandler = new SaveAndLoadHandler();
    this.initialize();
  }

  /**
   * Method to initialize the project settings manager
   */
  async initialize() {
    await this.#getPresets();

    this.#environmentSettingsEntry = document.getElementById(
      "environment-settings"
    );

    this.#graphicsSettingsEntry = document.getElementById("graphic-settings");

    this.#otherSettingsEntry = document.getElementById("other-settings");

    //render the graphics settings
    this.#renderUISettings();

    this.#environmentSettingsEntry.textContent = "No settings available";
    this.#otherSettingsEntry.textContent = "No settings available";
  }

  /**
   * Method to get the presets for shadows and fog from the project settings
   */
  async #getPresets() {
    const projectJson = await this.#saveAndLoadHandler.getProjectData();
    const settingsList = projectJson["settings"];
    this.#shadowEnabled = settingsList["shadows"];
    this.#fogEnabled = settingsList["fog"];
  }

  /**
   * Method to render the graphics settings
   * This method creates checkboxes for shadow and fog settings,
   * and applies the settings to the editor.
   */
  #renderUISettings() {
    this.#graphicsSettingsEntry.innerHTML = "";

    const graphicSettings = [
      {
        label: "Shadow",
        key: "shadow",
        enabled: this.#shadowEnabled,
        store: (val) => {
          this.#shadowEnabled = val;
        },
        apply: (val) => {
          this.#editor.setShadows(val);
        },
      },
      {
        label: "Fog",
        key: "fog",
        enabled: this.#fogEnabled,
        store: (val) => {
          this.#fogEnabled = val;
        },
        apply: (val) => {
          this.#editor.setFog(val);
        },
      },
    ];

    graphicSettings.forEach(({ label, key, enabled, store, apply }) => {
      const checkbox = this.#createCheckbox(label, enabled, (isChecked) => {
        store(isChecked);
        apply(isChecked);
        this.#saveAndLoadHandler.updateSettings(key, enabled);
      });
      this.#graphicsSettingsEntry.appendChild(checkbox);
    });
  }

  /**
   * Method to create a checkbox
   * @param {string} label - The label for the checkbox
   * @param {boolean} isChecked - Whether the checkbox is checked or not
   * @param {*} onChange - Callback function to handle changes in the checkbox state
   * @returns {HTMLDivElement} Wrapper for the checkbox
   */
  #createCheckbox(label, isChecked, onChange) {
    //Wrapper for the checkbox
    const wrapper = document.createElement("div");
    wrapper.classList.add("form-check", "mb-2");

    //create the checkbox
    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.classList.add("form-check-input");
    checkbox.checked = isChecked;
    checkbox.id = label + "Checkbox";

    //label for the checkbox
    const checkboxLabel = document.createElement("label");
    checkboxLabel.classList.add("form-check-label");
    checkboxLabel.textContent = label;
    checkboxLabel.setAttribute("for", checkbox.id);

    //Event listener for changes in the checkbox
    checkbox.addEventListener("change", () => {
      onChange(checkbox.checked);
    });

    wrapper.appendChild(checkbox);
    wrapper.appendChild(checkboxLabel);
    return wrapper;
  }
}

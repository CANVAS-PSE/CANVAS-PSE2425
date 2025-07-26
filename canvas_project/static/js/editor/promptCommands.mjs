import { Modal } from "bootstrap";
import { CommandPrompt } from "commandPrompt";
import { ObjectManager } from "objectManager";
import { SaveAndLoadHandler } from "saveAndLoadHandler";

/**
 * Parent class of all prompt commands
 */
export class PromptCommand extends HTMLElement {
  #commandName;
  #occurenceLength = null;
  /**
   * @type {number[]}
   */
  #selectedChars = null;
  #commandElem;
  #commandPrompt;

  /**
   * Creates a new prompt command
   * @param {string} name the name of the command
   * @param {CommandPrompt} commandPrompt the command prompt in use for this command
   * @param {string} [keybind=null] the keybind of the command
   */
  constructor(name, commandPrompt, keybind = null) {
    super();
    this.#commandName = name;
    this.#commandPrompt = commandPrompt;
    this.classList.add(
      "rounded-2",
      "p-1",
      "px-2",
      "d-flex",
      "justify-content-between",
      "align-items-center",
    );
    this.style.cursor = "pointer";

    this.#commandElem = document.createElement("div");
    this.#commandElem.innerHTML = name;
    this.appendChild(this.#commandElem);

    if (keybind) {
      const keybindElem = document.createElement("div");
      keybindElem.innerHTML = keybind;
      keybindElem.classList.add("rounded-2", "border", "p-0", "px-2");
      keybindElem.style.fontSize = "80%";
      this.appendChild(keybindElem);
    }

    // execute on click
    this.addEventListener("click", () => {
      this.execute();
      this.#commandPrompt.hide();
    });

    // select this element on hover
    this.addEventListener("mousemove", () => {
      this.#commandPrompt.selectCommand(
        this.#commandPrompt.currentlyAvailableCommands.indexOf(this),
      );
    });
  }

  get commandName() {
    return this.#commandName;
  }

  get occurenceLength() {
    return this.#occurenceLength;
  }

  set occurenceLength(length) {
    this.#occurenceLength = length;
  }

  /**
   * Returns an array of all indexes of characters that got selected by the searchring algorithm.
   * Use for hightlighting them.
   * @param {number[]} chars is an array of char indexes you want to be selected
   */
  set selectedChars(chars) {
    this.#selectedChars = chars;
    if (this.#selectedChars !== null) {
      if (this.#selectedChars.length > 1) {
        this.#occurenceLength =
          this.#selectedChars[this.#selectedChars.length - 1] -
          this.#selectedChars[0];
      } else {
        this.#occurenceLength = 0;
      }
    }
  }

  /**
   * Makes all the characters specified by 'selectedChars' bold.
   */
  formatCommandName() {
    if (this.#selectedChars) {
      let formattedName = "";
      let lastIndex = 0;
      this.#selectedChars.forEach((index) => {
        formattedName += this.#commandName.slice(lastIndex, index);
        formattedName += `<b>${this.#commandName[index]}</b>`;
        lastIndex = index + 1;
      });
      formattedName += this.#commandName.slice(lastIndex);
      this.#commandElem.innerHTML = formattedName;
    } else {
      this.#commandElem.innerHTML = this.#commandName;
    }
  }

  select() {
    this.classList.add("bg-primary");
  }

  unselect() {
    this.classList.remove("bg-primary");
  }

  /**
   * Executes the prompt command.
   */
  execute() {
    throw new Error("This method needs to be implemented in all subclasses");
  }
}

export class ThemePromptCommand extends PromptCommand {
  /**
   * Create a new theme command
   * @param {string} description the description of the command
   * @param {CommandPrompt} commandPrompt the commandprompt in use
   */
  constructor(description, commandPrompt) {
    if (new.target === ThemePromptCommand) {
      throw new Error(
        "Cannot instantiate abstract class ThemePromptCommand directly",
      );
    }
    super(description, commandPrompt);
  }

  execute() {
    throw new Error("This method needs to be implemented in all subclasses");
  }

  /**
   * Sets the theme of the application
   * @param {"light" | "dark" | "auto"} theme - The theme to set. Can be "light", "dark", or "auto".
   */
  setTheme(theme) {
    // store the theme
    localStorage.setItem("theme", theme);

    // update the theme
    if (theme === "auto") {
      document.documentElement.setAttribute(
        "data-bs-theme",
        window.matchMedia("(prefers-color-scheme: dark)").matches
          ? "dark"
          : "light",
      );
    } else {
      document.documentElement.setAttribute("data-bs-theme", theme);
    }

    // update the settings
    const themeSelect = document.getElementById("theme-select");

    if (!themeSelect) {
      return;
    }

    switch (theme) {
      case "light":
        //@ts-ignore
        themeSelect.value = "light";
        break;
      case "dark":
        //@ts-ignore
        themeSelect.value = "dark";
        break;
      default:
        //@ts-ignore
        themeSelect.value = "auto";
        break;
    }
  }
}

/**
 * Prompt command to enable light mode
 */
export class LightModePromptCommand extends ThemePromptCommand {
  /**
   * Create this prompt command
   * @param {CommandPrompt} commandPrompt the command prompt that handles this command
   */
  constructor(commandPrompt) {
    super("Use light mode", commandPrompt);
  }

  execute() {
    this.setTheme("light");
  }
}

/**
 * Prompt command to enable dark mode
 */
export class DarkModePromptCommand extends ThemePromptCommand {
  /**
   * Create this prompt command
   * @param {CommandPrompt} commandPrompt the command prompt that handles this command
   */
  constructor(commandPrompt) {
    super("Use dark mode", commandPrompt);
  }

  execute() {
    this.setTheme("dark");
  }
}

/**
 * Prompt command to enable auto mode
 */
export class AutoModePromptCommand extends ThemePromptCommand {
  /**
   * Create this prompt command
   * @param {CommandPrompt} commandPrompt the command prompt that handles this command
   */
  constructor(commandPrompt) {
    super("Use auto mode", commandPrompt);
  }

  execute() {
    this.setTheme("auto");
  }
}

/**
 * Prompt command to add a heliostat to the scene
 */
export class AddHeliostatPromptCommand extends PromptCommand {
  #objectManager;
  /**
   * Create this prompt command
   * @param {CommandPrompt} commandPrompt the command prompt that handles this command
   * @param {ObjectManager} objectManager - The ObjectManager instance to manage the creation of objects.
   */
  constructor(commandPrompt, objectManager) {
    super("Add heliostat", commandPrompt);
    this.#objectManager = objectManager;
  }

  execute() {
    this.#objectManager.createHeliostat();
  }
}

/**
 * Prompt command to add a receiver to the scene
 */
export class AddReceiverPromptCommand extends PromptCommand {
  #objectManager;
  /**
   * Create this prompt command
   * @param {CommandPrompt} commandPrompt the command prompt that handles this command
   * @param {ObjectManager} objectManager - The ObjectManager instance to manage the creation of objects.
   */
  constructor(commandPrompt, objectManager) {
    super("Add receiver", commandPrompt);
    this.#objectManager = objectManager;
  }

  execute() {
    this.#objectManager.createReceiver();
  }
}

/**
 * Prompt command to add a lightsource to the scene
 */
export class AddLightSourcePromptCommand extends PromptCommand {
  #objectManager;
  /**
   * Create this prompt command
   * @param {CommandPrompt} commandPrompt the command prompt that handles this command
   * @param {ObjectManager} objectManager - The ObjectManager instance to manage the creation of objects.
   */
  constructor(commandPrompt, objectManager) {
    super("Add light source", commandPrompt);
    this.#objectManager = objectManager;
  }

  execute() {
    this.#objectManager.createLightSource();
  }
}

/**
 * Prompt command to toggle fullscreen
 */
export class ToggleFullscreenPromptCommand extends PromptCommand {
  /**
   * Create this prompt command
   * @param {CommandPrompt} commandPrompt the command prompt that handles this command
   */
  constructor(commandPrompt) {
    super("Toggle fullscreen", commandPrompt, "F11");
  }

  execute() {
    if (navigator.userAgent.indexOf("Safari") > -1) {
      if (document.webkitFullscreenElement === null) {
        document.documentElement.webkitRequestFullscreen();
      } else if (document.webkitExitFullscreen) {
        document.webkitExitFullscreen();
      }
      return;
    }

    if (document.fullscreenElement === null) {
      document.documentElement.requestFullscreen();
    } else if (document.exitFullscreen) {
      document.exitFullscreen();
    }
  }
}

/**
 * Prompt command to export the current project
 */
export class ExportProjectPromptCommand extends PromptCommand {
  /**
   * Create this prompt command
   * @param {CommandPrompt} commandPrompt the command prompt that handles this command
   */
  constructor(commandPrompt) {
    super("Export project", commandPrompt);
  }

  execute() {
    let modal = new Modal(document.getElementById("loadingModal"));
    modal.show();

    const projectName = window.location.pathname.split("/")[2];

    fetch(window.location + "/download", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": SaveAndLoadHandler.getCookie("csrftoken"),
      },
    })
      .then((response) => {
        // Trigger file download after response
        return response.blob();
      })
      .then((data) => {
        let link = document.createElement("a");

        link.href = URL.createObjectURL(data);
        link.download = projectName + `.h5`;
        link.click();

        // After download, close modal and redirect
        modal.hide();
        window.location.reload();
      })
      .catch((error) => {
        console.error("Error:", error);
        modal.hide();
      });
  }
}

/**
 * Prompt command to render the current project
 */
export class RenderProjectPromptCommand extends PromptCommand {
  /**
   * Create this prompt command
   * @param {CommandPrompt} commandPrompt the command prompt that handles this command
   */
  constructor(commandPrompt) {
    super("Render project", commandPrompt);
  }

  execute() {
    const jobModal = new Modal(document.getElementById("startJobModal"));
    jobModal.show();

    document
      .getElementById("startJobModal")
      .addEventListener("shown.bs.modal", () => {
        document.getElementById("createNewJob").focus();
      });
  }
}

/**
 * Prompt command to open the settings pane
 */
export class OpenSettingsPromptCommand extends PromptCommand {
  /**
   * Create this prompt command
   * @param {CommandPrompt} commandPrompt the command prompt that handles this command
   */
  constructor(commandPrompt) {
    super("Open settings", commandPrompt);
  }

  execute() {
    const settingsModal = new Modal(document.getElementById("settings"));
    settingsModal.show();
  }
}

/**
 * Prompt command to open the job interface pane
 */
export class OpenJobInterfacePromptCommand extends PromptCommand {
  /**
   * Create this prompt command
   * @param {CommandPrompt} commandPrompt the command prompt that handles this command
   */
  constructor(commandPrompt) {
    super("Open job interface", commandPrompt);
  }

  execute() {
    const jobInterfaceModal = new Modal(
      document.getElementById("jobInterface"),
    );
    jobInterfaceModal.show();

    document
      .getElementById("jobInterface")
      .addEventListener("shown.bs.modal", () => {
        document.getElementById("createNewJob").focus();
      });
  }
}

/**
 * Prompt command to open the keybindings help page
 */
export class OpenKeybindsPromptCommand extends PromptCommand {
  /**
   * Create this prompt command
   * @param {CommandPrompt} commandPrompt the command prompt that handles this command
   */
  constructor(commandPrompt) {
    super("Open keybindings help page", commandPrompt);
  }

  execute() {
    const keybindingsModal = new Modal(
      document.getElementById("keyboardModal"),
    );
    keybindingsModal.show();
  }
}

/**
 * Prompt command to logout the user
 */
export class LogoutPromptCommand extends PromptCommand {
  /**
   * Create this prompt command
   * @param {CommandPrompt} commandPrompt the command prompt that handles this command
   */
  constructor(commandPrompt) {
    super("Logout", commandPrompt);
  }

  execute() {
    fetch(window.location.origin + "/logout/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": SaveAndLoadHandler.getCookie("csrftoken"),
      },
    }).then(() => {
      window.location.href = window.location.origin;
    });
  }
}

/**
 * Prompt command to create a new project
 */
export class NewProjectPromptCommand extends PromptCommand {
  /**
   * Create this prompt command
   * @param {CommandPrompt} commandPrompt the command prompt that handles this command
   */
  constructor(commandPrompt) {
    super("Create new project", commandPrompt);
  }

  execute() {
    const newProjectModal = new Modal(
      document.getElementById("createNewProject"),
    );
    newProjectModal.show();

    document
      .getElementById("createNewProject")
      .addEventListener("shown.bs.modal", () => {
        document.getElementById("id_name").focus();
      });
  }
}

/**
 * Prompt command to open an existing project
 */
export class OpenProjectPromptCommand extends PromptCommand {
  /**
   * Create this prompt command
   * @param {CommandPrompt} commandPrompt the command prompt that handles this command
   */
  constructor(commandPrompt) {
    super("Open exisiting project", commandPrompt);
  }

  execute() {
    const newProjectModal = new Modal(document.getElementById("openProject"));
    newProjectModal.show();
  }
}

// define the new HTML elements
customElements.define("light-mode-prompt-command", LightModePromptCommand);
customElements.define("dark-mode-prompt-command", DarkModePromptCommand);
customElements.define("auto-mode-prompt-command", AutoModePromptCommand);
customElements.define(
  "add-heliostat-prompt-command",
  AddHeliostatPromptCommand,
);
customElements.define("add-receiver-prompt-command", AddReceiverPromptCommand);
customElements.define(
  "add-light-source-prompt-command",
  AddLightSourcePromptCommand,
);
customElements.define(
  "toggle-fullscreen-prompt-command",
  ToggleFullscreenPromptCommand,
);
customElements.define(
  "export-project-prompt-command",
  ExportProjectPromptCommand,
);
customElements.define(
  "render-project-prompt-command",
  RenderProjectPromptCommand,
);
customElements.define(
  "open-settings-prompt-command",
  OpenSettingsPromptCommand,
);
customElements.define(
  "open-job-interface-prompt-command",
  OpenJobInterfacePromptCommand,
);
customElements.define(
  "open-keybings-prompt-command",
  OpenKeybindsPromptCommand,
);
customElements.define("logout-prompt-command", LogoutPromptCommand);
customElements.define("new-project-prompt-command", NewProjectPromptCommand);
customElements.define("open-project-prompt-command", OpenProjectPromptCommand);

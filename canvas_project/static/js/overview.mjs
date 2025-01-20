import { Editor } from "editor";
import { ObjectType } from "objects";
import { Picker } from "picker";

export class OverviewHandler {
    #editor;
    #picker;
    #overviewButton;
    #selectedItems = [];
    #heliostatList;
    #receiverList;
    #lightsourceList;
    #heliostatMap = new Map();
    #receiverMap = new Map();
    #lightsourceMap = new Map();

    /**
     * Creates a new overview handler.
     * @param {Picker} picker the picker currently in use.
     */
    constructor(picker) {
        this.#picker = picker;
        this.#editor = new Editor();
        this.#overviewButton = document.getElementById("overview-tab");
        this.#heliostatList = document.getElementById("heliostatList");
        this.#receiverList = document.getElementById("receiverList");
        this.#lightsourceList = document.getElementById("lightsourceList");

        // render when overview tab is selected
        this.#overviewButton.addEventListener("click", () => {
            this.#render();
        });

        // re-render when a new item is selected
        document
            .getElementById("canvas")
            .addEventListener("itemSelected", () => {
                if (this.#overviewButton.classList.contains("active")) {
                    this.#render();
                }
            });

        this.#handleUserInput();
    }

    #render() {
        // clear the list
        this.#heliostatList.innerHTML = "";
        this.#receiverList.innerHTML = "";
        this.#lightsourceList.innerHTML = "";

        const objects = this.#editor.objects;
        const selectedObjects = this.#picker.getSelectedObjects();

        // reset the selected items list, to be filled with the items specified by selectedObjects
        this.#selectedItems = [];

        // render the objects
        objects.forEach((element) => {
            const selected = selectedObjects.includes(element);

            switch (element.objectType) {
                case ObjectType.HELIOSTAT:
                    this.#heliostatList.appendChild(
                        this.#createHeliostatEntry(element, selected)
                    );
                    break;
                case ObjectType.RECEIVER:
                    this.#receiverList.appendChild(
                        this.#createReceiverEntry(element, selected)
                    );
                    break;
                case ObjectType.LIGHTSOURCE:
                    this.#lightsourceList.appendChild(
                        this.#createLightsourceEntry(element, selected)
                    );
                    break;
                default:
                    console.warn(`Unknown object type: ${element.objectType}`);
            }
        });
    }

    #createHeliostatEntry(object, selected) {
        this.#heliostatMap.set(`${object.apiID}`, object);

        // create the html element to render
        const heliostatEntry = document.createElement("div");
        heliostatEntry.role = "button";
        heliostatEntry.classList =
            "d-flex gap-2 p-2 rounded-2 overviewElem " +
            (selected ? "bg-primary-subtle" : "bg-body-secondary");

        const icon = document.createElement("i");
        icon.classList = "bi-arrow-up-right-square";
        heliostatEntry.appendChild(icon);

        const text = document.createElement("div");
        text.innerHTML = "Heliostat " + object.apiID;
        heliostatEntry.appendChild(text);

        heliostatEntry.dataset.apiId = object.apiID;
        heliostatEntry.dataset.objectType = ObjectType.HELIOSTAT;

        if (selected) {
            this.#selectedItems.push(heliostatEntry);
        }

        return heliostatEntry;
    }

    #createReceiverEntry(object, selected) {
        this.#receiverMap.set(`${object.apiID}`, object);

        // create the html element to render
        const receiverEntry = document.createElement("div");
        receiverEntry.role = "button";
        receiverEntry.classList =
            "d-flex gap-2 p-2 rounded-2 overviewElem " +
            (selected ? "bg-primary-subtle" : "bg-body-secondary");

        const icon = document.createElement("i");
        icon.classList = "bi bi-align-bottom";
        receiverEntry.appendChild(icon);

        const text = document.createElement("div");
        text.innerHTML = "Receiver " + object.apiID;
        receiverEntry.appendChild(text);

        receiverEntry.dataset.apiId = object.apiID;
        receiverEntry.dataset.objectType = ObjectType.RECEIVER;

        if (selected) {
            this.#selectedItems.push(receiverEntry);
        }

        return receiverEntry;
    }

    #createLightsourceEntry(object, selected) {
        this.#lightsourceMap.set(`${object.apiID}`, object);

        // create the html element to render
        const lightsourceEntry = document.createElement("div");
        lightsourceEntry.role = "button";
        lightsourceEntry.classList =
            "d-flex gap-2 p-2 rounded-2 overviewElem " +
            (selected ? "bg-primary-subtle" : "bg-body-secondary");

        const icon = document.createElement("i");
        icon.classList = "bi bi-lightbulb";
        lightsourceEntry.appendChild(icon);

        const text = document.createElement("div");
        text.innerHTML = "Lightsource " + object.apiID;
        lightsourceEntry.appendChild(text);

        lightsourceEntry.dataset.apiId = object.apiID;
        lightsourceEntry.dataset.objectType = ObjectType.LIGHTSOURCE;

        if (selected) {
            this.#selectedItems.push(lightsourceEntry);
        }

        return lightsourceEntry;
    }

    #handleUserInput() {
        document
            .getElementById("accordionOverview")
            .addEventListener("click", (event) => {
                // get the closest parent which has the overviewElem class
                const target = event.target.closest(".overviewElem");

                if (target && target.classList.contains("overviewElem")) {
                    // TODO: When pressing STRG add to selection or remove if already selected
                    // TODO: Whene holding SHIFT select everything between the highest and the clicked on element
                    // When more than one item is selected -> choose the nearest selected, or the last added elem

                    this.#selectedItems = [target];

                    const selectedObjects = [];
                    this.#selectedItems.forEach((element) => {
                        switch (element.dataset.objectType) {
                            case ObjectType.HELIOSTAT:
                                selectedObjects.push(
                                    this.#heliostatMap.get(
                                        `${element.dataset.apiId}`
                                    )
                                );
                                break;
                            case ObjectType.RECEIVER:
                                selectedObjects.push(
                                    this.#receiverMap.get(
                                        `${element.dataset.apiId}`
                                    )
                                );
                                break;
                            case ObjectType.LIGHTSOURCE:
                                selectedObjects.push(
                                    this.#lightsourceMap.get(
                                        `${element.dataset.apiId}`
                                    )
                                );
                                break;
                            default:
                                console.warn(
                                    `Unknown object type: ${element.objectType}`
                                );
                        }
                    });
                    this.#picker.setSelection(selectedObjects);
                }
            });
    }
}

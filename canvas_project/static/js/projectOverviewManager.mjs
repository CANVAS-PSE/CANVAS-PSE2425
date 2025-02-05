export class ProjectOverviewManager {
    constructor() {
        // handle all favorite buttons
        document.querySelectorAll(".favoriteButton").forEach((button) => {
            button.addEventListener("click", () => {
                this.#toggleFavorite(button);
            });
        });

        this.#handleFavoriteFilter();
        // handle duplication

        // handle deletion

        // handle editing
    }

    /**
     * Toggles the favorite setting for the given button
     * @param {HTMLElement} favoriteButton
     */
    #toggleFavorite(favoriteButton) {
        const projectName = favoriteButton.dataset.projectName;
        const isFavorite = favoriteButton.dataset.isFavorite;

        if (isFavorite == "true") {
            favoriteButton.dataset.isFavorite = "false";
            const projectElement = favoriteButton.closest(".project");
            projectElement.dataset.isFavorite = "false";
            favoriteButton.children[0].classList.remove(
                "bi-star-fill",
                "text-warning"
            );
            favoriteButton.children[0].classList.add("bi-star");
            fetch(window.location + "defavorProject/" + projectName);
        } else if (isFavorite == "false") {
            favoriteButton.dataset.isFavorite = "true";
            const projectElement = favoriteButton.closest(".project");
            projectElement.dataset.isFavorite = "true";
            favoriteButton.children[0].classList.remove("bi-star");
            favoriteButton.children[0].classList.add(
                "bi-star-fill",
                "text-warning"
            );
            fetch(window.location + "favorProject/" + projectName);
        } else {
            throw new Error(
                `invalid favorite state for project ${projectName}`
            );
        }
    }

    #handleFavoriteFilter() {
        const favoriteSwitchWrapper = document.createElement("div");
        favoriteSwitchWrapper.classList.add(
            "form-check",
            "form-switch",
            "position-relative",
            "mx-auto"
        );
        const favoriteSwitch = document.createElement("input");
        favoriteSwitch.classList.add("form-check-input");
        favoriteSwitch.type = "checkbox";
        favoriteSwitch.role = "switch";
        favoriteSwitch.id = "favoriteSwitch";

        const favoriteSwitchLabel = document.createElement("label");
        favoriteSwitchLabel.classList.add("form-check-label");
        favoriteSwitchLabel.setAttribute("for", "favoriteSwitch");
        favoriteSwitchLabel.innerHTML = "Only favorites";

        favoriteSwitchWrapper.appendChild(favoriteSwitch);
        favoriteSwitchWrapper.appendChild(favoriteSwitchLabel);

        document
            .getElementById("projectList")
            .insertBefore(
                favoriteSwitchWrapper,
                document.getElementById("projectList").children[0]
            );

        favoriteSwitch.addEventListener("change", () => {
            document.querySelectorAll(".project").forEach((project) => {
                if (favoriteSwitch.checked) {
                    if (project.dataset.isFavorite == "true") {
                        project.classList.add("d-block");
                        project.classList.remove("d-none");
                    } else {
                        project.classList.add("d-none");
                        project.classList.remove("d-block");
                    }
                } else {
                    project.classList.add("d-block");
                    project.classList.remove("d-none");
                }
            });
        });
    }
}

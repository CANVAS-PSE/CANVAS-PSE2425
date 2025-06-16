import { Heliostat, Receiver, LightSource } from "objects";

let saveAndLoadHandlerInstance = null;

/**
 * Provides a wrapper for the API
 *
 * Contains a methods for every databank manipulation needed.
 */
export class SaveAndLoadHandler {
    #projectID;
    #baseAPIUrl;

    /**
     * Creates a saveAndLoadHandler or returns the existing one
     * @param {Number} [projectId=null] the projectID for api requests.
     * @returns a new saveAndLoadHandler instance or the existing one.
     */
    constructor(projectId = null) {
        if (saveAndLoadHandlerInstance) {
            return saveAndLoadHandlerInstance;
        }
        if (!projectId) {
            throw new Error(
                "To initialize the SaveAndLoadHandler an projectID is needed",
            );
        }
        saveAndLoadHandlerInstance = this;

        this.#projectID = projectId;
        this.#baseAPIUrl = window.location.origin + "/api/";
    }

    /**
     * Returns a Json representation of the project defined by the project_id
     * @returns {Promise<JSON>} A JSON representation of the project
     */
    async getProjectData() {
        const url = this.#baseAPIUrl + "projects/" + this.#projectID;
        return this.#makeApiCall(url, "GET");
    }

    /**
     * Creates a databank entry for the given heliostat
     * @param {Heliostat} heliostat Is the heliostat you want an entry for
     * @returns {Promise<JSON>} JSON representation of the new heliostat.
     */
    async createHeliostat(heliostat) {
        const url =
            this.#baseAPIUrl + "projects/" + this.#projectID + "/heliostats/";

        const body = {
            name: heliostat.objectName,
            position_x: heliostat.position.x,
            position_y: heliostat.position.y,
            position_z: heliostat.position.z,
            aimpoint_x: heliostat.aimPoint.x,
            aimpoint_y: heliostat.aimPoint.y,
            aimpoint_z: heliostat.aimPoint.z,
            number_of_facets: heliostat.numberOfFacets,
            kinematic_type: heliostat.kinematicType,
        };

        return this.#makeApiCall(url, "POST", body);
    }

    /**
     * Creates a databank entry for the given receiver
     * @param {Receiver} receiver Is the receiver you want an entry for
     * @returns {Promise<JSON>} JSON representation of the new receiver.
     */
    async createReceiver(receiver) {
        const url =
            this.#baseAPIUrl + "projects/" + this.#projectID + "/receivers/";

        const body = {
            name: receiver.objectName,
            position_x: receiver.getPosition().x,
            position_y: receiver.getPosition().y,
            position_z: receiver.getPosition().z,
            normal_x: receiver.normalVector.x,
            normal_y: receiver.normalVector.y,
            normal_z: receiver.normalVector.z,
            rotation_y: receiver.quaternionToYDegree(receiver.oldQuaternion),
            curvature_e: receiver.curvatureE,
            curvature_u: receiver.curvatureU,
            plane_e: receiver.planeE,
            plane_u: receiver.planeU,
            resolution_e: receiver.resolutionE,
            resolution_u: receiver.resolutionU,
        };

        return this.#makeApiCall(url, "POST", body);
    }

    /**
     * Creates a databank entry for the given lightsource
     * @param {LightSource} lightsource Is the lightsource you want an entry for
     * @returns {Promise<JSON>} JSON representation of the new lightsource.
     */
    async createLightSource(lightsource) {
        const url =
            this.#baseAPIUrl + "projects/" + this.#projectID + "/lightsources/";

        const body = {
            name: lightsource.objectName,
            number_of_rays: lightsource.numberOfRays,
            lightsource_type: lightsource.lightSourceType,
            distribution_type: lightsource.distributionType,
            mean: lightsource.distributionMean,
            covariance: lightsource.distributionCovariance,
        };

        return this.#makeApiCall(url, "POST", body);
    }

    // Object deletion
    /**
     * Deletes the given heliostat from the backend
     * @param {Heliostat} heliostat Is the heliostat you want to delete
     */
    async deleteHeliostat(heliostat) {
        if (!heliostat.apiID) {
            return;
        }

        const url =
            this.#baseAPIUrl +
            "projects/" +
            this.#projectID +
            "/heliostats/" +
            heliostat.apiID +
            "/";

        return this.#makeApiCall(url, "DELETE");
    }

    // Object deletion
    /**
     * Deletes the given receiver from the backend
     * @param {Receiver} receiver Is the receiver you want to delete
     */
    async deleteReceiver(receiver) {
        if (!receiver.apiID) {
            return;
        }

        const url =
            this.#baseAPIUrl +
            "projects/" +
            this.#projectID +
            "/receivers/" +
            receiver.apiID +
            "/";

        return this.#makeApiCall(url, "DELETE");
    }

    // Object deletion
    /**
     * Deletes the given lightsource from the backend
     * @param {LightSource} lightsource Is the lightsource you want to delete
     */
    async deleteLightsource(lightsource) {
        if (!lightsource.apiID) {
            return;
        }

        const url =
            this.#baseAPIUrl +
            "projects/" +
            this.#projectID +
            "/lightsources/" +
            lightsource.apiID +
            "/";

        return this.#makeApiCall(url, "DELETE");
    }

    // Object updating
    /**
     * Updates the given heliostat in the backend
     * @param {Heliostat} heliostat Is the updated heliostat from the frontend
     * @returns {Promise<JSON>} JSON representation of the updated heliostat
     */
    async updateHeliostat(heliostat) {
        if (!heliostat.apiID) {
            return;
        }

        const url =
            this.#baseAPIUrl +
            "projects/" +
            this.#projectID +
            "/heliostats/" +
            heliostat.apiID +
            "/";

        const body = {
            id: heliostat.apiID,
            name: heliostat.objectName,
            position_x: heliostat.position.x,
            position_y: heliostat.position.y,
            position_z: heliostat.position.z,
            aimpoint_x: heliostat.aimPoint.x,
            aimpoint_y: heliostat.aimPoint.y,
            aimpoint_z: heliostat.aimPoint.z,
            number_of_facets: heliostat.numberOfFacets,
            kinematic_type: heliostat.kinematicType,
        };

        return this.#makeApiCall(url, "PUT", body);
    }

    /**
     * Updates the given receiver in the backend
     * @param {Receiver} receiver Is the updated receiver from the frontend
     * @returns {Promise<JSON>} JSON representation of the updated receiver
     */
    async updateReceiver(receiver) {
        if (!receiver.apiID) {
            return;
        }

        const url =
            this.#baseAPIUrl +
            "projects/" +
            this.#projectID +
            "/receivers/" +
            receiver.apiID +
            "/";

        const body = {
            id: receiver.apiID,
            name: receiver.objectName,
            receiver_type: receiver.towerType,
            position_x: receiver.getPosition().x,
            position_y: receiver.getPosition().y,
            position_z: receiver.getPosition().z,
            normal_x: receiver.normalVector.x,
            normal_y: receiver.normalVector.y,
            normal_z: receiver.normalVector.z,
            rotation_y: receiver.quaternionToYDegree(receiver.oldQuaternion),
            curvature_e: receiver.curvatureE,
            curvature_u: receiver.curvatureU,
            plane_e: receiver.planeE,
            plane_u: receiver.planeU,
            resolution_e: receiver.resolutionE,
            resolution_u: receiver.resolutionU,
        };

        return this.#makeApiCall(url, "PUT", body);
    }

    /**
     * Updates the given lightsource in the backend
     * @param {LightSource} lightsource Is the updated lightsource from the frontend
     * @returns {Promise<JSON>} JSON representation of the updated light source
     */
    async updateLightsource(lightsource) {
        if (!lightsource.apiID) {
            return;
        }

        const url =
            this.#baseAPIUrl +
            "projects/" +
            this.#projectID +
            "/lightsources/" +
            lightsource.apiID +
            "/";

        const body = {
            id: lightsource.apiID,
            name: lightsource.objectName,
            number_of_rays: lightsource.numberOfRays,
            lightsource_type: lightsource.lightSourceType,
            distribution_type: lightsource.distributionType,
            mean: lightsource.distributionMean,
            covariance: lightsource.distributionCovariance,
        };

        return this.#makeApiCall(url, "PUT", body);
    }

    // Settings updating
    /**
     * Updates the settings accroding to the given changes
     * @param {String} attribute the attribute you want to change
     * @param {any} newValue the new value of the attribute
     * @returns {Promise<JSON>} JSON of all the project settings
     */
    async updateSettings(attribute, newValue) {
        const url =
            this.#baseAPIUrl + "projects/" + this.#projectID + "/settings/";

        const body = {
            [attribute]: newValue,
        };

        return this.#makeApiCall(url, "PUT", body);
    }

    /**
     * Gets the cookie specified by the name
     * @param {String} name The name of the cookie you want to get.
     * @returns the cookie or null if it couldn't be found.
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

    /**
     * Wrapper function for an standard api call
     * @param {string} endpoint The endpoint to make the api call to
     * @param {"PUT" | "POST" | "GET" | "DELETE"} method The method you want to use
     * @param {any} [body=null] the body for the api call
     */
    async #makeApiCall(endpoint, method, body) {
        return fetch(endpoint, {
            method: method,
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": this.#getCookie("csrftoken"),
            },
            body: JSON.stringify(body),
        })
            .then((response) => {
                if (!response.ok) {
                    throw new Error(`Response status: ${response.status}`);
                }
                return response.json();
            })
            .catch((error) => console.log(error.message));
    }
}

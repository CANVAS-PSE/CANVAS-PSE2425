import * as THREE from "three";

import { ViewHelper } from "compass";
import { OrbitControls } from "orbitControls";
import { TransformControls } from "transformControls";

import { UndoRedoHandler } from "undoRedoHandler";
import { SaveAndLoadHandler } from "saveAndLoadHandler";
//import { Navbar } from "navbar";
import { OverviewHandler } from "overview";
//import { ModeSelector } from "modeSelector";
import { Picker } from "picker";
//import { ProjectSettingManager } from "projectSettingManager";
//import { QuickSelector } from "quickSelector";
//import { JobInterface } from "jobInterface";
//import { Inspector } from "inspector";

import { Heliostat, Receiver, LightSource, Terrain, ObjectType } from "objects";

let editorInstance = null;
export class Editor {
    #undoRedoHandler;
    #saveAndLoadHandler;
    #navbar;
    #picker;
    #overview;
    #modeSelector;
    #projectSettingManager;
    #quickSelector;
    #jobInterface;
    #inspector;

    #projectId;
    #canvas;
    #transformControls;
    #controls;
    #compass;
    #selectionBox;
    #directionalLight;
    #hemisphereLight;
    #skybox;
    #skyboxLoader;
    #renderer;
    #camera;
    #scene;
    #selectableGroup = new THREE.Group();
    #terrain;

    constructor(projectId) {
        // singleton
        if (editorInstance) return editorInstance;
        editorInstance = this;

        this.#projectId = projectId;

        this.#saveAndLoadHandler = new SaveAndLoadHandler(this.#projectId);

        // initate ThreeJs scene
        this.#setUpScene().#loadProject();

        // initiate needed classes
        this.#undoRedoHandler = new UndoRedoHandler();
        //this.#navbar = new Navbar();
        //this.#modeSelector = new ModeSelector();
        this.#picker = new Picker(
            this.#camera,
            this.#transformControls,
            this.#selectionBox,
            this.#selectableGroup
        );
        this.#overview = new OverviewHandler(this.#picker);
        //this.#projectSettingManager = new ProjectSettingManager();
        //this.#quickSelector = new QuickSelector();
        //this.#jobInterface = new JobInterface();
        //this.#inspector = new Inspector(this.#picker);

        window.addEventListener("resize", () => this.onWindowResize());

        this.animate();
    }

    animate() {
        requestAnimationFrame(() => this.animate());
        this.render();
    }

    render() {
        this.#selectionBox.update();
        this.#renderer.clear();
        this.#renderer.render(this.#scene, this.#camera);
        this.#compass.render(this.#renderer);
    }

    updateAspectRatio() {
        this.#camera.aspect =
            this.#canvas.offsetWidth / this.#canvas.offsetHeight;
        this.#camera.updateProjectionMatrix();
    }

    onWindowResize() {
        this.updateAspectRatio();
        this.#renderer.setSize(
            this.#canvas.offsetWidth,
            this.#canvas.offsetHeight
        );
        this.render();
    }

    #setUpScene() {
        this.#canvas = document.getElementById("canvas");

        this.#scene = new THREE.Scene();
        this.#camera = new THREE.PerspectiveCamera(
            75,
            this.#canvas.clientWidth / this.#canvas.clientHeight,
            0.1,
            2000
        );
        this.#camera.position.set(-7.5, 2.5, 0.75);

        this.#renderer = new THREE.WebGLRenderer({ antialias: true });
        // since we render multiple times (scene and compass), we need to clear the renderer manually
        this.#renderer.autoClear = false;
        this.#renderer.shadowMap.enabled = true;
        this.#renderer.setSize(
            this.#canvas.clientWidth,
            this.#canvas.clientHeight
        );
        this.#canvas.appendChild(this.#renderer.domElement);

        //set up empty scene
        this.#skyboxLoader = new THREE.CubeTextureLoader();
        this.#skybox = this.#skyboxLoader.load([
            "/static/img/skybox/px.png",
            "/static/img/skybox/nx.png",
            "/static/img/skybox/py.png",
            "/static/img/skybox/ny.png",
            "/static/img/skybox/pz.png",
            "/static/img/skybox/nz.png",
        ]);
        this.#scene.background = this.#skybox;
        this.#scene.fog = new THREE.Fog(0xdde0e0, 100, 2200);

        this.#hemisphereLight = new THREE.HemisphereLight();
        this.#scene.add(this.#hemisphereLight);

        this.#terrain = new Terrain(2000);
        this.#scene.add(this.#terrain);

        this.#directionalLight = new THREE.DirectionalLight(0xffffff, 5);
        this.#directionalLight.position.set(200, 100, 200);
        this.#directionalLight.castShadow = true;
        this.#scene.add(this.#directionalLight);

        this.#directionalLight.shadow.mapSize.set(16384, 16384);
        this.#directionalLight.shadow.radius = 2;
        this.#directionalLight.shadow.blurSamples = 10;
        this.#directionalLight.shadow.camera.top = 200;
        this.#directionalLight.shadow.camera.bottom = -200;
        this.#directionalLight.shadow.camera.left = 400;
        this.#directionalLight.shadow.camera.right = -400;
        this.#directionalLight.shadow.camera.far = 1000;

        // Helpers
        this.#compass = new ViewHelper(
            this.#camera,
            this.#renderer.domElement,
            200,
            "circles"
        );

        this.#selectionBox = new THREE.BoxHelper();
        this.#scene.add(this.#selectionBox);

        // controls
        this.#transformControls = new TransformControls(
            this.#camera,
            this.#renderer.domElement
        );
        this.#scene.add(this.#transformControls.getHelper());

        this.#controls = new OrbitControls(
            this.#camera,
            this.#renderer.domElement
        );
        this.#controls.screenSpacePanning = false;
        this.#controls.maxDistance = 500;
        this.#controls.minDistance = 10;
        this.#controls.maxPolarAngle = Math.PI / 2 - 0.02;

        // disable orbit controls while moving object
        this.#transformControls.addEventListener(
            "dragging-changed",
            (event) => {
                this.#controls.enabled = !event.value;
            }
        );

        this.#selectableGroup.name = "selectableGroup";
        this.#scene.add(this.#selectableGroup);

        return this;
    }

    async #loadProject() {
        const projectJson = await this.#saveAndLoadHandler.getProjectData();

        const heliostatList = projectJson["heliostats"];
        const receiverList = projectJson["receivers"];
        const lightsourceList = projectJson["lightsources"];
        const settingsList = projectJson["settings"];

        heliostatList.forEach((heliostat) => {
            this.#selectableGroup.add(
                new Heliostat(
                    heliostat.id,
                    new THREE.Vector3(
                        heliostat.position_x,
                        heliostat.position_y,
                        heliostat.position_z
                    ),
                    new THREE.Vector3(
                        heliostat.aimpoint_x,
                        heliostat.aimpoint_y,
                        heliostat.aimpoint_z
                    ),
                    heliostat.number_of_facets,
                    heliostat.kinematic_type
                )
            );
        });

        receiverList.forEach((receiver) => {
            this.#selectableGroup.add(
                new Receiver(
                    receiver.id,
                    new THREE.Vector3(
                        receiver.position_x,
                        receiver.position_y,
                        receiver.position_z
                    ),
                    receiver.rotation_y,
                    new THREE.Vector3(
                        receiver.normal_x,
                        receiver.normal_y,
                        receiver.normal_z
                    ),
                    receiver.towerType,
                    receiver.plane_e,
                    receiver.plane_u,
                    receiver.resolution_e,
                    receiver.resolution_u,
                    receiver.curvature_e,
                    receiver.curvature_u
                )
            );
        });

        lightsourceList.forEach((lightsource) => {
            this.#selectableGroup.add(
                new LightSource(
                    lightsource.id,
                    lightsource.number_of_rays,
                    lightsource.lightsource_type,
                    lightsource.distribution_type,
                    lightsource.mean,
                    lightsource.covariance
                )
            );
        });

        // set the settings
        this.setShadows(settingsList["shadows"]).setFog(settingsList["fog"]);

        // TODO: Update settings also in UI --> wait till implemented

        return this;
    }

    /**
     * Enables or disables the shadows
     * @param {Boolean} mode is the mode you want to use
     */
    setShadows(mode) {
        this.#renderer.shadowMap.enabled = mode;
        this.#saveAndLoadHandler.updateSettings("shadows", mode);
        return this;
    }

    /**
     * Enables or disables the fog
     * @param {Boolean} mode is the mode you want to use
     */
    setFog(mode) {
        this.#scene.fog = mode ? new THREE.Fog(0xdde0e0, 100, 2200) : null;
        this.#saveAndLoadHandler.updateSettings("fog", mode);
        return this;
    }

    /**
     * Adds an object to the scene and saves it inside of the database.
     * Only allows adding of heliostat, receivers or lightsources.
     * @param {THREE.Object3D} object the object you want to add.
     */
    async addObject(object) {
        const objectType = object.objectType;
        if (!objectType) {
            return this;
        }

        switch (objectType) {
            case ObjectType.HELIOSTAT:
                this.#selectableGroup.add(object);
                object.apiID = (
                    await this.#saveAndLoadHandler.createHeliostat(object)
                )["id"];
                break;
            case ObjectType.RECEIVER:
                this.#selectableGroup.add(object);
                object.apiID = (
                    await this.#saveAndLoadHandler.createReceiver(object)
                )["id"];
                break;
            case ObjectType.LIGHTSOURCE:
                this.#selectableGroup.add(object);
                object.apiID = (
                    await this.#saveAndLoadHandler.createLightSource(object)
                )["id"];
                break;
            default:
                console.warn(`Unknown object type: ${objectType}`);
                break;
        }

        return this;
    }

    /**
     * Deletes the given object from the scene and from the database.
     * Only allows deletion of heliostat, receivers and lightsources.
     * @param {THREE.Object3D} object the object you want to delete.
     */
    async deleteObject(object) {
        const objectType = object.objectType;
        if (!objectType) {
            return this;
        }

        switch (objectType) {
            case ObjectType.HELIOSTAT:
                this.#selectableGroup.remove(object);
                await this.#saveAndLoadHandler.deleteHeliostat(object);
                break;
            case ObjectType.RECEIVER:
                this.#selectableGroup.remove(object);
                await this.#saveAndLoadHandler.deleteReceiver(object);
                break;
            case ObjectType.LIGHTSOURCE:
                this.#selectableGroup.remove(object);
                await this.#saveAndLoadHandler.deleteLightsource(object);
                break;
            default:
                console.warn(`Unknown object type: ${objectType}`);
                break;
        }

        return this;
    }

    /**
     * @returns {Array<THREE.Object3D>} an array containing all placed objects.
     */
    get objects() {
        return this.#selectableGroup.children;
    }
}

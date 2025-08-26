"""A module for managing hdf5 files in Canvas."""

import os
import pathlib

import h5py
import torch
from artist.data_loader import stral_loader
from artist.scenario.configuration_classes import (
    ActuatorConfig,
    ActuatorPrototypeConfig,
    HeliostatConfig,
    HeliostatListConfig,
    KinematicPrototypeConfig,
    LightSourceConfig,
    LightSourceListConfig,
    PowerPlantConfig,
    PrototypeConfig,
    SurfacePrototypeConfig,
    TargetAreaConfig,
    TargetAreaListConfig,
)
from artist.scenario.h5_scenario_generator import H5ScenarioGenerator
from artist.scenario.surface_generator import SurfaceGenerator
from artist.util import config_dictionary, set_logger_config
from django.conf import settings
from django.contrib.auth.models import User

from canvas import message_dict, path_dict
from canvas.test_constants import (
    ACTUATOR_NAME,
    ACTUATOR_NAME_2,
    CURVATURE_DEFAULT,
    HELIOSTAT_NAME_1,
    HOMOGENEOUS_COORDINATE,
    KINEMATIC_PROTOTYPE_CONFIG,
    NURBS_FIT_SCHEDULER_PARAMS,
    POSITION_COORDINATE_X,
    POSITION_COORDINATE_Y,
    POSITION_COORDINATE_Z,
)
from project_management.models import Heliostat, LightSource, Project, Receiver


class HDF5Manager:
    """Manages hdf5 file. Creates or reads hdf5 files compatible with ARTIST.

    Methods
    -------
    create_hdf5_file
    create_project_from_hdf5_file

    """

    # Helper function to safely extract values from datasets
    # in case they are None or not in the expected format.
    # Returns the default value if the dataset is None or cannot be converted.
    @staticmethod
    def safe_val(x, default=0.0):
        """
        Safely extract the value from a dataset, returning a default if None or invalid.
        """
        if x is None:
            return default
        try:
            return x[()]
        except TypeError:
            return x

    def create_hdf5_file(self, user: User, project: Project) -> None:
        """Create a HDF5 file for the given project.

        Parameters
        ----------
        user : User
            The user associated with the project.
        project : Project
            The project to be converted to an HDF5 file.

        """

        # Set up logger.
        set_logger_config()

        device = self._pick_device()

        scenario_path = self._prepare_paths(user, project)

        # Include the power plant configuration.
        power_plant_config = PowerPlantConfig(
            power_plant_position=torch.tensor([0.0, 0.0, 0.0], device=device)
        )

        # Include the target area configuration.
        target_area_list_config = self._create_target_area_config(
            project=project, device=device
        )

        # Include the light source configuration.
        light_source_list_config = self._create_light_source_config(
            project=project, device=device
        )

        # Include the prototype configuration.
        prototype_config = self._create_prototype_config(device=device)

        # Include the heliostat prototype config.
        heliostats_list_config = self._create_heliostat_config(
            project=project, device=device
        )

        # Initialize the scenario generator with the provided configurations.
        scenario_generator = H5ScenarioGenerator(
            file_path=scenario_path,
            power_plant_config=power_plant_config,
            target_area_list_config=target_area_list_config,
            light_source_list_config=light_source_list_config,
            prototype_config=prototype_config,
            heliostat_list_config=heliostats_list_config,
        )
        # Generate the scenario and save it to the specified HDF5 file.
        scenario_generator.generate_scenario()

    def _pick_device(self) -> torch.device:
        """
        Pick the device for tensor operations, either CPU or CUDA if available.
        """
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")

    def _prepare_paths(self, user: User, project: Project) -> pathlib.Path:
        """Prepare the paths for saving the scenario file."""

        scenario_dir = pathlib.Path("./hdf5_management/scenarios")
        # Check if scenario folder exists
        os.makedirs(scenario_dir, exist_ok=True)

        # The following parameter is the name of the scenario.
        scenario_path = pathlib.Path(
            f"{scenario_dir}/{user.id}_{project.name}{path_dict.SCENARIO_FILE_SUFFIX}"
        )
        # This checks to make sure the path you defined is valid and a scenario HDF5 can be saved there.
        if not pathlib.Path(scenario_path).parent.is_dir():
            raise FileNotFoundError(
                message_dict.folder_not_found_text.format(
                    pathlib.Path(scenario_path).parent
                )
            )

        return scenario_path

    def _create_surface_prototype_from_stral(
        self, device: torch.device
    ) -> SurfacePrototypeConfig:
        """
        Build the surface prototype configuration from a STRAL file.
        """
        # Set CANVAS_ROOT
        canvas_root = settings.BASE_DIR

        stral_file_path = canvas_root / path_dict.TEST_STRAL_DATA_PATH

        (
            facet_translation_vectors,
            canting,
            surface_points_with_facets_list,
            surface_normals_with_facets_list,
        ) = stral_loader.extract_stral_deflectometry_data(
            stral_file_path=stral_file_path, device=device
        )

        # Generate surface configuration from STRAL data.
        surface_generator = SurfaceGenerator(device=device)

        # Please leave the optimizable parameters empty, they will automatically be added for the surface fit.
        nurbs_fit_optimizer = torch.optim.Adam(
            [torch.empty(1, requires_grad=True)], lr=1e-3
        )
        nurbs_fit_scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
            nurbs_fit_optimizer, **NURBS_FIT_SCHEDULER_PARAMS
        )

        # Use this surface config for fitted deflectometry surfaces.
        surface_config = surface_generator.generate_fitted_surface_config(
            heliostat_name=HELIOSTAT_NAME_1,
            facet_translation_vectors=facet_translation_vectors,
            canting=canting,
            surface_points_with_facets_list=surface_points_with_facets_list,
            surface_normals_with_facets_list=surface_normals_with_facets_list,
            optimizer=nurbs_fit_optimizer,
            scheduler=nurbs_fit_scheduler,
            device=device,
        )

        # Use this surface configuration for ideal surfaces.
        # surface_config = surface_generator.generate_ideal_surface_config(
        #     facet_translation_vectors=facet_translation_vectors,
        #     canting=canting,
        #     device=device,
        # )
        surface_prototype_config = SurfacePrototypeConfig(
            facet_list=surface_config.facet_list
        )
        return surface_prototype_config

    def _create_prototype_config(self, device: torch.device) -> PrototypeConfig:
        """
        Build the prototype configuration for the project.
        """

        # Build the surface prototype from the STRAL file.
        surface_prototype_config = self._create_surface_prototype_from_stral(
            device=device
        )

        # Include the kinematic prototype configuration.
        kinematic_prototype_config = KinematicPrototypeConfig(
            type=config_dictionary.rigid_body_key,
            initial_orientation=torch.tensor(KINEMATIC_PROTOTYPE_CONFIG),
        )

        # Include an ideal actuator.
        actuator1_prototype = ActuatorConfig(
            key=ACTUATOR_NAME,
            type=config_dictionary.ideal_actuator_key,
            clockwise_axis_movement=False,
        )

        # Include an ideal actuator.
        actuator2_prototype = ActuatorConfig(
            key=ACTUATOR_NAME_2,
            type=config_dictionary.ideal_actuator_key,
            clockwise_axis_movement=True,
        )

        # Create a list of actuators.
        actuator_prototype_list = [actuator1_prototype, actuator2_prototype]

        # Include the actuator prototype config.
        actuator_prototype_config = ActuatorPrototypeConfig(
            actuator_list=actuator_prototype_list
        )

        # Include the final prototype config.
        prototype_config = PrototypeConfig(
            surface_prototype=surface_prototype_config,
            kinematic_prototype=kinematic_prototype_config,
            actuators_prototype=actuator_prototype_config,
        )
        return prototype_config

    def _create_target_area_config(self, project: Project, device: torch.device):
        """
        Build the target area configuration for the project.
        """

        # Create list for target area (receiver) configs
        target_area_config_list = []

        # Add all receivers to list
        for receiver in project.receivers.all():
            receiver_config = TargetAreaConfig(
                target_area_key=str(receiver),
                geometry=config_dictionary.target_area_type_planar,
                center=torch.tensor(
                    [
                        receiver.position_x,
                        receiver.position_y,
                        receiver.position_z,
                        1.0,
                    ],
                    device=device,
                ),
                normal_vector=torch.tensor(
                    [receiver.normal_x, receiver.normal_y, receiver.normal_z, 0.0],
                    device=device,
                ),
                plane_e=receiver.plane_e,
                plane_u=receiver.plane_u,
                curvature_e=receiver.curvature_e,
                curvature_u=receiver.curvature_u,
            )
            target_area_config_list.append(receiver_config)

        # Include the tower area configurations.
        target_area_list_config = TargetAreaListConfig(target_area_config_list)
        return target_area_list_config

    def _create_light_source_config(self, project: Project, device: torch.device):
        """
        Build the light source configuration for the project.
        """

        # Create a list of light source configs
        light_source_list = []

        # Add all light sources to list
        for light_source in project.light_sources.all():
            light_source_config = LightSourceConfig(
                light_source_key=str(light_source),
                light_source_type=light_source.light_source_type,
                number_of_rays=light_source.number_of_rays,
                distribution_type=light_source.distribution_type,
                mean=light_source.mean,
                covariance=light_source.covariance,
            )
            light_source_list.append(light_source_config)

        # Include the configuration for the list of light sources.
        light_source_list_config = LightSourceListConfig(
            light_source_list=light_source_list
        )
        return light_source_list_config

    def _create_heliostat_config(self, project: Project, device: torch.device):
        """
        Build the heliostat configuration for the project.
        """

        # Note, not all individual heliostat parameters are provided here

        # Generate the surface configuration.
        # For reasons of simplicity and the lack of Heliostat-surface attributes in this Canvas version,
        # the facet_prototype_list will be used here.
        # Due to this, the number of facettes will always be the one set in the stral-file in this version (=4).

        # Create a list of all heliostats
        heliostat_list = []

        # Add all heliostats to list
        for heliostat in project.heliostats.all():
            heliostat_config = HeliostatConfig(
                name=str(heliostat),
                id=heliostat.pk,
                position=torch.tensor(
                    [
                        heliostat.position_x,
                        heliostat.position_y,
                        heliostat.position_z,
                        HOMOGENEOUS_COORDINATE,
                    ],
                    device=device,
                ),
            )
            heliostat_list.append(heliostat_config)

        # Create the configuration for all heliostats.
        heliostats_list_config = HeliostatListConfig(heliostat_list=heliostat_list)
        return heliostats_list_config

    def create_project_from_hdf5_file(self, project_file: str, new_project: Project):
        """Create a project from a HDF5 file.

        Parameters
        ----------
        project_file: str
            The path to the HDF5 file
        new_project: Project
            The project in which the data is to be stored

        """
        with h5py.File(project_file, "r") as hdf5_file:
            # create the heliostats from the hdf5 file
            self._create_heliostats_from_hdf5_file(
                h5f=hdf5_file, new_project=new_project
            )
            # creates the light sources from the hdf5 file
            self._create_light_sources_from_hdf5_file(
                h5f=hdf5_file, new_project=new_project
            )
            # creates the receivers from the hdf5 file
            self._create_receivers_from_hdf5_file(
                h5f=hdf5_file, new_project=new_project
            )

    def _create_heliostats_from_hdf5_file(self, h5f: h5py.File, new_project: Project):
        """
        Create heliostats from a HDF5 file.
        """

        heliostats_group: h5py.Group = h5f.get(config_dictionary.heliostat_key)
        if heliostats_group is not None:
            for heliostat_object in heliostats_group:
                heliostat = heliostats_group[heliostat_object]

                position = heliostat[config_dictionary.heliostat_position]
                position_x = position[POSITION_COORDINATE_X]
                position_y = position[POSITION_COORDINATE_Y]
                position_z = position[POSITION_COORDINATE_Z]

                Heliostat.objects.create(
                    project=new_project,
                    name=str(heliostat_object),
                    position_x=position_x,
                    position_y=position_y,
                    position_z=position_z,
                )

    def _create_light_sources_from_hdf5_file(
        self, h5f: h5py.File, new_project: Project
    ):
        """
        Create light sources from a HDF5 file.
        """
        light_sources_group: h5py.Group = h5f.get(config_dictionary.light_source_key)
        if light_sources_group is not None:
            for light_source_object in light_sources_group:
                light_source = light_sources_group[light_source_object]
                number_of_rays = light_source[
                    config_dictionary.light_source_number_of_rays
                ]
                light_source_type = light_source[config_dictionary.light_source_type]

                distribution_params = light_source[
                    config_dictionary.light_source_distribution_parameters
                ]
                covariance = distribution_params[
                    config_dictionary.light_source_covariance
                ]
                distribution_type = distribution_params[
                    config_dictionary.light_source_distribution_type
                ]
                mean = distribution_params[config_dictionary.light_source_mean]

                LightSource.objects.create(
                    project=new_project,
                    name=str(light_source_object),
                    number_of_rays=number_of_rays[()],
                    light_source_type=light_source_type[()].decode("utf-8"),
                    covariance=covariance[()],
                    distribution_type=distribution_type[()].decode("utf-8"),
                    mean=mean[()],
                )

    def _create_receivers_from_hdf5_file(self, h5f: h5py.File, new_project: Project):
        """
        Create receivers from a HDF5 file.
        """
        receivers_group: h5py.Group = h5f.get(config_dictionary.target_area_key)
        if receivers_group is not None:
            for receiver_object in receivers_group:
                receiver = receivers_group[receiver_object]

                position = receiver[config_dictionary.target_area_position_center]
                position_x = position[POSITION_COORDINATE_X]
                position_y = position[POSITION_COORDINATE_Y]
                position_z = position[POSITION_COORDINATE_Z]

                normal = receiver[config_dictionary.target_area_normal_vector]
                normal_x = normal[POSITION_COORDINATE_X]
                normal_y = normal[POSITION_COORDINATE_Y]
                normal_z = normal[POSITION_COORDINATE_Z]

                plane_e = receiver[config_dictionary.target_area_plane_e]
                plane_u = receiver[config_dictionary.target_area_plane_u]

                # Optional datasets (often absent for planar target areas)
                curv_e_ds = receiver.get(config_dictionary.target_area_curvature_e)
                curv_u_ds = receiver.get(config_dictionary.target_area_curvature_u)

                curvature_e = HDF5Manager.safe_val(curv_e_ds, default=CURVATURE_DEFAULT)
                curvature_u = HDF5Manager.safe_val(curv_u_ds, default=CURVATURE_DEFAULT)

                Receiver.objects.create(
                    project=new_project,
                    name=str(receiver_object),
                    position_x=position_x,
                    position_y=position_y,
                    position_z=position_z,
                    normal_x=normal_x,
                    normal_y=normal_y,
                    normal_z=normal_z,
                    plane_e=plane_e[()],
                    plane_u=plane_u[()],
                    curvature_e=curvature_e,
                    curvature_u=curvature_u,
                )

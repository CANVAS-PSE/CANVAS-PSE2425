import pathlib
import torch
from artist.util import config_dictionary, set_logger_config
from artist.util.configuration_classes import (
    ActuatorConfig,
    ActuatorPrototypeConfig,
    SurfaceConfig,
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
from artist.util.scenario_generator import (
    ActuatorListConfig,
    KinematicConfig,
    ScenarioGenerator,
)
from artist.util.surface_converter import SurfaceConverter
from project_management.models import Heliostat, Lightsource, Project, Receiver
import h5py
from django.conf import settings
from django.contrib.auth.models import User


class HDF5Manager:
    def create_hdf5_file(self, user: User, project: Project):
        """
        Creates the actual HDF5 file

        Parameters
        ----------
        project : Project
            The project which is to be converted into an HDF5 file

        Returns
        -------
        HDF5File????
        """

        #
        # General Setup
        #

        # Set CANVAS_ROOT
        CANVAS_ROOT = settings.BASE_DIR

        # Set up logger.
        set_logger_config()

        # Set the device.
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # The following parameter is the name of the scenario.
        scenario_path = pathlib.Path(
            f"./HDF5Management/scenarios/{user.id}_{project.name}ScenarioFile"
        )

        # This checks to make sure the path you defined is valid and a scenario HDF5 can be saved there.
        if not pathlib.Path(scenario_path).parent.is_dir():
            raise FileNotFoundError(
                f"The folder ``{pathlib.Path(scenario_path).parent}`` selected to save the scenario does not exist. "
                "Please create the folder or adjust the file path before running again!"
            )

        # The path to the stral file containing heliostat and deflectometry data.
        stral_file_path = (
            pathlib.Path(CANVAS_ROOT) / "HDF5Management/data/test_stral_data.binp"
        )

        # Include the power plant configuration.
        power_plant_config = PowerPlantConfig(
            power_plant_position=torch.tensor([0.0, 0.0, 0.0], device=device)
        )

        #
        # Receiver(s)
        #

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
            )
            target_area_config_list.append(receiver_config)

        # Include the tower area configurations.
        target_area_list_config = TargetAreaListConfig(target_area_config_list)

        #
        # Light source(s)
        #

        # Create a list of light source configs
        light_source_list = []

        # Add all light sources to list
        for light_source in project.lightsources.all():
            light_source_config = LightSourceConfig(
                light_source_key=str(light_source),
                light_source_type=light_source.lightsource_type,
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

        #
        # Prototype
        #

        # Generate surface configuration from STRAL data.
        # max_epoch set to 100 for a faster scenario file creation
        surface_converter = SurfaceConverter(
            max_epoch=100,
        )
        facet_prototype_list = surface_converter.generate_surface_config_from_stral(
            stral_file_path=stral_file_path, device=device
        )

        # Generate the surface prototype configuration.
        surface_prototype_config = SurfacePrototypeConfig(
            facet_list=facet_prototype_list
        )

        # Note that we do not include kinematic deviations in this scenario!
        # Include the kinematic prototype configuration.
        kinematic_prototype_config = KinematicPrototypeConfig(
            type=config_dictionary.rigid_body_key,
            initial_orientation=torch.tensor([0.0, 0.0, 1.0, 0.0], device=device),
        )

        # Include an ideal actuator.
        actuator1_prototype = ActuatorConfig(
            key="actuator_1",
            type=config_dictionary.ideal_actuator_key,
            clockwise_axis_movement=False,
        )

        # Include a second ideal actuator.
        actuator2_prototype = ActuatorConfig(
            key="actuator_2",
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

        #
        # Heliostat(s)
        #

        # Note, not all individual heliostat parameters are provided here

        # Generate the surface configuration.
        # For reasons of simplicity and the lack of Heliostat-surface attributes in this Canvas version,
        # the facet_prototype_list will be used here.
        # Due to this, the number of facettes will always be the one set in the stral-file in this version (=4).
        surface_config = SurfaceConfig(facet_list=facet_prototype_list)

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
                        1.0,
                    ],
                    device=device,
                ),
                aim_point=torch.tensor(
                    [
                        heliostat.aimpoint_x,
                        heliostat.aimpoint_y,
                        heliostat.aimpoint_z,
                        1.0,
                    ],
                    device=device,
                ),
                surface=surface_config,
                kinematic=KinematicConfig(
                    type=config_dictionary.rigid_body_key,
                    initial_orientation=torch.tensor(
                        [0.0, 0.0, 1.0, 0.0], device=device
                    ),
                ),
                actuators=ActuatorListConfig(actuator_list=actuator_prototype_list),
            )
            heliostat_list.append(heliostat_config)

        # Create the configuration for all heliostats.
        heliostats_list_config = HeliostatListConfig(heliostat_list=heliostat_list)

        #
        # Generate the scenario HDF5 file given the defined parameters
        #

        scenario_generator = ScenarioGenerator(
            file_path=scenario_path,
            power_plant_config=power_plant_config,
            target_area_list_config=target_area_list_config,
            light_source_list_config=light_source_list_config,
            prototype_config=prototype_config,
            heliostat_list_config=heliostats_list_config,
        )
        scenario_generator.generate_scenario()

    def create_project_from_hdf5_file(self, project_file: str, new_project: Project):
        with h5py.File(project_file, "r") as f:
            heliostats_group: h5py.Group = f.get("heliostats")
            if heliostats_group is not None:
                for heliostat_object in heliostats_group:
                    heliostat = heliostats_group[heliostat_object]

                    aimpoint = heliostat["aim_point"]
                    aimpoint_x = aimpoint[0]
                    aimpoint_y = aimpoint[1]
                    aimpoint_z = aimpoint[2]

                    position = heliostat["position"]
                    position_x = position[0]
                    position_y = position[1]
                    position_z = position[2]

                    surface = heliostat["surface"]
                    facets = surface["facets"]
                    number_of_facets = len(facets.keys())

                    Heliostat.objects.create(
                        project=new_project,
                        name=str(heliostat_object),
                        position_x=position_x,
                        position_y=position_y,
                        position_z=position_z,
                        aimpoint_x=aimpoint_x,
                        aimpoint_y=aimpoint_y,
                        aimpoint_z=aimpoint_z,
                        number_of_facets=number_of_facets,
                    )

            # powerplant_group: h5py.Group = f.get("power_plant")
            # if powerplant_group is not None:
            #     pass
            # # At the moment there is no powerPlant position stored with a scenario in CANVAS
            #
            # prototypes_group: h5py.Group = f.get("prototypes")
            # if prototypes_group is not None:
            #     pass
            #     # Placeholder for when prototypes are effectively used

            lightsources_group: h5py.Group = f.get("lightsources")
            if lightsources_group is not None:
                for lightsource_object in lightsources_group:
                    lightsource = lightsources_group[lightsource_object]
                    number_of_rays = lightsource["number_of_rays"]
                    lightsource_type = lightsource["type"]

                    distribution_params = lightsource["distribution_parameters"]
                    covariance = distribution_params["covariance"]
                    distribution_type = distribution_params["distribution_type"]
                    mean = distribution_params["mean"]

                    Lightsource.objects.create(
                        project=new_project,
                        name=str(lightsource_object),
                        number_of_rays=number_of_rays[()],
                        lightsource_type=lightsource_type[()].decode("utf-8"),
                        covariance=covariance[()],
                        distribution_type=distribution_type[()].decode("utf-8"),
                        mean=mean[()],
                    )

            receivers_group: h5py.Group = f.get("target_areas")
            if receivers_group is not None:
                for receiver_object in receivers_group:
                    receiver = receivers_group[receiver_object]

                    position = receiver["position_center"]
                    position_x = position[0]
                    position_y = position[1]
                    position_z = position[2]

                    normal = receiver["normal_vector"]
                    normal_x = normal[0]
                    normal_y = normal[1]
                    normal_z = normal[2]

                    plane_e = receiver["plane_e"]
                    plane_u = receiver["plane_u"]

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
                    )

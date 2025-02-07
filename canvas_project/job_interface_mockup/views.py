from .models import Job
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from .models import Project

import random

from django.conf import settings
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
from artist.util.scenario_generator import ScenarioGenerator
from artist.util.surface_converter import SurfaceConverter


# Create your views here.
@login_required
@require_http_methods(["POST", "GET"])
def createNewJob(request, project_id):
    project = get_object_or_404(Project, owner=request.user, pk=project_id)
    if request.method == "POST":
        newJob = Job.objects.create(owner=request.user, project=project)
        return JsonResponse({"jobID": newJob.pk})
    if request.method == "GET":
        jobs = Job.objects.filter(owner=request.user, project=project).order_by(
            "starting_time"
        )
        job_ids = [job.pk for job in jobs]
        return JsonResponse({"jobIDs": job_ids})


@login_required
@require_http_methods(["DELETE", "GET"])
def getJobStatus(request, jobID, project_id):
    project = get_object_or_404(Project, owner=request.user, pk=project_id)
    if request.method == "GET":
        job = get_object_or_404(Job, pk=jobID, owner=request.user, project=project)

        starting_time = job.starting_time

        time_diff = (timezone.now() - starting_time).total_seconds() / 60

        result = None
        if time_diff > 3:
            progress = 1
        else:
            progress = round(time_diff / 3, 2)

        if time_diff > 3:
            status = "Finished"
            result = f"/static/img/render/example_{random.randint(1, 19)}.pdf"
        elif time_diff > 2:
            status = "Aligning Heliostats"
        elif time_diff > 1:
            status = "Creating HDF5 file"
        else:
            status = "Creating HDF5 file"

        return JsonResponse(
            {
                "jobID": job.pk,
                "status": status,
                "progress": progress,
                "result": result,
            }
        )
    if request.method == "DELETE":
        job = get_object_or_404(Job, pk=jobID, owner=request.user, project=project)
        job.delete()

        return HttpResponse(status=200)


def createHDF5(project):
    """
    This function creates an HDF5 file from a given project.
    It can be called with the project/ scenario that is to be rendered as an argument.
    The HDF5 file will be stored at the location defined below (scenario_path variable).

    This mock-up however does not use this function but returns a faked status. This is due
    to the fact, that, in a later version of Canvas, this mock-up will be entirely replaced with
    an interface to Artist. Artist will then be responsible for the HDF5 generation and
    will require the scenario that is to be rendered as an argument.
    Therefore this function is to be seen as an instruction/ indicator on how the scenario creation can
    work in a later version.
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
    scenario_path = pathlib.Path(CANVAS_ROOT) / "./hdfCreation/scenarios/scenarioFile"

    # This checks to make sure the path you defined is valid and a scenario HDF5 can be saved there.
    if not pathlib.Path(scenario_path).parent.is_dir():
        raise FileNotFoundError(
            f"The folder ``{pathlib.Path(scenario_path).parent}`` selected to save the scenario does not exist. "
            "Please create the folder or adjust the file path before running again!"
        )

    # The path to the stral file containing heliostat and deflectometry data.
    stral_file_path = (
        pathlib.Path(CANVAS_ROOT) / "hdfCreation/data/test_stral_data.binp"
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
                [receiver.position_x, receiver.position_y, receiver.position_z, 1.0],
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
    for lightSource in project.lightsources.all():
        light_source_config = LightSourceConfig(
            light_source_key=str(lightSource),
            light_source_type=lightSource.lightsource_type,
            number_of_rays=lightSource.number_of_rays,
            distribution_type=lightSource.distribution_type,
            mean=lightSource.mean,
            covariance=lightSource.covariance,
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
    # max_epoch set to 100 for a faster scenario file creation.
    surface_converter = SurfaceConverter(
        max_epoch=100,
    )
    facet_prototype_list = surface_converter.generate_surface_config_from_stral(
        stral_file_path=stral_file_path, device=device
    )

    # Generate the surface prototype configuration.
    surface_prototype_config = SurfacePrototypeConfig(facet_list=facet_prototype_list)

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
                [heliostat.position_x, heliostat.position_y, heliostat.position_z, 1.0],
                device=device,
            ),
            aim_point=torch.tensor(
                [heliostat.aimpoint_x, heliostat.aimpoint_y, heliostat.aimpoint_z, 1.0],
                device=device,
            ),
            surface=surface_config,
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

    return True

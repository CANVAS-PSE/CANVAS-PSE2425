from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from project_management.models import Project
from django.urls import reverse
from project_management.forms import ProjectForm
from django.http import FileResponse, HttpResponse, Http404

from django.conf import settings

from django.conf import settings
import pathlib
import torch
from artist.util import config_dictionary, set_logger_config
from artist.util.configuration_classes import (
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
from artist.util.scenario_generator import ScenarioGenerator
from artist.util.surface_converter import SurfaceConverter


@login_required
def editor(request, project_name):
    """
    Handles the editor view for a given project.

    Parameters
    ----------
    request : HttpRequest
        The request the user send to get here.
    project_name : str
        The project_name specified as a url parameter.

    Returns
    -------
    HttpResponse
        The editor page where the user can edit the project.
    """

    if request.method == "GET":
        # Return 404 not found if user has no project with this id
        project = get_object_or_404(Project, name=project_name, owner=request.user)
        project.last_edited = timezone.now()
        project.save()

        createProjectForm = ProjectForm()
        allProjects = Project.objects.filter(owner=request.user).order_by(
            "-last_edited"
        )

        return render(
            request,
            "editor/editor.html",
            context={
                "project_id": project.pk,
                "project_name": project.name,
                "createProjectForm": createProjectForm,
                "projects": allProjects,
            },
        )
    elif request.method == "POST":
        form = ProjectForm(request.POST)

        # if valid redirect to new project
        if form.is_valid():
            nameUnique = True
            allProjects = Project.objects.filter(owner=request.user).order_by(
                "-last_edited"
            )
            new_project_name = form["name"].value()
            for existingProject in allProjects:
                if new_project_name == existingProject.name:
                    nameUnique = False
            if nameUnique:
                form = form.save(commit=False)
                form.owner = request.user
                form.last_edited = timezone.now()
                form.save()
                messages.success(request, "Successfully created the new project")
                return redirect("/editor/" + new_project_name)

        # if not render error message
        project = get_object_or_404(Project, name=project_name, owner=request.user)
        project.last_edited = timezone.now()
        project.save()

        createProjectForm = ProjectForm()
        allProjects = Project.objects.filter(owner=request.user).order_by(
            "-last_edited"
        )

        messages.error(
            request,
            "A project with this name already exists. Please choose a different name.",
        )

        return render(
            request,
            "editor/editor.html",
            context={
                "project_id": project.pk,
                "project_name": project.name,
                "createProjectForm": createProjectForm,
                "projects": allProjects,
            },
        )


@login_required
def download(request, project_name):
    """
    Converts the specified project into an hdf5 file and downloads it.

    Parameters
    ----------
    request : HttpRequest
        The request the user send to get here.
    project_name : str
        The project_name specified as a url parameter.

    Returns
    -------
    HttpResponse
        FileResponse to download the hdf5 file.
    """

    project = get_object_or_404(Project, name=project_name, owner=request.user)

    # Set CANVAS_ROOT
    CANVAS_ROOT = settings.BASE_DIR

    path = pathlib.Path(CANVAS_ROOT) / "./hdfCreation/scenarios/scenarioFile.h5"

    createHDF5(project)

    response = FileResponse(
        open(path, "rb"), as_attachment=True, filename=project.name + ".h5"
    )

    return response


@login_required
def renderHDF5(request, project_name):
    """
        Renders the specified project into an hdf5 file and sends it to the JobInterface.


        Parameters
        ----------
        request : HttpRequest
            The request the user send to get here.
    <<<<<<< HEAD
        project_name : str
            The project_name specified as a url parameter.

        Returns
        -------
        HttpResponse
            ...
    """

    project = get_object_or_404(Project, name=project_name, owner=request.user)

    if request.method == "POST":
        createHDF5(project)
        return redirect(reverse("editor", kwargs={"project_name": project_name}))

    return redirect(reverse("editor", kwargs={"project_name": project_name}))


@login_required
def uploadPreview(request, project_name):
    """
    Updates the preview of the project

    Parameters
    ----------
    request : HttpRequest
        The request the user send to get here.

    Returns
    -------
    HttpResponse : status 200
        On successfull POST request
    HttpResponse : status 404
        on all other occasions
    """

    if request.method == "POST":
        project = get_object_or_404(Project, name=project_name, owner=request.user)
        file = request.FILES["preview"]

        project.preview.delete()
        project.preview = file
        project.save()

        return HttpResponse(status=200)
    return Http404


def createHDF5(project):
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
    # Probably needs more specific config
    #

    # Generate surface configuration from STRAL data.
    surface_converter = SurfaceConverter(
        max_epoch=400,
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

    # Note, not all individual heliostat parameters are provided here, but set via the prototype

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

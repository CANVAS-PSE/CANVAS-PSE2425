from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.urls import reverse
from .models import Project, Heliostat, Lightsource, Receiver
from django.shortcuts import redirect, render, get_object_or_404
from .forms import ProjectForm, UpdateProjectForm
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User

import h5py


# General project handling
@login_required
def projects(request):
    if request.method == "POST":
        # Initialize the form with POST and FILE data
        form = ProjectForm(request.POST, request.FILES)

        # Check if form is valid before proceeding
        if form.is_valid():
            projectFile = request.FILES.get("file")
            projectName = form.cleaned_data["name"].strip().replace(" ", "_")
            projectDescription = (
                form.cleaned_data["description"].strip()
                if form.cleaned_data["description"]
                else ""
            )

            # If no file is uploaded, handle the project creation without the file
            if projectFile is None:
                allProjects = Project.objects.filter(owner=request.user)
                nameUnique = True
                for existingProject in allProjects:
                    if (
                        existingProject.name == projectName
                        and existingProject.owner == request.user
                    ):
                        nameUnique = False
                        break

                if nameUnique:
                    newProject = Project(
                        name=projectName,
                        description=projectDescription,
                        owner=request.user,
                        last_edited=timezone.now(),
                    )
                    newProject.save()
                    return redirect("editor", project_name=projectName)

            # Handle file upload (e.g., HDF5 file)
            else:
                allProjects = Project.objects.filter(owner=request.user)
                nameUnique = True
                for existingProject in allProjects:
                    if (
                        existingProject.name == projectName
                        and existingProject.owner == request.user
                    ):
                        nameUnique = False
                        break

                if nameUnique:
                    newProject = Project(
                        name=projectName,
                        description=projectDescription,
                        owner=request.user,
                        last_edited=timezone.now(),
                    )
                    newProject.save()
                    openHDF5_CreateProject(projectFile, newProject)
                    return redirect("editor", project_name=projectName)

    else:  # GET request
        form = ProjectForm()

    # Fetch all projects for the current user
    allProjects = Project.objects.filter(owner=request.user).order_by("-last_edited")
    for project in allProjects:
        project.uid = _generate_uid(request)
        project.token = _generate_token(project.name)

    context = {
        "projects": allProjects,
        "form": form,
    }
    return render(request, "project_management/projects.html", context)


@login_required
def updateProject(request, project_name):
    project = Project.objects.get(owner=request.user, name=project_name)
    form = UpdateProjectForm(request.POST, instance=project)
    if request.method == "POST":
        if project.owner == request.user:
            if form.is_valid:
                allProjects = Project.objects.all()
                nameUnique = True
                nameChanged = True
                formName = form["name"].value()
                formName = formName.replace(" ", "_")
                formDescription = form["description"].value()
                if project_name == formName:
                    nameChanged = False
                for existingProject in allProjects:
                    if formName == existingProject.name:
                        nameUnique = False
                if nameUnique or not nameChanged:
                    project.last_edited = timezone.now()
                    project.name = formName
                    if formDescription is None:
                        project.description = ""
                    else:
                        project.description = formDescription
                    project.save()
                    return HttpResponseRedirect(reverse("projects"))
                return redirect("projects")
    return render(
        request,
        "project_management/projects.html",
        {"form": form, project_name: project_name},
    )


# Deleting a project
@login_required
def deleteProject(request, project_name):
    project = Project.objects.get(owner=request.user, name=project_name)
    if project.owner == request.user:
        project.delete()
        return redirect("projects")


# Set project to favorite
@login_required
def favorProject(request, project_name):
    project = Project.objects.get(owner=request.user, name=project_name)
    if project.owner == request.user:
        project.favorite = "true"
        project.save(update_fields=["favorite"])
        return redirect("projects")


# Set project to not favorite
@login_required
def defavorProject(request, project_name):
    project = Project.objects.get(owner=request.user, name=project_name)
    if project.owner == request.user:
        project.favorite = "false"
        project.save(update_fields=["favorite"])
        return redirect("projects")


# Duplicate a project
@login_required
def duplicateProject(request, project_name):
    project = Project.objects.get(owner=request.user, name=project_name)
    if project.owner == request.user:
        fks_to_copy = (
            list(project.heliostats.all())
            + list(project.receivers.all())
            + list(project.lightsources.all())
        )
        settings = project.settings
        project.pk = None

        # Finding a new project name unique to user
        newNameFound = False
        while not newNameFound:
            try:
                Project.objects.get(name=project_name, owner=request.user)
                project_name = project_name + "_copy"
            except Project.DoesNotExist:
                project.name = project_name
                project.save()
                newNameFound = True

        # Copy all objects associated to the project via foreign keys
        for assoc_object in fks_to_copy:
            assoc_object.pk = None
            assoc_object.project = project
            assoc_object.save()

        # Copy settings
        settings.pk = None
        settings.project = project
        settings.save()

        return redirect("projects")


def openHDF5_CreateProject(projectFile, newProject):
    with h5py.File(projectFile, "r") as f:
        heliostatsGroup = f.get("heliostats")
        if heliostatsGroup is not None:
            for heliostatObject in heliostatsGroup:
                heliostat = heliostatsGroup[heliostatObject]

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
                numberOfFacets = len(facets.keys())

                Heliostat.objects.create(
                    project=newProject,
                    name=str(heliostatObject),
                    position_x=position_x,
                    position_y=position_y,
                    position_z=position_z,
                    aimpoint_x=aimpoint_x,
                    aimpoint_y=aimpoint_y,
                    aimpoint_z=aimpoint_z,
                    number_of_facets=numberOfFacets,
                )

        powerplantGroup = f.get("power_plant")
        if powerplantGroup is not None:
            pass
        # At the moment there is no powerPlant position stored with a scenario in CANVAS

        prototypesGroup = f.get("prototypes")
        if prototypesGroup is not None:
            pass
            # Placeholder for when prototypes are effectively used

        lightsourcesGroup = f.get("lightsources")
        if lightsourcesGroup is not None:
            for lightsourceObject in lightsourcesGroup:
                lightsource = lightsourcesGroup[lightsourceObject]
                numberOfRays = lightsource["number_of_rays"]
                lightsourceType = lightsource["type"]

                distributionParams = lightsource["distribution_parameters"]
                covariance = distributionParams["covariance"]
                distributionType = distributionParams["distribution_type"]
                mean = distributionParams["mean"]

                Lightsource.objects.create(
                    project=newProject,
                    name=str(lightsourceObject),
                    number_of_rays=numberOfRays[()],
                    lightsource_type=lightsourceType[()].decode("utf-8"),
                    covariance=covariance[()],
                    distribution_type=distributionType[()].decode("utf-8"),
                    mean=mean[()],
                )

        receiversGroup = f.get("target_areas")
        if receiversGroup is not None:
            for receiverObject in receiversGroup:
                receiver = receiversGroup[receiverObject]

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
                    project=newProject,
                    name=str(receiverObject),
                    position_x=position_x,
                    position_y=position_y,
                    position_z=position_z,
                    normal_x=normal_x,
                    normal_y=normal_y,
                    normal_z=normal_z,
                    plane_e=plane_e[()],
                    plane_u=plane_u[()],
                )


# Share a project
@login_required
def shareProject(request, project_name):
    # create new sharedProject model
    project = get_object_or_404(Project, owner=request.user, name=project_name)
    project.last_shared = timezone.now()
    project.save()
    return redirect("projects")


@login_required
def sharedProjects(request, uid, token):
    # get the shared project
    try:
        userID = urlsafe_base64_decode(uid).decode()
        user = get_user_model().objects.get(pk=userID)
        project_name = urlsafe_base64_decode(token).decode()
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        raise Http404

    project = get_object_or_404(Project, owner=user, name=project_name)

    if project.last_shared is None or (timezone.now() - project.last_shared).days > 3:
        raise Http404

    # render a preview where the user can choose to add the project
    if request.method == "GET":
        return render(
            request,
            "project_management/sharedProject.html",
            context={"project": project},
        )

    # copy the project to the user
    elif request.method == "POST":
        # copy the associated project to the user
        fks_to_copy = (
            list(project.heliostats.all())
            + list(project.receivers.all())
            + list(project.lightsources.all())
        )
        settings = project.settings
        project.pk = None

        # Finding a new project name unique to user
        newNameFound = False
        while not newNameFound:
            try:
                project.name = project.name + "_shared"
                Project.objects.get(name=project.name, owner=request.user)
            except Project.DoesNotExist:
                project.name = project.name
                project.owner = request.user
                project.save()
                newNameFound = True

        # Copy all objects associated to the project via foreign keys
        for assoc_object in fks_to_copy:
            assoc_object.pk = None
            assoc_object.project = project
            assoc_object.save()

        # Copy settings
        settings.pk = None
        settings.project = project
        settings.save()

        return redirect("projects")


def _generate_uid(request):
    return urlsafe_base64_encode(str(request.user.id).encode())


def _generate_token(project_name):
    return urlsafe_base64_encode(str(project_name).encode())

from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import redirect, render
from .models import Project, Heliostat, Lightsource, Receiver
from .forms import ProjectForm, UpdateProjectForm
from datetime import datetime
from django.contrib.auth.decorators import login_required

import h5py


# General project handling
@login_required
def projects(request):
    form = ProjectForm()
    projectFile = request.FILES.get("file")
    projectName = request.POST.get("name")
    projectDescription = request.POST.get("description")
    if request.method == "GET":
        allProjects = Project.objects.order_by("-last_edited")
        context = {"projects": allProjects, "form": form}
        return render(request, "project_management/projects.html", context)
    elif request.method == "POST":
        form = ProjectForm(request.POST)
        if projectFile is None:
            allProjects = Project.objects.all()
            if form.is_valid():
                nameUnique = True
                for existingProject in allProjects:
                    if (
                        form["name"].value() == existingProject.name
                        and existingProject.owner == request.user
                    ):
                        nameUnique = False
                if nameUnique:
                    newProject = Project(
                        name=projectName, description=projectDescription
                    )
                    newProject.owner = request.user
                    newProject.last_edited = datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                    newProject.save()
                    return redirect("editor", project_name=projectName)
        else:
            if form.is_valid():
                allProjects = Project.objects.all()
                nameUnique = True
                for existingProject in allProjects:
                    if projectName == existingProject.name and str(
                        (existingProject.owner) == request.user
                    ):
                        nameUnique = False

                if nameUnique:
                    newProject = Project(
                        name=projectName, description=projectDescription
                    )
                    newProject.owner = request.user
                    newProject.last_edited = datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                    newProject.save()
                    openHDF5_CreateProject(projectFile, newProject)
                    return redirect("editor", project_name=projectName)

        context = {"projects": allProjects, "form": form}
        return render(request, "project_management/projects.html", context)


@login_required
def updateProject(request, project_name):
    if request.method == "POST":
        project = Project.objects.get(owner=request.user, name=project_name)
        if project.owner == request.user:
            form = UpdateProjectForm(request.POST, instance=project)
            if form.is_valid:
                allProjects = Project.objects.all()
                nameUnique = True
                nameNotChanged = False
                if project_name == form["name"].value():
                    nameNotChanged = True
                for existingProject in allProjects:
                    if form["name"].value() == existingProject.name:
                        nameUnique = False
                if nameUnique or nameNotChanged:
                    project.last_edited = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    form.save()
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
                Project.objects.get(name=project_name)
                project_name = project_name + "copy"
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

                Heliostat.objects.create(
                    project=newProject,
                    name=str(heliostatObject),
                    position_x=position_x,
                    position_y=position_y,
                    position_z=position_z,
                    aimpoint_x=aimpoint_x,
                    aimpoint_y=aimpoint_y,
                    aimpoint_z=aimpoint_z,
                )

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
                    lightsource_type=lightsourceType[()],
                    covariance=covariance[()],
                    distribution_type=distributionType[()],
                    mean=mean[()],
                )

        powerplantGroup = f.get("power_plant")
        if powerplantGroup is not None:
            pass
        # At the moment there is no powerPlant position stored with a scenario in CANVAS

        prototypesGroup = f.get("prototypes")
        if prototypesGroup is not None:
            pass
        # Placeholder for when prototypes are effectively used

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

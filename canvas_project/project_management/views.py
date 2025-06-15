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
from django.contrib import messages
from HDF5Management.HDF5Manager import HDF5Manager
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
                else:
                    messages.error(request, "The project name must be unique.")

            # Handle file upload
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

                    hdf5Manager = HDF5Manager()
                    hdf5Manager.createProjectFromHDF5File(projectFile, newProject)

                    return redirect("editor", project_name=projectName)
                else:
                    messages.error(request, "The project name must be unique.")

        else:
            for field in form:
                for error in field.errors:
                    messages.error(request, f"Error in {field.label}: {error}")

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
    allProjects = Project.objects.filter(owner=request.user).order_by("-last_edited")
    if request.method == "POST":
        if project.owner == request.user:
            if form.is_valid():
                nameUnique = True
                nameChanged = True
                formName = form.cleaned_data["name"].strip().replace(" ", "_")
                formDescription = form.cleaned_data.get("description", "")
                if project_name == formName:
                    nameChanged = False
                for existingProject in allProjects:
                    if (
                        existingProject.owner == request.user
                        and formName == existingProject.name
                    ):
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
                else:
                    messages.error(request, "The project name must be unique.")

            else:
                for field in form:
                    for error in field.errors:
                        messages.error(request, f"Error in {field.label}: {error}")

    else:
        form = UpdateProjectForm(instance=project)

    return HttpResponseRedirect(reverse("projects"))


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
        project.favorite = False

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
        project.favorite = False

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

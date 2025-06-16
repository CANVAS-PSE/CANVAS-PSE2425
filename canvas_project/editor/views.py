import os
from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from HDF5Management.HDF5Manager import HDF5Manager
from project_management.forms import ProjectForm
from django.http import FileResponse, HttpResponse, Http404

from project_management.models import (
    Project,
)


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
        try:
            project = Project.objects.get(owner=request.user, name=project_name)
        except Project.DoesNotExist:
            messages.error(request, "Project doesn't exist")
            return redirect("projects")

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

    hdf5Manager = HDF5Manager()
    hdf5Manager.createHDF5File(request.user, project)

    # Set CANVAS_ROOT
    path = f"./HDF5Management/scenarios/{request.user.id}{project_name}ScenarioFile.h5"

    response = FileResponse(
        open(path, "rb"), as_attachment=True, filename=project_name + ".h5"
    )

    os.remove(path)

    return response


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
    raise Http404

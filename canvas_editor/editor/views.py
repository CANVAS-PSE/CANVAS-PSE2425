import os
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from hdf5_management.hdf5_manager import HDF5Manager
from django.contrib.auth.models import User
from project_management.forms import ProjectForm
from django.http import FileResponse, HttpResponse
from project_management.models import (
    Project,
)


@login_required
@require_GET
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

    try:
        project = Project.objects.get(owner=request.user, name=project_name)
    except Project.DoesNotExist:
        messages.error(request, "Project doesn't exist")
        return redirect("projects")

    project.last_edited = timezone.now()
    project.save()

    create_project_form = ProjectForm()
    all_projects = Project.objects.filter(owner=request.user).order_by("-last_edited")

    return render(
        request,
        "editor/editor.html",
        context={
            "project_id": project.pk,
            "project_name": project.name,
            "createProjectForm": create_project_form,
            "projects": all_projects,
        },
    )


def is_name_unique(user: User, project_name: str) -> bool:
    unique = True
    for project in user.projects.all():
        if project.name == project_name:
            unique = False
            break
    return unique


@login_required
@require_GET
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

    hdf5_manager = HDF5Manager()
    hdf5_manager.create_hdf5_file(request.user, project)

    # Set CANVAS_ROOT
    path = (
        f"./hdf5_management/scenarios/{request.user.id}_{project.name}ScenarioFile.h5"
    )

    f = open(path, "rb")
    response = FileResponse(f, as_attachment=True, filename=project_name + ".h5")

    original_close = response.close

    def close_and_cleanup(*args, **kwargs):
        try:
            try:
                if not f.closed:
                    f.close()
            finally:
                # Delete the temporary file after sending it
                try:
                    path.unlink()
                except FileNotFoundError:
                    pass
        finally:
            # <- IMPORTANT: Call Django's own close
            return original_close(*args, **kwargs)

    response.close = close_and_cleanup
    return response


@login_required
@require_POST
def upload_preview(request, project_name):
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

    project = get_object_or_404(Project, name=project_name, owner=request.user)
    file = request.FILES["preview"]

    project.preview.delete()
    project.preview = file
    project.save()

    return HttpResponse(status=200)

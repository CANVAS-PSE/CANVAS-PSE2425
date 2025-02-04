from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from project_management.models import Project
from django.http import FileResponse, HttpResponse, Http404

import os
from django.conf import settings


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

    # Return 404 not found if user has no project with this id
    project = get_object_or_404(Project, name=project_name, owner=request.user)
    project.last_edited = timezone.now()
    project.save()

    return render(
        request,
        "editor/editor.html",
        context={"project_id": project.pk, "project_name": project.name},
    )


@login_required
def download(request, project_name):
    """
    Converts the specified project into a hdf5 file and downloads it.

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

    # Placeholder for actual download functionality added later
    project = get_object_or_404(Project, name=project_name, owner=request.user)

    path = os.path.join(
        settings.BASE_DIR, "static/artist/test_scenario_alignment_optimization.h5"
    )
    response = FileResponse(open(path, "rb"))
    response["Content-Type"] = "application/octet-stream"
    response["Content-Disposition"] = f'attachment; filename="{project.name}.h5"'
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
    return Http404

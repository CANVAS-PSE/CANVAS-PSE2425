import os

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import FileResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views import View
from django.views.generic import TemplateView

from hdf5_management.hdf5_manager import HDF5Manager
from project_management.forms import ProjectForm
from project_management.models import (
    Project,
)


class EditorView(LoginRequiredMixin, TemplateView):
    """Render the editor view."""

    template_name = "editor/editor.html"

    def get_context_data(self, **kwargs):
        """Get the context of the editor page."""
        context = super().get_context_data(**kwargs)
        project_name = self.kwargs.get("project_name")
        request = self.request
        project = get_object_or_404(Project, owner=request.user, name=project_name)

        project.last_edited = timezone.now()
        project.save()

        create_project_form = ProjectForm()
        all_projects = Project.objects.filter(owner=request.user).order_by(
            "-last_edited"
        )

        context.update(
            {
                "project_id": project.pk,
                "project_name": project.name,
                "createProjectForm": create_project_form,
                "projects": all_projects,
            }
        )
        return context


class DownloadView(LoginRequiredMixin, View):
    """Converts the specified project into an hdf5 file and downloads it."""

    def get(self, request, project_name):
        """Create and download the hdf5 file."""
        project = get_object_or_404(Project, name=project_name, owner=request.user)

        hdf5_manager = HDF5Manager()
        hdf5_manager.create_hdf5_file(request.user, project)

        # Set CANVAS_ROOT
        path = f"./hdf5_management/scenarios/{request.user.id}_{project.name}ScenarioFile.h5"

        response = FileResponse(
            open(path, "rb"), as_attachment=True, filename=project_name + ".h5"
        )

        os.remove(path)

        return response


class UploadPreviewView(LoginRequiredMixin, View):
    """Updates the preview of the project."""

    def post(self, request, project_name):
        """Upload the previed for this project."""
        project = get_object_or_404(Project, name=project_name, owner=request.user)
        file = request.FILES["preview"]

        project.preview.delete()
        project.preview = file
        project.save()

        return HttpResponse(status=200)

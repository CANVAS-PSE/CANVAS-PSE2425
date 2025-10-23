import tempfile

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.views import View

from hdf5_management.hdf5_manager import HDF5Manager
from project_management.models import Project


class DownloadView(LoginRequiredMixin, View):
    """Converts the specified project into an hdf5 file and downloads it."""

    def get(self, request, project_name):
        """Create and download the hdf5 file."""
        project = get_object_or_404(Project, name=project_name, owner=request.user)

        # Use a temporary file that will be automatically deleted
        with tempfile.NamedTemporaryFile(delete=False, suffix=".h5") as tmp_file:
            HDF5Manager.create_hdf5_file(
                request.user, project, output_path=tmp_file.name
            )
            tmp_file.flush()
            tmp_file.seek(0)
            response = FileResponse(
                tmp_file, as_attachment=True, filename=f"{project_name}.h5"
            )

        return response

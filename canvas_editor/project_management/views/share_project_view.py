from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views import View

from project_management.models import Project
from canvas import view_name_dict


class ShareProjectView(LoginRequiredMixin, View):
    """Sharing a project."""

    def post(self, request, project_name):
        """Mark the last shared time point in the project."""
        project = get_object_or_404(Project, owner=request.user, name=project_name)
        project.last_shared = timezone.now()
        project.save()
        return redirect(view_name_dict.projects_view)

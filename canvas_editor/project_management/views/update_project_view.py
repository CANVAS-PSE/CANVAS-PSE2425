from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import FormView

from canvas import view_name_dict
from project_management.forms.update_project_form import UpdateProjectForm
from project_management.models import Project


class UpdateProjectView(LoginRequiredMixin, FormView):
    """Hanlde updating of a project."""

    template_name = view_name_dict.projects_view
    form_class = UpdateProjectForm
    http_method_names = ["post"]

    def get_success_url(self):
        """Get the url of the projects view at runtime."""
        return reverse(view_name_dict.projects_view)

    def get_form_kwargs(self):
        """Add the instance to the forms key word arguments."""
        kwargs = super().get_form_kwargs()
        kwargs["instance"] = Project.objects.get(
            owner=self.request.user, name=self.kwargs["project_name"]
        )
        return super().get_form_kwargs()

    def form_invalid(self, form):
        """Handle invalid update project form."""
        for field in form:
            for error in field.errors:
                messages.error(self.request, f"Error in {field.label}: {error}")

        return super().form_invalid(form)

    def form_valid(self, form):
        """Handle valid update project form."""
        form.save()

        return super().form_valid(form)

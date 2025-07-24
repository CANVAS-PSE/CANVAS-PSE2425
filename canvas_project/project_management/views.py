from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.views import View
from django.views.generic import ListView
from .models import Project
from django.shortcuts import redirect, render, get_object_or_404
from .forms import ProjectForm, UpdateProjectForm
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.contrib import messages
from hdf5_management.hdf5_manager import HDF5Manager

PROJECT_NAME_MUST_BE_UNIQUE_WARNING = "The project name must be unique"


class ProjectsView(LoginRequiredMixin, ListView):
    """
    Manages the displaying and creating of projects
    """

    model = Project
    template_name = "project_management/projects.html"
    context_object_name = "projects"

    def get_queryset(self):
        queryset = Project.objects.filter(owner=self.request.user).order_by(
            "-last_edited"
        )
        for project in queryset:
            project.uid = _generate_uid(self.request)
            project.token = _generate_token(project.name)
        return queryset

    def get_context_data(self, **kwargs):
        """
        Adds the ProjectForm to the context.
        """
        context = super().get_context_data(**kwargs)
        context["form"] = ProjectForm()
        return context

    def post(self, request):
        # Initialize the form with POST and FILE data
        form = ProjectForm(request.POST, request.FILES)

        # Check if form is valid before proceeding
        if form.is_valid() and is_name_unique(
            request.user, form.cleaned_data["name"].strip().replace(" ", "_")
        ):
            project_name = form.cleaned_data["name"].strip().replace(" ", "_")
            project_file = request.FILES.get("file")
            project_description = form.cleaned_data.get("description", "").strip()

            _create_project(
                request.user, project_name, project_description, project_file
            )

            return redirect("editor", project_name=project_name)

        else:
            messages.error(request, PROJECT_NAME_MUST_BE_UNIQUE_WARNING)
            for field in form:
                for error in field.errors:
                    messages.error(request, f"Error in {field.label}: {error}")

            context = self.get_context_data(object_list=self.get_queryset())
            context["form"] = form
            return render(request, "project_management/projects.html", context)


def _create_project(
    user: User, project_name: str, project_description: str, project_file
):
    new_project = Project(
        name=project_name,
        description=project_description,
        owner=user,
        last_edited=timezone.now(),
    )
    new_project.save()

    if project_file is not None:
        hdf5_manager = HDF5Manager()
        hdf5_manager.create_project_from_hdf5_file(project_file, new_project)


@login_required
@require_POST
def update_project(request, project_name):
    project = Project.objects.get(owner=request.user, name=project_name)
    form = UpdateProjectForm(request.POST, instance=project)

    if project.owner == request.user and form.is_valid():
        form_name = form.cleaned_data["name"].strip().replace(" ", "_")
        form_description = form.cleaned_data.get("description", "")
        if is_name_unique(request.user, form_name) or form_name == project_name:
            project.last_edited = timezone.now()
            project.name = form_name
            project.description = form_description if form_description else ""
            project.save()
            return HttpResponseRedirect(reverse("projects"))
        else:
            messages.error(request, PROJECT_NAME_MUST_BE_UNIQUE_WARNING)

    else:
        for field in form:
            for error in field.errors:
                messages.error(request, f"Error in {field.label}: {error}")

    return HttpResponseRedirect(reverse("projects"))


# Deleting a project
@login_required
@require_POST
def delete_project(request, project_name):
    project = Project.objects.get(owner=request.user, name=project_name)
    if project.owner == request.user:
        project.delete()
        return redirect("projects")


# Set project to favorite
@login_required
@require_POST
def favor_project(request, project_name):
    project = Project.objects.get(owner=request.user, name=project_name)
    if project.owner == request.user:
        project.favorite = "true"
        project.save(update_fields=["favorite"])
        return redirect("projects")


# Set project to not favorite
@login_required
@require_POST
def defavor_project(request, project_name):
    project = Project.objects.get(owner=request.user, name=project_name)
    if project.owner == request.user:
        project.favorite = "false"
        project.save(update_fields=["favorite"])
        return redirect("projects")


# Duplicate a project
@login_required
@require_POST
def duplicate_project(request, project_name):
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
        new_name_found = False
        while not new_name_found:
            try:
                Project.objects.get(name=project_name, owner=request.user)
                project_name = project_name + "_copy"
            except Project.DoesNotExist:
                project.name = project_name
                project.save()
                new_name_found = True

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
@require_POST
def share_project(request, project_name):
    # create new sharedProject model
    project = get_object_or_404(Project, owner=request.user, name=project_name)
    project.last_shared = timezone.now()
    project.save()
    return redirect("projects")


class SharedProjectView(LoginRequiredMixin, View):
    """
    Manages copying a shared project to the user
    """

    def get(self, request, uid, token):
        # get the shared project
        try:
            user_id = urlsafe_base64_decode(uid).decode()
            user = get_user_model().objects.get(pk=user_id)
            project_name = urlsafe_base64_decode(token).decode()
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise Http404

        project = get_object_or_404(Project, owner=user, name=project_name)

        if (
            project.last_shared is None
            or (timezone.now() - project.last_shared).days > 3
        ):
            raise Http404

        return render(
            request,
            "project_management/sharedProject.html",
            context={"project": project},
        )

    def post(self, request, uid, token):
        # get the shared project
        try:
            user_id = urlsafe_base64_decode(uid).decode()
            user = get_user_model().objects.get(pk=user_id)
            project_name = urlsafe_base64_decode(token).decode()
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise Http404

        project = get_object_or_404(Project, owner=user, name=project_name)

        if (
            project.last_shared is None
            or (timezone.now() - project.last_shared).days > 3
        ):
            raise Http404

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
        new_name_found = False
        while not new_name_found:
            try:
                project.name = project.name + "_shared"
                Project.objects.get(name=project.name, owner=request.user)
            except Project.DoesNotExist:
                project.owner = request.user
                project.save()
                new_name_found = True

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


def is_name_unique(user: User, project_name: str) -> bool:
    for project in user.projects.all():
        if project.name == project_name:
            return False
    return True

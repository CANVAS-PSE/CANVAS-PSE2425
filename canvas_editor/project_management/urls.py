from django.urls import path

from canvas import view_name_dict

from . import views

urlpatterns = [
    path("", views.ProjectsView.as_view(), name=view_name_dict.projects_view),
    path(
        "updateProject/<str:project_name>",
        views.update_project,
        name=view_name_dict.update_project_view,
    ),
    path(
        "deleteProject/<str:project_name>",
        views.delete_project,
        name=view_name_dict.delete_project_view,
    ),
    path(
        "toggle_favor/<str:project_name>",
        views.toggle_favor_project,
        name=view_name_dict.toggle_favor_project_view,
    ),
    path(
        "duplicateProject/<str:project_name>",
        views.duplicate_project,
        name=view_name_dict.duplicate_project_view,
    ),
    path(
        "shareProject/<str:project_name>",
        views.share_project,
        name=view_name_dict.share_project_view,
    ),
    path(
        "sharedProjects/<str:uid>/<str:token>",
        views.SharedProjectView.as_view(),
        name=view_name_dict.shared_projects_view,
    ),
]

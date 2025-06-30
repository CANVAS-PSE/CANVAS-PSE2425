from django.urls import path

from . import views

urlpatterns = [
    path("", views.projects, name="projects"),
    path(
        "updateProject/<str:project_name>", views.update_project, name="updateProject"
    ),
    path(
        "deleteProject/<str:project_name>", views.delete_project, name="deleteProject"
    ),
    path("favorProject/<str:project_name>", views.favor_project, name="favorProject"),
    path(
        "defavorProject/<str:project_name>",
        views.defavor_project,
        name="defavorProject",
    ),
    path(
        "duplicateProject/<str:project_name>",
        views.duplicate_project,
        name="duplicateProject",
    ),
    path(
        "shareProject/<str:project_name>",
        views.share_project,
        name="shareProject",
    ),
    path(
        "sharedProjects/<str:uid>/<str:token>",
        views.shared_project,
        name="sharedProjects",
    ),
]

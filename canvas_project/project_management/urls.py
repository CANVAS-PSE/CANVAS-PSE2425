from django.urls import path

from . import views

urlpatterns = [
    path("", views.projects, name="projects"),
    path("updateProject/<str:project_name>", views.updateProject, name="updateProject"),
    path("deleteProject/<str:project_name>", views.deleteProject, name="deleteProject"),
    path("favorProject/<str:project_name>", views.favorProject, name="favorProject"),
    path(
        "defavorProject/<str:project_name>",
        views.defavorProject,
        name="defavorProject",
    ),
    path(
        "duplicateProject/<str:project_name>",
        views.duplicateProject,
        name="duplicateProject",
    ),
]

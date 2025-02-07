from django.urls import path

from . import views

urlpatterns = [
    path("<str:project_name>", views.editor, name="editor"),
    path("download/<str:project_name>", views.download, name="download"),
    path("<str:project_name>/upload", views.uploadPreview, name="uploadPreview"),
]

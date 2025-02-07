from django.urls import path

from . import views

urlpatterns = [
    path("<str:project_name>", views.editor, name="editor"),
    path("<str:project_name>/download", views.download, name="download"),
    path("<str:project_name>/renderHDF5", views.renderHDF5, name="renderHDF5"),
    path("<str:project_name>/upload", views.uploadPreview, name="upload"),
]

from django.urls import path

from . import views

urlpatterns = [
    path("<str:project_name>", views.editor, name="editor"),
    path("download/<str:project_name>", views.download, name="download"),
    path("renderHDF5/<str:project_name>", views.renderHDF5, name="renderHDF5"),
]

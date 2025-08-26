from django.urls import path

from . import views

urlpatterns = [
    path("<str:project_name>", views.EditorView.as_view(), name="editor"),
    path("<str:project_name>/download", views.DownloadView.as_view(), name="download"),
    path("<str:project_name>/upload", views.UploadPreviewView.as_view(), name="upload"),
]

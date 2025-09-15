from django.urls import path

from editor.views.download_view import DownloadView
from editor.views.editor_view import EditorView
from editor.views.update_preview_view import UploadPreviewView

urlpatterns = [
    path("<str:project_name>", EditorView.as_view(), name="editor"),
    path("<str:project_name>/download", DownloadView.as_view(), name="download"),
    path("<str:project_name>/upload", UploadPreviewView.as_view(), name="upload"),
]

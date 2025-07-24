from django.urls import path

from . import views

urlpatterns = [
    path("<str:project_id>/", views.JobManagementView.as_view(), name="createNewJob"),
    path(
        "<str:project_id>/<int:job_id>/",
        views.JobStatusView.as_view(),
        name="jobStatus",
    ),
]

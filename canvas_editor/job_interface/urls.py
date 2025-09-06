from django.urls import path

from job_interface.views.job_management_view import JobManagementView
from job_interface.views.job_status_view import JobStatusView


urlpatterns = [
    path("<str:project_id>/", JobManagementView.as_view(), name="createNewJob"),
    path(
        "<str:project_id>/<int:job_id>/",
        JobStatusView.as_view(),
        name="jobStatus",
    ),
]

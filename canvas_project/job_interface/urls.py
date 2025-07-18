from django.urls import path

from . import views

urlpatterns = [
    path("<str:project_id>/", views.create_new_job, name="createNewJob"),
    path("<str:project_id>/<int:job_id>/", views.get_job_status, name="jobStatus"),
]

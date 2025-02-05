from django.urls import path

from . import views

urlpatterns = [
    path("", views.createNewJob, name="createNewJob"),
    path("<int:jobID>/", views.getJobStatus, name="jobStatus"),
]

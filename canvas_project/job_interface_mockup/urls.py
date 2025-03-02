from django.urls import path

from . import views

urlpatterns = [
    path("<str:project_id>/", views.createNewJob, name="createNewJob"),
    path("<str:project_id>/<int:jobID>/", views.getJobStatus, name="jobStatus"),
    path("<str:project_id>/hdf5", views.exampleCreateHDF5, name="exampleHDF5Creation"),
]

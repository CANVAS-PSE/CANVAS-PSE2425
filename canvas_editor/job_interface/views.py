from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views import View

from .models import Job, Project


class JobManagementView(LoginRequiredMixin, View):
    def get(self, request, project_id):
        project = get_object_or_404(Project, owner=request.user, pk=project_id)
        jobs = Job.objects.filter(owner=request.user, project=project).order_by(
            "starting_time"
        )
        job_ids = [job.pk for job in jobs]
        return JsonResponse({"jobIDs": job_ids})

    def post(self, request, project_id):
        project = get_object_or_404(Project, owner=request.user, pk=project_id)
        new_job = Job.objects.create(owner=request.user, project=project)
        return JsonResponse({"jobID": new_job.pk})


class JobStatusView(LoginRequiredMixin, View):
    def get(self, request, job_id, project_id):
        project = get_object_or_404(Project, owner=request.user, pk=project_id)
        job = get_object_or_404(Job, pk=job_id, owner=request.user, project=project)

        starting_time = job.starting_time

        time_diff = (timezone.now() - starting_time).total_seconds() / 60

        result = None
        if time_diff > 3:
            progress = 1
        else:
            progress = round(time_diff / 3, 2)

        if time_diff > 3:
            status = "Finished"
            result = "/static/img/render/example_0.pdf"
        elif time_diff > 2:
            status = "Aligning Heliostats"
        else:
            status = "Creating HDF5 file"

        return JsonResponse(
            {
                "jobID": job.pk,
                "status": status,
                "progress": progress,
                "result": result,
            }
        )

    def delete(self, request, job_id, project_id):
        project = get_object_or_404(Project, owner=request.user, pk=project_id)
        job = get_object_or_404(Job, pk=job_id, owner=request.user, project=project)
        job.delete()

        return HttpResponse(status=200)

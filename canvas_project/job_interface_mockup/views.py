from django.shortcuts import render
from .models import Job
from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.utils import timezone

import random


# Create your views here.
@login_required
@require_http_methods(["POST"])
def createNewJob(request):
    newJob = Job.objects.create(owner=request.user)
    return JsonResponse({"jobID": newJob.pk})


@login_required
def getJobStatus(request, jobID):
    if request.method == "GET":
        job = get_object_or_404(Job, pk=jobID, owner=request.user)

        starting_time = job.starting_time

        time_diff = (timezone.now() - starting_time).total_seconds() / 60

        result = None
        if time_diff > 3:
            progress = 1
        else:
            progress = round(time_diff / 3, 2)

        if time_diff > 3:
            status = "Finished"
            result = f"/static/img/render/example_{random.randint(1, 19)}.pdf"
        elif time_diff > 2:
            status = "Aligning Heliostats"
        elif time_diff > 1:
            status = "Creating HDF5 file"
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
    raise Http404

from datetime import timedelta

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from canvas import view_name_dict
from job_interface.models import Job
from project_management.models import Heliostat, LightSource, Project, Receiver


class JobInterfaceViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.project = Project.objects.create(
            name="Test project", description="Test project description", owner=self.user
        )
        Heliostat.objects.create(project=self.project)
        Receiver.objects.create(project=self.project)
        LightSource.objects.create(project=self.project)
        self.job = Job.objects.create(owner=self.user, project=self.project)
        self.client.login(username="testuser", password="testpassword")

        # urls
        self.createNewJob_url = reverse(
            view_name_dict.create_new_job_view, args=[self.project.pk]
        )
        self.getJobStatus_url = reverse(
            view_name_dict.job_status_view, args=[self.project.pk, self.job.pk]
        )

    def test_create_new_job_post(self):
        response = self.client.post(self.createNewJob_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Job.objects.count(), 2)
        self.assertEqual(response.json()["jobID"], Job.objects.last().pk)
        self.assertTrue(
            (Job.objects.last().starting_time - timezone.now()).total_seconds() < 2
        )
        self.assertEqual(Job.objects.last().owner, self.user)
        self.assertEqual(Job.objects.last().project, self.project)

    def test_create_new_job_post_logged_out(self):
        self.client.logout()

        response = self.client.post(self.createNewJob_url)

        self.assertEqual(response.status_code, 302)

    def test_create_new_job_get(self):
        response = self.client.get(self.createNewJob_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["jobIDs"]), Job.objects.count())
        self.assertEqual(response.json()["jobIDs"][0], Job.objects.first().pk)

    def test_create_new_job_get_logged_out(self):
        self.client.logout()

        response = self.client.get(self.createNewJob_url)

        self.assertEqual(response.status_code, 302)

    def test_get_job_status_get_creating_hdf5(self):
        self.job.starting_time = timezone.now()

        response = self.client.get(self.getJobStatus_url)

        self.assertEqual(response.json()["jobID"], self.job.pk)
        self.assertEqual(response.json()["status"], "Creating HDF5 file")
        self.assertEqual(
            response.json()["progress"],
            round(
                ((timezone.now() - self.job.starting_time).total_seconds() / 60) / 3, 2
            ),
        )
        self.assertIsNone(response.json()["result"])

    def test_get_job_status_get_aligning_heliostats(self):
        self.job.starting_time = timezone.now() - timedelta(minutes=2.5)
        self.job.save()

        response = self.client.get(self.getJobStatus_url)

        self.assertEqual(response.json()["jobID"], self.job.pk)
        self.assertEqual(response.json()["status"], "Aligning Heliostats")
        self.assertEqual(
            response.json()["progress"],
            round(
                ((timezone.now() - self.job.starting_time).total_seconds() / 60) / 3, 2
            ),
        )
        self.assertIsNone(response.json()["result"])

    def test_get_job_status_get_finished(self):
        self.job.starting_time = timezone.now() - timedelta(minutes=3)
        self.job.save()

        response = self.client.get(self.getJobStatus_url)

        self.assertEqual(response.json()["jobID"], self.job.pk)
        self.assertEqual(response.json()["status"], "Finished")
        self.assertEqual(
            response.json()["progress"],
            round(
                ((timezone.now() - self.job.starting_time).total_seconds() / 60) / 3, 2
            ),
        )
        self.assertIsNotNone(response.json()["result"])

    def test_get_job_status_get_logged_out(self):
        self.client.logout()

        response = self.client.get(self.getJobStatus_url)

        self.assertEqual(response.status_code, 302)

    def test_get_job_status_delete(self):
        response = self.client.delete(self.getJobStatus_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Job.objects.count(), 0)

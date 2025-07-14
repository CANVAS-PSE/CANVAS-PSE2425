from django.test import TestCase, Client
from django.contrib.auth.models import User
from job_interface_mockup.models import Job
from project_management.models import Project, Heliostat, Receiver, Lightsource
from django.utils import timezone
from datetime import timedelta
from django.urls import reverse


class ViewTests(TestCase):
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
        Lightsource.objects.create(project=self.project)
        self.job = Job.objects.create(owner=self.user, project=self.project)
        self.client.login(username="testuser", password="testpassword")

        # urls
        self.createNewJob_url = reverse("createNewJob", args=[self.project.pk])
        self.getJobStatus_url = reverse(
            "jobStatus", args=[self.project.pk, self.job.pk]
        )

    def test_createNewJob_POST(self):
        response = self.client.post(self.createNewJob_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Job.objects.count(), 2)
        self.assertEqual(response.json()["jobID"], Job.objects.last().pk)
        self.assertTrue(
            (Job.objects.last().starting_time - timezone.now()).total_seconds() < 2
        )
        self.assertEqual(Job.objects.last().owner, self.user)
        self.assertEqual(Job.objects.last().project, self.project)

    def test_createNewJob_POST_logged_out(self):
        self.client.logout()

        response = self.client.post(self.createNewJob_url)

        self.assertEqual(response.status_code, 302)

    def test_createNewJob_GET(self):
        response = self.client.get(self.createNewJob_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["jobIDs"]), Job.objects.count())
        self.assertEqual(response.json()["jobIDs"][0], Job.objects.first().pk)

    def test_createNewJob_GET_logged_out(self):
        self.client.logout()

        response = self.client.get(self.createNewJob_url)

        self.assertEqual(response.status_code, 302)

    def test_getJobStatus_GET_creatingHDF5(self):
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

    def test_getJobStatus_GET_aligningHeliostats(self):
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

    def test_getJobStatus_GET_finished(self):
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

    def test_getJobStatus_GET_logged_out(self):
        self.client.logout()

        response = self.client.get(self.getJobStatus_url)

        self.assertEqual(response.status_code, 302)

    def test_getJobStatus_DELETE(self):
        response = self.client.delete(self.getJobStatus_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Job.objects.count(), 0)

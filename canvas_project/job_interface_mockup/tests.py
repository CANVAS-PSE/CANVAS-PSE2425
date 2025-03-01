from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import Job
from project_management.models import Project
from django.utils import timezone


class ModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )

    def test_job_owner_given(self):
        job = Job.objects.create(owner=self.user)

        self.assertTrue(isinstance(job, Job))
        self.assertTrue((job.starting_time - timezone.now()).total_seconds() < 2)
        self.assertEqual(job.owner, self.user)
        self.assertIsNone(job.project)

    def test_job_owner_and_project_given(self):
        self.project = Project.objects.create(
            name="Test project", description="Test project description", owner=self.user
        )
        job = Job.objects.create(owner=self.user, project=self.project)

        self.assertTrue(isinstance(job, Job))
        print((job.starting_time - timezone.now()).total_seconds)
        self.assertTrue((job.starting_time - timezone.now()).total_seconds() < 2)
        self.assertEqual(job.owner, self.user)
        self.assertEqual(job.project, self.project)

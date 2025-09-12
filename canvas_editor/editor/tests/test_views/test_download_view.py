import io

import h5py
from artist.util import config_dictionary
from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from canvas import view_name_dict
from project_management.models import Heliostat, LightSource, Project, Receiver


class DownloadViewTest(TestCase):
    def setUp(self):
        self.download = reverse(
            view_name_dict.editor_download_view, kwargs={"project_name": "testProject"}
        )
        user = User.objects.create_user(username="testuser", password="testpassword")
        self.client = Client()
        self.client.login(username="testuser", password="testpassword")

        project = Project()
        project.name = "testProject"
        project.description = "This is a test project."
        project.owner = user
        project.save()

        # Add a heliostat to the project
        heliostat = Heliostat()
        heliostat.name = "testHeliostat"
        heliostat.project = project
        heliostat.position_x = 42
        heliostat.save()

        # Add a receiver to the project
        receiver = Receiver()
        receiver.name = "testReceiver"
        receiver.project = project
        receiver.normal_x = 42
        receiver.save()

        # Add a light source to the project
        light_source = LightSource()
        light_source.name = "testLightSource"
        light_source.project = project
        light_source.number_of_rays = 42
        light_source.save()

    def test_download(self):
        response = self.client.get(self.download)

        # assert that response is a file response containing a hdf5 file
        self.assertTrue(response.has_header("Content-Disposition"))
        self.assertIn(
            'attachment; filename="testProject.h5"', response["Content-Disposition"]
        )

        downloaded_hdf5_bytes = b"".join(response.streaming_content)
        downloaded_file_buffer = io.BytesIO(downloaded_hdf5_bytes)

        with h5py.File(downloaded_file_buffer, "r") as hdf5_file:
            # Check if the datasets contain the expected data
            heliostats = hdf5_file.get(config_dictionary.heliostat_key)
            receivers = hdf5_file.get(config_dictionary.target_area_key)
            light_sources = hdf5_file.get(config_dictionary.light_source_key)

            self.assertIsNotNone(heliostats)
            self.assertIsNotNone(receivers)
            self.assertIsNotNone(light_sources)

            for heliostat in heliostats:
                self.assertEqual(
                    42, heliostats[heliostat][config_dictionary.heliostat_position][0]
                )

            for receiver in receivers:
                self.assertEqual(42, receivers[receiver]["normal_vector"][0])

            for light_source in light_sources:
                self.assertEqual(42, light_sources[light_source]["number_of_rays"][()])

    def test_download_logged_out(self):
        self.client.logout()
        response = self.client.get(self.download)
        self.assertEqual(response.status_code, 302)

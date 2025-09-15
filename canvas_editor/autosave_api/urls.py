from django.urls import path

from autosave_api.views.heliostat_detail import HeliostatDetail
from autosave_api.views.heliostat_list import HeliostatList
from autosave_api.views.light_source_detail import LightSourceDetail
from autosave_api.views.light_source_list import LightSourceList
from autosave_api.views.project_detail_list import ProjectDetailList
from autosave_api.views.project_list import ProjectList
from autosave_api.views.receiver_detail import ReceiverDetail
from autosave_api.views.receiver_list import ReceiverList
from autosave_api.views.settings_detail import SettingsDetail


urlpatterns = [
    path("projects/", ProjectList.as_view(), name="project_list"),
    path("projects/<int:pk>/", ProjectDetailList.as_view(), name="project_detail"),
    path(
        "projects/<int:project_id>/heliostats/",
        HeliostatList.as_view(),
        name="heliostat_list",
    ),
    path(
        "projects/<int:project_id>/heliostats/<int:pk>/",
        HeliostatDetail.as_view(),
        name="heliostat_detail",
    ),
    path(
        "projects/<int:project_id>/receivers/",
        ReceiverList.as_view(),
        name="receiver_list",
    ),
    path(
        "projects/<int:project_id>/receivers/<int:pk>/",
        ReceiverDetail.as_view(),
        name="receiver_detail",
    ),
    path(
        "projects/<int:project_id>/light_sources/",
        LightSourceList.as_view(),
        name="light_source_list",
    ),
    path(
        "projects/<int:project_id>/light_sources/<int:pk>/",
        LightSourceDetail.as_view(),
        name="light_source_detail",
    ),
    path(
        "projects/<int:project_id>/settings/",
        SettingsDetail.as_view(),
        name="settings_detail",
    ),
]

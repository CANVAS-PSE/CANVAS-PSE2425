from django.urls import path

from .views import (
    HeliostatDetail,
    HeliostatList,
    LightSourceDetail,
    LightSourceList,
    ProjectDetailList,
    ProjectList,
    ReceiverDetail,
    ReceiverList,
    SettingsDetail,
)

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

from django.urls import path
from .views import (
    ProjectList,
    ProjectDetailList,
    HeliostatList,
    HeliostatDetail,
    ReceiverList,
    ReceiverDetail,
    LightsourceList,
    LightsourceDetail,
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
        "projects/<int:project_id>/lightsources/",
        LightsourceList.as_view(),
        name="lightsource_list",
    ),
    path(
        "projects/<int:project_id>/lightsources/<int:pk>/",
        LightsourceDetail.as_view(),
        name="lightsource_detail",
    ),
    path(
        "projects/<int:project_id>/settings/",
        SettingsDetail.as_view(),
        name="settings_detail",
    ),
]

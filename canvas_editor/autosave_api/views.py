from rest_framework import generics
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated

from project_management.models import (
    Heliostat,
    LightSource,
    Project,
    Receiver,
    Settings,
)

from .serializers import (
    HeliostatSerializer,
    LightSourceSerializer,
    ProjectDetailSerializer,
    ProjectSerializer,
    ReceiverSerializer,
    SettingsSerializer,
)


class ProjectList(generics.ListCreateAPIView):
    """
    Creates a view to list all of the projects of the user who's currently logged in, you can also create a new projectadd.
    """

    serializer_class = ProjectSerializer

    # Accepted authentication classes and the needed permissions to access the API
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    # Overwrite the default function to use the request user as the owner of the project and also create a new settings object
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        # Select only the projects the user owns
        return Project.objects.filter(owner=self.request.user)


class ProjectDetailList(generics.RetrieveUpdateDestroyAPIView):
    """
    Creates a view to list a specific project, specified by the given pk in the url, where you can also delete the project.
    """

    serializer_class = ProjectDetailSerializer

    # Accepted authentication classes and the needed permissions to access the API
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Select only the projects the user owns
        return Project.objects.filter(owner=self.request.user)


class HeliostatList(generics.ListCreateAPIView):
    """
    Creates a view to list all heliostats and create new ones.
    """

    serializer_class = HeliostatSerializer

    # Accepted authentication classes and the needed permissions to access the API
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    # Overwrite the default function to use the project defined by the project_id in the url for saving the heliostat
    def perform_create(self, serializer):
        # kwargs = keyword arguement
        project_id = self.kwargs["project_id"]
        project = generics.get_object_or_404(
            Project, id=project_id, owner=self.request.user
        )
        serializer.save(project=project)

    def get_queryset(self):
        project_id = self.kwargs["project_id"]
        return Heliostat.objects.filter(
            project__id=project_id, project__owner=self.request.user
        )


class HeliostatDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Creates a view to retrieve, edit or delete a specific heliostat, defined by the pk in the url.
    """

    serializer_class = HeliostatSerializer

    # Accepted authentication classes and the needed permissions to access the API
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Heliostat.objects.filter(project__owner=self.request.user)


class ReceiverList(generics.ListCreateAPIView):
    """
    Creates a view to list all receivers or to create a new one.
    """

    serializer_class = ReceiverSerializer

    # Accepted authentication classes and the needed permissions to access the API
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    # Overwrite the default function to use the project defined by the project_id in the url for saving the heliostat
    def perform_create(self, serializer):
        project_id = self.kwargs["project_id"]
        project = generics.get_object_or_404(
            Project, id=project_id, owner=self.request.user
        )
        serializer.save(project=project)

    def get_queryset(self):
        project_id = self.kwargs["project_id"]
        return Receiver.objects.filter(
            project__id=project_id, project__owner=self.request.user
        )


class ReceiverDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Creates a view of a specific receiver to retrieve, edit or delete it.
    """

    serializer_class = ReceiverSerializer

    # Accepted authentication classes and the needed permissions to access the API
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Receiver.objects.filter(project__owner=self.request.user)


class LightSourceList(generics.ListCreateAPIView):
    """
    Creates a view to list all light sources or to create a new one.
    """

    serializer_class = LightSourceSerializer

    # Accepted authentication classes and the needed permissions to access the API
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    # Overwrite the default function to use the project_id for saving the heliostat
    def perform_create(self, serializer):
        project_id = self.kwargs["project_id"]
        project = generics.get_object_or_404(
            Project, id=project_id, owner=self.request.user
        )
        serializer.save(project=project)

    def get_queryset(self):
        project_id = self.kwargs["project_id"]
        return LightSource.objects.filter(
            project__id=project_id, project__owner=self.request.user
        )


class LightSourceDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Creates a view to retrieve, update or delete a specific lightsource, defined by the given pk.
    """

    serializer_class = LightSourceSerializer

    # Accepted authentication classes and the needed permissions to access the API
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return LightSource.objects.filter(project__owner=self.request.user)


class SettingsDetail(generics.RetrieveUpdateAPIView):
    """
    Creates a view to list and update all settings.
    """

    serializer_class = SettingsSerializer

    # Accepted authentication classes and the needed permissions to access the API
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    # Overwrite the default get_object function to not use the primary key, but select the settings object by the corresponding project
    def get_object(self):
        project_id = self.kwargs["project_id"]
        queryset = self.get_queryset()
        obj = generics.get_object_or_404(queryset, project__id=project_id)
        return obj

    def get_queryset(self):
        """
        Return the settings for the project of the user.
        """
        return Settings.objects.filter(project__owner=self.request.user)

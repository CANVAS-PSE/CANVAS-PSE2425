from rest_framework import serializers

from project_management.models import (
    Heliostat,
    LightSource,
    Project,
    Receiver,
    Settings,
)


class HeliostatSerializer(serializers.ModelSerializer):
    """Serializer to convert a heliostat into JSON or to convert JSON into a heliostat."""

    class Meta:
        """Meta class for HeliostatSerializer."""

        model = Heliostat
        exclude = ["project"]


class ReceiverSerializer(serializers.ModelSerializer):
    """Serializer to convert a receiver into JSON or to convert JSON into a receiver."""

    class Meta:
        """Meta class for ReceiverSerializer."""

        model = Receiver
        exclude = ["project"]


class LightSourceSerializer(serializers.ModelSerializer):
    """Serializer to convert a light source into JSON or to convert JSON into a light source."""

    class Meta:
        """Meta class for LightSourceSerializer."""

        model = LightSource
        exclude = ["project"]


class SettingsSerializer(serializers.ModelSerializer):
    """Serializer to convert a settings object into JSON or to convert JSON into a settings object."""

    class Meta:
        """Meta class for SettingsSerializer."""

        model = Settings
        exclude = ["project", "id"]


class ProjectSerializer(serializers.ModelSerializer):
    """Serializer to convert a project into JSON only containing name and id."""

    class Meta:
        """Meta class for ProjectSerializer."""

        model = Project
        fields = ["id", "name"]


class ProjectDetailSerializer(serializers.ModelSerializer):
    """Serializer to convert a project into JSON, containing all the linked foreign fields, or to convert JSON into a project."""

    heliostats = HeliostatSerializer(many=True, read_only=True)
    receivers = ReceiverSerializer(many=True, read_only=True)
    light_sources = LightSourceSerializer(many=True, read_only=True)
    settings = SettingsSerializer(read_only=True)

    class Meta:
        """Meta class for ProjectDetailSerializer."""

        model = Project
        fields = [
            "name",
            "heliostats",
            "receivers",
            "light_sources",
            "settings",
        ]

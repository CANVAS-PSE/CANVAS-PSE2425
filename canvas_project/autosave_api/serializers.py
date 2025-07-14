from rest_framework import serializers
from project_management.models import (
    Project,
    Heliostat,
    Receiver,
    Lightsource,
    Settings,
)


class HeliostatSerializer(serializers.ModelSerializer):
    """
    Serializer to convert a heliostat into JSON or to convert JSON into a heliostat.
    """

    class Meta:
        model = Heliostat
        exclude = ["project"]


class ReceiverSerializer(serializers.ModelSerializer):
    """
    Serializer to convert a receiver into JSON or to convert JSON into a receiver.
    """

    class Meta:
        model = Receiver
        exclude = ["project"]


class LightsourceSerializer(serializers.ModelSerializer):
    """
    Serializer to convert a lightsource into JSON or to convert JSON into a lightsource.
    """

    class Meta:
        model = Lightsource
        exclude = ["project"]


class SettingsSerializer(serializers.ModelSerializer):
    """
    Serializer to convert a settings object into JSON or to convert JSON into a settings object.
    """

    class Meta:
        model = Settings
        exclude = ["project", "id"]


class ProjectSerializer(serializers.ModelSerializer):
    """
    Serializer to convert a project into JSON only containing name and id.
    """

    class Meta:
        model = Project
        fields = ["id", "name"]


class ProjectDetailSerializer(serializers.ModelSerializer):
    """
    Serializer to convert a project into JSON, containing all the linked foreign fields, or to convert JSON into a project.
    """

    heliostats = HeliostatSerializer(many=True, read_only=True)
    receivers = ReceiverSerializer(many=True, read_only=True)
    lightsources = LightsourceSerializer(many=True, read_only=True)
    settings = SettingsSerializer(read_only=True)

    class Meta:
        model = Project
        fields = [
            "name",
            "heliostats",
            "receivers",
            "lightsources",
            "settings",
        ]

from django.forms import ModelForm
from .models import Project
from django import forms
import re
from django.core.exceptions import ValidationError


def validateSymbols(value):
    if not re.match(r"^[a-zA-Z0-9_\säöüÄÖÜ-]+$", value):
        raise ValidationError("No special characters allowed.")


def validateFile(value):
    # Check if the file is uploaded
    if not value:
        return value  # If no file is uploaded, no need for validation.

    # Check file extension (only allow .h5 files for example)
    if not value.name.endswith(".h5"):
        raise ValidationError("Only HDF5 (.h5) files are allowed.")

    # Check file size
    max_size = 1024 * 1024 * 1024  # 1GB
    if value.size > max_size:
        raise ValidationError("File size should not exceed 1GB.")

    return value


class UpdateProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = ["name", "description"]

    name = forms.CharField(
        max_length=100,
        validators=[validateSymbols],
    )

    description = forms.CharField(
        max_length=500, required=False, widget=forms.TextInput()
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].widget.attrs.update(
            {"class": "form-control", "id": "createProjectNameInput"}
        )
        self.fields["description"].widget.attrs.update(
            {"class": "form-control", "id": "createProjectDescriptionInput"}
        )


class ProjectForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        validators=[validateSymbols],
    )
    description = forms.CharField(
        max_length=500, required=False, widget=forms.TextInput()
    )
    file = forms.FileField(
        required=False,
        validators=[validateFile],
        widget=forms.ClearableFileInput(
            attrs={"class": "form-control", "accept": ".h5"}
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].widget.attrs.update({"class": "form-control"})
        self.fields["description"].widget.attrs.update({"class": "form-control"})
        self.fields["file"].widget.attrs.update({"class": "form-control"})

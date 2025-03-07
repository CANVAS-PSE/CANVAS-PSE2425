from django.forms import ModelForm
from .models import Project
from django import forms
import re
from django.core.exceptions import ValidationError


def validateSymbols(value):
    if not re.match(r"^[a-zA-Z0-9_\s]+$", value):
        raise ValidationError("Only letters, numbers, and spaces are allowed.")


class UpdateProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = ["name", "description"]

    name = forms.CharField(
        max_length=100,
        validators=[validateSymbols],
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].widget.attrs.update({"class": "form-control"})
        self.fields["name"].widget.attrs.update({"id": "createProjectNameInput"})
        self.fields["description"].widget.attrs.update({"class": "form-control"})


class ProjectForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        validators=[validateSymbols],
    )
    description = forms.CharField(max_length=500, required=False)
    file = forms.FileField(
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].widget.attrs.update({"class": "form-control"})
        self.fields["description"].widget.attrs.update({"class": "form-control"})
        self.fields["file"].widget.attrs.update({"class": "form-control"})

    def clean_file(self):
        """Ensure the uploaded file is an HDF5 (.h5) file."""
        file = self.cleaned_data.get("file")
        if file and not file.name.endswith(".h5"):
            raise ValidationError("Only HDF5 (.h5) files are allowed.")
        return file

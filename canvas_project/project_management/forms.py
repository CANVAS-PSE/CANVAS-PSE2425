from django.forms import ModelForm
from .models import Project
from django import forms


class UpdateProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = ["name", "description"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].widget.attrs.update({"class": "form-control"})
        self.fields["name"].widget.attrs.update({"id": "createProjectNameInput"})
        self.fields["description"].widget.attrs.update({"class": "form-control"})


class ProjectForm(forms.Form):
    name = forms.CharField(max_length=300)
    description = forms.CharField(max_length=500)
    file = forms.FileField(
        label="HDF5 import: This field is optional. Add an HDF5 (.h5) file if you wish to import a project.",
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].widget.attrs.update({"class": "form-control"})
        self.fields["description"].widget.attrs.update({"class": "form-control"})
        self.fields["file"].widget.attrs.update({"class": "form-control"})

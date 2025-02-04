from django.forms import ModelForm
from .models import Project
from django import forms


class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = ["name", "description"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].widget.attrs.update({"class": "form-control"})
        self.fields["description"].widget.attrs.update({"class": "form-control"})


class UpdateProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = ["name", "description"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].widget.attrs.update({"class": "form-control"})
        self.fields["description"].widget.attrs.update({"class": "form-control"})


class ImportProjectForm(forms.Form):
    name = forms.CharField(max_length=300)
    description = forms.CharField(max_length=500)
    file = forms.FileField(label="Choose an HDF5 file")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].widget.attrs.update({"class": "form-control"})
        self.fields["description"].widget.attrs.update({"class": "form-control"})

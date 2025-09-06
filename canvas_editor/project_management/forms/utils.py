from django.core.exceptions import ValidationError


import re


def validate_symbols(name):
    if not re.match(r"^[a-zA-Z0-9_\säöüÄÖÜ-]+$", name):
        raise ValidationError("No special characters allowed.")

    return name

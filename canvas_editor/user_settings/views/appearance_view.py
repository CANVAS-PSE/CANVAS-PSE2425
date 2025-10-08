from django.views.generic import TemplateView


class AppearanceView(TemplateView):
    """View to change the appearance settings of canvas."""

    template_name = "user_settings/appearance.html"

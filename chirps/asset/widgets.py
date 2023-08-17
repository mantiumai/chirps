from django import forms
from django.utils.html import format_html


class KeyValueWidget(forms.TextInput):
    """Display key-value pairs"""

    template_name = 'asset/key_value_widget.html'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attrs.update({'class': 'form-control'})

    def render(self, name, value, attrs=None, renderer=None):
        """Render key-value pairs"""
        attrs = self.build_attrs(self.attrs, attrs)
        return format_html('<div class="key-value-widget">{}</div>', super().render(name, value, attrs, renderer))

# widgets.py
from django import forms
from django.utils.translation import gettext_lazy as _

class DatePickerInput(forms.DateInput):
    input_type = 'date'
    
    def __init__(self, attrs=None):
        default_attrs = {
            'class': 'datepicker',
            'placeholder': _('Επιλέξτε')
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)

class CustomFileInput(forms.FileInput):
    template_name = 'core/partials/file_input.html'

    def format_value(self, value):
        # Return the value so it gets passed to get_context instead of None
        return value

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)

        merged_attrs = context['widget']['attrs']
        context['widget']['disabled'] = merged_attrs.get('disabled', False)
        context['widget']['required'] = merged_attrs.get('required', False)
        context['widget']['accept'] = merged_attrs.get('accept', '')
        existing_filename = merged_attrs.get('data-existing-filename', '')

        has_file = bool(value) or bool(existing_filename) or context['widget'].get('is_initial', False)
        context['widget']['has_file'] = has_file

        # Extract just the filename from the value
        if has_file and value:
            # value is typically a FieldFile object or string path
            filename = str(value).replace('\\', '/').split('/')[-1]
            context['widget']['filename'] = filename
            if hasattr(value, 'url'):
                try:
                    context['widget']['url'] = value.url
                except ValueError:
                    context['widget']['url'] = ''
        elif has_file:
            initial_name = context['widget'].get('initial_name', '')
            filename = existing_filename or initial_name
            context['widget']['filename'] = str(filename).replace('\\', '/').split('/')[-1] if filename else ''
            context['widget']['url'] = context['widget'].get('initial_url', '')

        # Clear value so it is not rendered as value="..." in the HTML input element
        context['widget']['value'] = None

        return context

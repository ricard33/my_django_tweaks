"""
Settings for my_django_tweaks are all namespaced in the MY_DJANGO_TWEAKS setting.
For example your project's `settings.py` file might look like this:

MY_DJANGO_TWEAKS = {
    'FIELDS_PARAMETER_NAME': '.fields',
    'INCLUDE_FIELDS_PARAMETER_NAME': '.include_fields',
}

This module provides the `tweaks_settings` object, that is used to access
my_django_tweaks settings, checking for user settings first, then falling
back to the defaults.
"""
from django.core.signals import setting_changed
from rest_framework.settings import APISettings

DEFAULTS = {
    'FIELDS_PARAMETER_NAME': '.fields',
    'INCLUDE_FIELDS_PARAMETER_NAME': '.include_fields',
}

IMPORT_STRINGS = []

tweaks_settings = APISettings(None, DEFAULTS, IMPORT_STRINGS)


def reload_api_settings(*args, **kwargs):
    setting = kwargs['setting']
    if setting == 'MY_DJANGO_TWEAKS':
        tweaks_settings.reload()


setting_changed.connect(reload_api_settings)

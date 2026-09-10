from django.conf import settings
from django.utils.translation import get_language

def get_lang():
    return (get_language() or settings.LANGUAGE_CODE)[:2]

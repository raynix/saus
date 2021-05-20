from django import forms
from django.core import validators

from surls.models import Surl

class SearchSurlForm(forms.Form):
  search = forms.CharField(label='', max_length=100, required=False)

class SurlForm(forms.Form):
  url = forms.CharField(
    label='',
    help_text='The URL to be shortened',
    max_length=1000,
    validators=[validators.URLValidator()]
  )
  slug = forms.CharField(
    label='',
    help_text='Optional alias for the URL, but popular ones might be taken already',
    max_length=200,
    required=False,
    validators=[validators.validate_slug]
  )

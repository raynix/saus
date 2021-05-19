from django import forms

from surls.models import Surl

class SearchSurlForm(forms.Form):
  search = forms.CharField(label='', max_length=100, required=False)

class SurlForm(forms.Form):
  url = forms.CharField(max_length=200)

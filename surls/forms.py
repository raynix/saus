from django import forms
from django.core import validators
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from surls.models import Surl, Bookmark

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

class CustomUserCreationForm(UserCreationForm):
  email = forms.EmailField(
    required=True,
    help_text='Required. Enter a valid email address.',
    widget=forms.EmailInput(attrs={
      'class': 'form-control',
      'placeholder': 'Enter your email address'
    })
  )

  first_name = forms.CharField(
    max_length=30,
    required=False,
    help_text='Optional.',
    widget=forms.TextInput(attrs={
      'class': 'form-control',
      'placeholder': 'Enter your first name'
    })
  )

  last_name = forms.CharField(
    max_length=30,
    required=False,
    help_text='Optional.',
    widget=forms.TextInput(attrs={
      'class': 'form-control',
      'placeholder': 'Enter your last name'
    })
  )

  class Meta:
    model = User
    fields = ("username", "first_name", "last_name", "email", "password1", "password2")

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.fields['username'].widget.attrs.update({
      'class': 'form-control',
      'placeholder': 'Choose a username'
    })
    self.fields['password1'].widget.attrs.update({
      'class': 'form-control',
      'placeholder': 'Enter your password'
    })
    self.fields['password2'].widget.attrs.update({
      'class': 'form-control',
      'placeholder': 'Confirm your password'
    })

  def save(self, commit=True):
    user = super().save(commit=False)
    user.email = self.cleaned_data["email"]
    user.first_name = self.cleaned_data["first_name"]
    user.last_name = self.cleaned_data["last_name"]
    if commit:
      user.save()
    return user

class BookmarkForm(forms.ModelForm):
  tags = forms.CharField(
    max_length=200,
    required=False,
    help_text='Comma-separated tags (e.g. programming, tutorial, reference)',
    widget=forms.TextInput(attrs={
      'class': 'form-control',
      'placeholder': 'Enter tags separated by commas'
    })
  )

  class Meta:
    model = Bookmark
    fields = ['title', 'url', 'tags']
    widgets = {
      'title': forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter bookmark title'
      }),
      'url': forms.URLInput(attrs={
        'class': 'form-control',
        'placeholder': 'https://example.com'
      })
    }

  def clean_url(self):
    url = self.cleaned_data.get('url')
    if url and not url.startswith(('http://', 'https://')):
      url = 'https://' + url
    return url

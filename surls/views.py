import requests

from django.shortcuts import render, redirect
from django.http import HttpResponse, FileResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q

import qrcode
from qrcode.image.pure import PyPNGImage
from tempfile import SpooledTemporaryFile

from .models import Domain, Surl, Profile, Bookmark
from .forms import SurlForm, SearchSurlForm, CustomUserCreationForm, BookmarkForm

import logging
logger = logging.getLogger(__name__)

def shorten(request):
  domain_name = request.META['HTTP_HOST']
  domain = Domain.objects.get(name=domain_name)
  form = SurlForm()
  if not domain:
    return HttpResponse(status=404)

  if request.method == 'POST':
    form = SurlForm(request.POST)
    if form.is_valid():
      try:
        test_url = form.cleaned_data['url']
        test_response = requests.get(test_url)
        if test_response.ok:
          surl = Surl.safe_create(
            url=test_url,
            domain=domain,
            title='N/a',
            keyword=form.cleaned_data['slug']
          )
          messages.success(request, f"New short URL <a href='https://{domain_name}/{surl.keyword}'> https://{domain_name}/{surl.keyword} </a> created for {test_url}<br/><img src=\"{surl.keyword}/qr.png\"/>")
          return redirect('/')
      except Exception as e:
        logger.error(e)
        messages.error(request, "Error processing the URL")
        return redirect('/')
  return render(request, 'new.html', {'form': form})

def launch(request, keyword):
  domain_name = request.META['HTTP_HOST']
  surl = Surl.launch(keyword=keyword, domain_name=domain_name)
  if surl:
    surl.hit()
    return redirect(surl, permanent=True)
  else:
    return HttpResponse(status=404)

@login_required
def manage(request, keyword):
  current_user = request.user
  if keyword == '_all':
    surl_list = Surl.objects.filter(domain=current_user.profile.domain)
    search = request.GET.get('search', None)
    if search:
      surl_list = surl_list.filter( Q(keyword__icontains=search) | Q(url__icontains=search) )

    paginator = Paginator(surl_list.all(), 12)

    page = request.GET.get('page')
    surls = paginator.get_page(page)
    form = SearchSurlForm(request.GET)
    return render(request, 'manage.html', {'surls': surls, 'form': form})

  else:
    return HttpResponse(status=404)

def qr(request, keyword):
  domain_name = request.META['HTTP_HOST']
  img = qrcode.make(f'https://{domain_name}/{keyword}', image_factory=PyPNGImage)
  in_memory_file = SpooledTemporaryFile()
  img.save(in_memory_file)
  in_memory_file.seek(0)
  return FileResponse(in_memory_file, filename='qr.png')

def register(request):
  if request.method == 'POST':
    form = CustomUserCreationForm(request.POST)
    if form.is_valid():
      user = form.save()
      login(request, user)
      messages.success(request, f"Welcome {user.username}! Your account has been created successfully.")
      return redirect('/')
    else:
      messages.error(request, "Please correct the errors below.")
  else:
    form = CustomUserCreationForm()

  return render(request, 'registration/register.html', {'form': form})

@login_required
def bookmark_list(request):
  """View to list user's bookmarks"""
  try:
    profile = Profile.objects.get(user=request.user)
    bookmarks = Bookmark.objects.filter(profile=profile)
  except Profile.DoesNotExist:
    messages.error(request, "Please contact admin to set up your profile.")
    return redirect('/')

  search = request.GET.get('search', None)
  if search:
    bookmarks = bookmarks.filter(
      Q(title__icontains=search) |
      Q(tags__icontains=search)
    )

  paginator = Paginator(bookmarks, 10)
  page = request.GET.get('page')
  bookmarks_page = paginator.get_page(page)

  return render(request, 'bookmarks/list.html', {
    'bookmarks': bookmarks_page,
    'search': search
  })

@login_required
def bookmark_create(request):
  """View to create a new bookmark"""
  try:
    profile = Profile.objects.get(user=request.user)
  except Profile.DoesNotExist:
    messages.error(request, "Please contact admin to set up your profile.")
    return redirect('/')

  if request.method == 'POST':
    form = BookmarkForm(request.POST)
    if form.is_valid():
      bookmark = form.save(commit=False)
      bookmark.profile = profile
      bookmark.save()
      messages.success(request, f"Bookmark '{bookmark.title}' created successfully!")
      return redirect('bookmark_list')
    else:
      messages.error(request, "Please correct the errors below.")
  else:
    form = BookmarkForm()

  return render(request, 'bookmarks/create.html', {'form': form})

@login_required
def bookmark_edit(request, bookmark_id):
  """View to edit an existing bookmark"""
  try:
    profile = Profile.objects.get(user=request.user)
    bookmark = get_object_or_404(Bookmark, id=bookmark_id, profile=profile)
  except Profile.DoesNotExist:
    messages.error(request, "Please contact admin to set up your profile.")
    return redirect('/')

  if request.method == 'POST':
    form = BookmarkForm(request.POST, instance=bookmark)
    if form.is_valid():
      form.save()
      messages.success(request, f"Bookmark '{bookmark.title}' updated successfully!")
      return redirect('bookmark_list')
    else:
      messages.error(request, "Please correct the errors below.")
  else:
    form = BookmarkForm(instance=bookmark)

  return render(request, 'bookmarks/edit.html', {'form': form, 'bookmark': bookmark})

@login_required
def bookmark_delete(request, bookmark_id):
  """View to delete a bookmark"""
  try:
    profile = Profile.objects.get(user=request.user)
    bookmark = get_object_or_404(Bookmark, id=bookmark_id, profile=profile)
  except Profile.DoesNotExist:
    messages.error(request, "Please contact admin to set up your profile.")
    return redirect('/')

  if request.method == 'POST':
    title = bookmark.title
    bookmark.delete()
    messages.success(request, f"Bookmark '{title}' deleted successfully!")
    return redirect('bookmark_list')

  return render(request, 'bookmarks/delete.html', {'bookmark': bookmark})

@login_required
def bookmark_visit(request, bookmark_id):
  """View to visit a bookmark and increment hit counter"""
  try:
    profile = Profile.objects.get(user=request.user)
    bookmark = get_object_or_404(Bookmark, id=bookmark_id, profile=profile)
  except Profile.DoesNotExist:
    messages.error(request, "Please contact admin to set up your profile.")
    return redirect('/')

  bookmark.hit()
  return redirect(bookmark.url)

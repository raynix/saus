import requests

from django.shortcuts import render, redirect
from django.http import HttpResponse, FileResponse
from django.views.decorators.cache import cache_page
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q

import qrcode
from qrcode.image.pure import PyPNGImage
from tempfile import SpooledTemporaryFile

from .models import *
from .forms import *

import logging
logger = logging.getLogger(__name__)

def index(request):
  return HttpResponse("Hello, world. You're at the polls index.")

def shorten(request):
  domain_name = request.META['HTTP_HOST']
  domain = Domain.objects.get(name=domain_name)
  form = SurlForm()
  if not domain:
    return HttpResponse("Domain not supported", status=404)

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

#@login_required
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

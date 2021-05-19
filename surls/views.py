import ujson
import requests

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.cache import cache_page
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q

from .models import *
from .forms import *

def index(request):
  return HttpResponse("Hello, world. You're at the polls index.")

def shorten(request):
  domain_name = request.META['HTTP_HOST']
  domain = Domain.objects.get(name=domain_name)
  if not domain:
    return HttpResponse(status=404)

  if request.method == 'POST':
    form = SurlForm(request.POST)
    if form.is_valid():
      test_url = form.cleaned_data['url']
      test_response = requests.get(test_url)
      if test_response.ok:
        surl = Surl.safe_create(
          url=test_url,
          domain=domain,
          title='N/a'
        )
        messages.success(request, f"New short URL <a href='http://{domain_name}/{surl.keyword}'> http://{domain_name}/{surl.keyword} </a> created for {test_url}")
        return redirect('/')
  else:
    return render(request, 'new.html', {'form': SurlForm()})

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

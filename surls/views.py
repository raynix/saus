from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

def launch(request, keyword):
  domain_name = request.META['HTTP_HOST']
  surl = Surl.launch(keyword=keyword, domain_name=domain_name)
  if surl:
    surl.hit()
    return redirect(surl, permanent=True)
  else:
    return HttpResponse(status=404)

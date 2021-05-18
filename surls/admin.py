from django.contrib import admin

from .models import *

admin.site.register(Domain, DomainAdmin)
admin.site.register(Surl, SurlAdmin)
#admin.site.register(Profile, ProfileAdmin)

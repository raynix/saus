from django.db import models

import hashlib

from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.core.cache import cache
from django.conf import settings

class Domain(models.Model):
    name = models.CharField(max_length=200, db_index=True)

    def __str__(self):
        return self.name

    def number_of_surls(self):
        return Surl.objects.filter(domain__name=self.name).count()

class DomainAdmin(admin.ModelAdmin):
    list_display = ( 'name', 'number_of_surls' )

class Surl(models.Model):
    keyword = models.CharField(max_length=200, db_index=True)
    url = models.CharField(max_length=1000)
    title = models.CharField(max_length=1000)
    domain = models.ForeignKey(Domain, on_delete=models.PROTECT)
    hits = models.BigIntegerField(default=0)
    url_hash = models.CharField(max_length=64, db_index=True, default='')

    def __str__(self):
        return self.domain.name + '/' + self.keyword + '  --->  ' + self.url

    def get_absolute_url(self):
        return self.url

    def save(self, *args, **kwargs):
        self.url_hash = hashlib.sha256(self.url.encode('utf-8')).hexdigest()
        super(Surl, self).save(*args, **kwargs)

    def generate_b62(self):
        self.keyword = self.baseN(self.id)

    def hit(self):
        self.hits += 1
        self.save()

    @classmethod
    def baseN(cls, num, b=62, numerals="0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"):
        return ((num == 0) and  "0" ) or ( cls.baseN(num // b, b).lstrip("0") + numerals[num % b])

    @classmethod
    def is_keyword_available(cls, keyword, domain):
        return not Surl.objects.filter(keyword=keyword, domain=domain).first()

    @classmethod
    def url_exists(cls, url, domain):
        url_sha256 = hashlib.sha256(url.encode('utf-8')).hexdigest()
        return Surl.objects.filter(url_hash=url_sha256, domain=domain).first()

    @classmethod
    def safe_create(cls, url, domain, title, keyword=None):
        old_link = cls.url_exists(url, domain)
        if keyword:
            if old_link and old_link.keyword == keyword:
                return old_link
        else:
            if old_link:
                return old_link
            next_id = cls.objects.latest('id').id + 1
            keyword = cls.baseN( next_id )
        suffix_count = 0
        suffix = ''
        while not cls.is_keyword_available( keyword + suffix, domain ):
            suffix_count += 1
            suffix = '_' + cls.baseN( suffix_count )

        surl = Surl( keyword=keyword + suffix, url = url, title=title, domain=domain )
        surl.save()
        return surl
    @classmethod
    def launch(cls, keyword, domain_name):
        cache_key = f"{domain_name}/{keyword}"
        cached_surls = cache.get(cache_key)
        if cached_surls:
            return cls.objects.get(pk=cached_surls)
        result_set = cls.objects.filter(keyword=keyword, domain__name=domain_name)
        if not result_set:
            return None
        exact_match = [ r for r in result_set if r.keyword == keyword ]
        if exact_match:
            final_match = exact_match[0]
        else:
            final_match = result_set[0]
        cache.set(cache_key, final_match.id, settings.CACHE_TTL)
        return final_match

class SurlAdmin(admin.ModelAdmin):
    list_display = ( 'keyword', 'domain', 'url', 'hits' )
    list_filter = ( 'domain__name', )
    search_fields = ( 'keyword', 'url' )

from django.db import models
import hashlib
from django.contrib import admin
from django.contrib.auth.models import User
from typing import Optional

from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

class Domain(models.Model):
    name = models.CharField(max_length=200, db_index=True)

    def __str__(self) -> str:
        return str(self.name)

    def number_of_surls(self) -> int:
        return Surl.objects.filter(domain__name=self.name).count()  # type: ignore

class DomainAdmin(admin.ModelAdmin):
    list_display = ( 'name', 'number_of_surls' )

class Surl(models.Model):
    keyword = models.CharField(max_length=200, db_index=True)
    url = models.CharField(max_length=1000)
    title = models.CharField(max_length=1000)
    domain = models.ForeignKey(Domain, on_delete=models.PROTECT)
    hits = models.BigIntegerField(default=0)  # type: ignore
    url_hash = models.CharField(max_length=64, db_index=True, default='')

    def __str__(self) -> str:
        return self.domain.name + '/' + self.keyword + '  --->  ' + self.url

    def get_absolute_url(self) -> str:
        return str(self.url)

    def save(self, *args, **kwargs):
        # Ensure url is a string before encoding
        url_str = str(self.url) if self.url else ''
        self.url_hash = hashlib.sha256(url_str.encode('utf-8')).hexdigest()
        super(Surl, self).save(*args, **kwargs)

    def generate_b62(self) -> None:
        if self.id:  # type: ignore
            self.keyword = self.baseN(self.id)  # type: ignore

    def hit(self) -> None:
        # Use F() expression for atomic increment or refresh from db
        from django.db.models import F
        if self.id:  # type: ignore
            Surl.objects.filter(id=self.id).update(hits=F('hits') + 1)  # type: ignore
            self.refresh_from_db(fields=['hits'])

    @classmethod
    def baseN(cls, num: int, b: int = 62, numerals: str = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ") -> str:
        return ((num == 0) and  "0" ) or ( cls.baseN(num // b, b).lstrip("0") + numerals[num % b])

    @classmethod
    def is_keyword_available(cls, keyword: str, domain: Domain) -> bool:
        return not cls.objects.filter(keyword=keyword, domain=domain).first()  # type: ignore

    @classmethod
    def url_exists(cls, url: str, domain: Domain) -> Optional['Surl']:
        url_str = str(url) if url else ''
        url_sha256 = hashlib.sha256(url_str.encode('utf-8')).hexdigest()
        return cls.objects.filter(url_hash=url_sha256, domain=domain).first()  # type: ignore

    @classmethod
    def safe_create(cls, url: str, domain: Domain, title: str, keyword: Optional[str] = None) -> 'Surl':
        old_link = cls.url_exists(url, domain)
        if keyword:
            if old_link and old_link.keyword == keyword:
                return old_link
        else:
            if old_link:
                return old_link
            next_id = 5000
            try:
                latest_obj = cls.objects.latest('id')  # type: ignore
                if latest_obj.id:  # type: ignore
                    next_id = latest_obj.id + 1  # type: ignore
            except ObjectDoesNotExist:
                pass
            keyword = cls.baseN(next_id)
        suffix_count = 0
        suffix = ''
        while not cls.is_keyword_available(keyword + suffix, domain):
            suffix_count += 1
            suffix = '_' + cls.baseN(suffix_count)

        surl = Surl(keyword=keyword + suffix, url=url, title=title, domain=domain)
        surl.save()
        return surl
    @classmethod
    def launch(cls, keyword: str, domain_name: str) -> Optional['Surl']:
        cache_key = f"{domain_name}/{keyword}"
        cached_surls = cache.get(cache_key)
        if cached_surls:
            return cls.objects.get(pk=cached_surls)  # type: ignore
        result_set = cls.objects.filter(keyword=keyword, domain__name=domain_name)  # type: ignore
        if not result_set:
            return None
        exact_match = [r for r in result_set if r.keyword == keyword]
        if exact_match:
            final_match = exact_match[0]
        else:
            final_match = result_set[0]
        if final_match.id:  # type: ignore
            cache.set(cache_key, final_match.id, settings.CACHE_TTL)  # type: ignore
        return final_match

class SurlAdmin(admin.ModelAdmin):
    list_display = ( 'keyword', 'domain', 'url', 'hits' )
    list_filter = ( 'domain__name', )
    search_fields = ( 'keyword', 'url' )

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    domain = models.ForeignKey(Domain, on_delete=models.PROTECT)
    token = models.CharField(max_length=200, db_index=True)

    def username(self) -> str:
        return self.user.username  # type: ignore

    def domainname(self) -> str:
        return self.domain.name

    @classmethod
    def authenticate(cls, request_token: str) -> Optional['Profile']:
        if len(request_token) == 0:
            return None
        pf = cls.objects.filter(token=request_token).first()  # type: ignore
        return pf

class ProfileAdmin(admin.ModelAdmin):
    list_display = ( 'username', 'domainname', 'token' )

class Bookmark(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='bookmarks')
    title = models.CharField(max_length=500)
    url = models.URLField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    tags = models.CharField(max_length=200, blank=True, help_text="Comma-separated tags")
    hits = models.BigIntegerField(default=0)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"{self.title} - {self.profile.username()}"

    def get_tags_list(self) -> list:
        """Return tags as a list"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
        return []

    def set_tags_from_list(self, tag_list: list) -> None:
        """Set tags from a list of strings"""
        self.tags = ', '.join(tag_list)

    def hit(self) -> None:
        """Increment hit counter atomically"""
        from django.db.models import F
        if self.id:
            Bookmark.objects.filter(id=self.id).update(hits=F('hits') + 1)
            self.refresh_from_db(fields=['hits'])

class BookmarkAdmin(admin.ModelAdmin):
    list_display = ('title', 'profile', 'url', 'hits', 'created_at')
    list_filter = ('created_at', 'profile__user')
    search_fields = ('title', 'url', 'tags')
    readonly_fields = ('created_at', 'modified_at', 'hits')
    fieldsets = (
        (None, {
            'fields': ('title', 'url', 'profile')
        }),
        ('Categorization', {
            'fields': ('tags',)
        }),
        ('Statistics', {
            'fields': ('hits',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'modified_at'),
            'classes': ('collapse',)
        }),
    )

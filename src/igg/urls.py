from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from django.conf.urls import patterns, include, url
from django.views.generic import ListView, TemplateView
from igg.marathon.models import *

# Generic/Class-based Views: https://docs.djangoproject.com/en/dev/topics/class-based-views/

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
  # Admin
  url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
  url(r'^admin/', include(admin.site.urls)),

  url(r'^$', TemplateView.as_view(template_name='marathon/index.html'), name='home'),
  url(r'^games/$', ListView.as_view(model=Game), name='game-list'),
)

# https://docs.djangoproject.com/en/dev/howto/static-files/#serving-static-files-in-development
urlpatterns += staticfiles_urlpatterns()

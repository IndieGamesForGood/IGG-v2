from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

from igg.marathon.views import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
  # Admin
  url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
  url(r'^admin/', include(admin.site.urls)),

  url(r'^$', TemplateView.as_view(template_name='marathon/index.html'), name='home'),
  url(r'^donate-now/$', TemplateView.as_view(template_name='marathon/donate.html'), name='donate_now'),

  url(r'^games/$', GameListView.as_view(), name='game_list'),
  url(r'^games/(?P<slug>[a-zA-Z0-9_.-]+)/$', GameDetailView.as_view(), name='game_detail'),

  url(r'^challenges/$', ChallengeListView.as_view(), name='challenge_list'),
  url(r'^challenges/(?P<slug>[a-zA-Z0-9_.-]+)/$', ChallengeDetailView.as_view(), name='challenge_detail'),

  url(r'^raffles/$', RaffleListView.as_view(), name='raffle_list'),
  url(r'^raffles/(?P<slug>[a-zA-Z0-9_.-]+)/$', RaffleDetailView.as_view(), name='raffle_detail'),

  url(r'^schedule/$', ScheduleListView.as_view(), name='schedule_list'),
  url(r'^donors/$', DonorListView.as_view(), name='donor_list'),
)

# https://docs.djangoproject.com/en/dev/howto/static-files/#serving-static-files-in-development
urlpatterns += staticfiles_urlpatterns()

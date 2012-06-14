from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from django.conf.urls import patterns, include, url
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic import TemplateView

from igg.marathon.views import *

from registration.views import activate
from registration.views import register

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
  # Admin
  url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
  url(r'^admin/', include(admin.site.urls)),

  url(r'^ajax/(?P<model>\w+)/', ensure_csrf_cookie(AjaxLookaheadView.as_view()), name='ajax_lookahead'),

  # django-paypal
  (r'^paypal/ipn/', include('paypal.standard.ipn.urls')),

  # django-registration
  url(r'^activate/complete/$',
    TemplateView.as_view(template_name='registration/activation_complete.html'),
    name='registration_activation_complete'),
  # Activation keys get matched by \w+ instead of the more specific
  # [a-fA-F0-9]{40} because a bad activation key should still get to the view;
  # that way it can return a sensible "invalid key" message instead of a
  # confusing 404.
  url(r'^activate/(?P<activation_key>\w+)/$',
    activate,
    {'backend': 'igg.marathon.backends.IggRegistrationBackend'},
    name='registration_activate'),
  url(r'^register/$',
    register,
    {'backend': 'igg.marathon.backends.IggRegistrationBackend'},
    name='registration_register'),
  url(r'^register/complete/$',
    TemplateView.as_view(template_name='registration/registration_complete.html'),
    name='registration_complete'),
  url(r'^register/closed/$',
    TemplateView.as_view(template_name='registration/registration_closed.html'),
    name='registration_disallowed'),
  url(r'', include('registration.auth_urls')),

  url(r'^$', TemplateView.as_view(template_name='marathon/index.html'), name='home'),
  url(r'^donate/now/$', DonateFormView.as_view(), name='donate_now'),
  url(r'^donate/thank-you/$',
      TemplateView.as_view(template_name='marathon/donation_thankyou.html'), name='donation_complete'),
  url(r'^donate/cancelled/$',
      TemplateView.as_view(template_name='marathon/donation_cancelled.html'), name='donation_cancelled'),

  url(r'^games/$', GameListView.as_view(), name='game_list'),
  url(r'^games/(?P<pk>\d+)/$', GameDetailView.as_view(), name='game_detail'),
  url(r'^games/(?P<pk>\d+)/edit/$', ensure_csrf_cookie(GameEditFormView.as_view()), name='game_edit'),

  url(r'^challenges/$', ChallengeListView.as_view(), name='challenge_list'),
  url(r'^challenges/(?P<pk>\d+)/$', ChallengeDetailView.as_view(), name='challenge_detail'),

  url(r'^raffles/$', RaffleListView.as_view(), name='raffle_list'),
  url(r'^raffles/(?P<pk>\d+)/$', RaffleDetailView.as_view(), name='raffle_detail'),

  url(r'^schedule/$', ScheduleListView.as_view(template_name='marathon/schedule.html'), name='schedule_list'),
  url(r'^donors/$', DonorListView.as_view(), name='donor_list'),
)

# https://docs.djangoproject.com/en/dev/howto/static-files/#serving-static-files-in-development
urlpatterns += staticfiles_urlpatterns()

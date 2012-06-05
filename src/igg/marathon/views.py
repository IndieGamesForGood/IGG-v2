from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.template.loader import render_to_string
from django.utils.http import urlquote_plus
from django.utils.translation import ugettext as _
from django.views.generic import ListView, DetailView, FormView, View

from igg.marathon.mixins import JSONResponseMixin
from igg.marathon.models import *
from igg.marathon.forms import DonateForm

import hashlib
import time

# Generic/Class-based Views: https://docs.djangoproject.com/en/dev/topics/class-based-views/

class GameListView(ListView):
  context_object_name = 'games'
  def get_queryset(self):
    if self.request.user.is_staff:
      return Game.objects.all()
    else:
      return Game.objects.filter(visible=True)

class GameDetailView(DetailView):
  model = Game
  context_object_name = 'game'

  def get_context_data(self, **kwargs):
    # Call the base implementation first to get a context
    context = super(GameDetailView, self).get_context_data(**kwargs)
    game = context.get('game')
    total = MarathonInfo.info().total
    if total != 0:
      context['threshold'] = int(game.points / MarathonInfo.info().total)
    else:
      context['threshold'] = 0
    return context

class ChallengeListView(ListView):
  context_object_name = 'challenges'

  def get_queryset(self):
    if self.request.user.is_staff:
      return Challenge.objects.all()
    elif self.request.user.is_authenticated():
      return self.request.user.challenges
    else:
      return Challenge.objects.filter(accepted=True,private=False)

class ChallengeDetailView(DetailView):
  model = Challenge
  context_object_name = 'challenge'

class RaffleListView(ListView):
  context_object_name = 'raffles'

  def get_queryset(self):
    if self.request.user.is_staff:
      return Raffle.objects.all()
    else:
      return Raffle.objects.filter(visible=True)


class RaffleDetailView(DetailView):
  model = Raffle
  context_object_name = 'raffle'


class ScheduleListView(ListView):
  context_object_name = 'schedules'

  def get_queryset(self):
    if self.request.user.is_staff:
      return Schedule.objects.all()
    else:
      return Schedule.objects.filter(visible=True)


class DonorListView(ListView):
  context_object_name = 'donations'

  def get_queryset(self):
    if self.request.user.is_staff:
      return Donation.objects.all().order_by('-time')
    else:
      return Donation.objects.filter(approved=True).order_by('-time')


class DonateFormView(FormView):
  template_name = 'marathon/donate.html'
  form_class = DonateForm

  def post(self, request, *args, **kwargs):
      self.request = request
      return super(DonateFormView, self).post(request, *args, **kwargs)

  def form_valid(self, form):
    site = Site.objects.get_current()
    amount = form.cleaned_data.get('amount')
    email  = form.cleaned_data.get('email').strip()
    name   = form.cleaned_data.get('name')
    if name:
      name = name.strip()
    url = form.cleaned_data.get('url')
    if url:
      url = url.strip()
    twitter = form.cleaned_data.get('twitter')
    if twitter:
      twitter = twitter.strip()
    comment = form.cleaned_data.get('comment')
    if comment:
      comment = comment.strip()
    game = form.cleaned_data.get('game')
    challenge = form.cleaned_data.get('challenge')
    raffle = form.cleaned_data.get('raffle')

    try:
      user = User.objects.get(email=email)
    except User.DoesNotExist:
      # Username is the current time plus part of the user's email, all truncated to 30 chars.
      username = (email.replace('@', '').replace('.', '').replace('_', '') + '_' + str(time.time()))[:30]
      password = User.objects.make_random_password()
      user = User.objects.create_user(username, email=email, password=password)
      user.is_staff = False
      user.is_active = True
      user.is_superuser = False
      if name:
        names = name.split()
        user.first_name = names[0]
        user.last_name = ' '.join(names[1:])
        template_name = names[0]
      else:
        template_name = email
      user.save()
      # must call authenticate
      user = authenticate(username=username, password=password)
      login(self.request, user)
      # Send e-mail with username/password
      context = {'user': user, 'name': template_name,
                 'email': email, 'password': password,
                 'amount': amount, 'site': site}
      subject = ''.join(render_to_string('marathon/donation_new_account_email_subject.txt', context).splitlines())
      message = render_to_string('marathon/donation_new_account_email.txt', context)
      user.email_user(subject, message, settings.SERVER_EMAIL)
    user.profile.url = form.cleaned_data.get('url', None)
    user.profile.twitter = form.cleaned_data.get('twitter', None)
    user.save()
    user.profile.save()
    ipn_hash = hashlib.sha1(str(time.time()) + str(amount) +
                            str(email) + str(name) + str(twitter) +
                            str(comment) + str(game) + str(challenge) +
                            str(raffle) + str(user)).hexdigest()
    donation = Donation(user=user, name=name,
                        url=url, twitter=twitter,
                        amount=amount, comment=comment,
                        game=game, challenge=challenge,
                        raffle=raffle, approved=False,
                        points=0, ipn_hash=ipn_hash)
    donation.save()
    url = (settings.PAYPAL_WEBSCR_URL +
          '?amount=' + str(amount) +
          '&notify_url=' + urlquote_plus('http://' + site.domain + reverse('paypal-ipn')) +
          '&bn=' + urlquote_plus(_('Indie Games for Good')) +
          '&return=' + urlquote_plus('http://' + site.domain + reverse('donation_complete')) +
          '&cancel_return=' + urlquote_plus('http://' + site.domain + reverse('donation_cancelled')) +
          '&rm=1' +
          '&cmd=_donations' +
          '&cbt=Return+to+' + urlquote_plus(_('Indie Games for Good')) +
          '&tax=0.00' +
          '&shipping=0.00' +
          '&business=' + urlquote_plus(settings.PAYPAL_RECEIVER_EMAIL) +
          '&item_name=' + urlquote_plus(_('Donation to Child\'s Play Charity via ') + _('Indie Games for Good')) +
          '&custom=' + ipn_hash
          )
    return HttpResponseRedirect(url)

class AjaxLookaheadView(JSONResponseMixin, ListView):
  # https://docs.djangoproject.com/en/dev/topics/class-based-views/#dynamic-filtering
  def get_queryset(self):
    model = self.kwargs.get('model')
    if model == 'game':
      return Game.objects.filter(visible=True)
    elif model == 'raffle':
      return Raffle.objects.filter(visible=True)
    elif model == 'challenge':
      return Challenge.objects.filter(accepted=True)
    raise Http404

  def get(self, request, *args, **kwargs):
    return self.http_method_not_allowed(request, *args, **kwargs)

  def post(self, request, *args, **kwargs):
    query = request.POST.get('query')
    if query is None:
      raise Http404
    return self.render_to_response([a.name for a in self.get_queryset().filter(name__contains=query.strip())])





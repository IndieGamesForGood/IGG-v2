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
from django.views.generic.edit import CreateView, UpdateView

from igg.marathon.mixins import JSONResponseMixin
from igg.marathon.models import *
from igg.marathon.forms import *

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

class GameEditFormView(UpdateView):
  template_name = 'marathon/game_edit.html'
  form_class = GameEditForm
  model = Game
  context_object_name = 'game'
  success_url = 'doesnt_matter'

  def form_valid(self, form):
    # Call super() to actually save the object
    http_response = super(GameEditFormView, self).form_valid(form)
    return HttpResponse('SUCCESS')

class GameCreateFormView(CreateView):
  template_name = 'marathon/game_add.html'
  form_class = GameAddForm
  model = Game
  context_object_name = 'game'

  def form_valid(self, form):
    game = Game()
    game.name = form.cleaned_data.get('name')
    game.developer = form.cleaned_data.get('developer')
    game.site = form.cleaned_data.get('site')
    game.description = form.cleaned_data.get('description')
    game.visible = False
    game.points = 0
    game.save()
    return HttpResponse('Submitted Successfully!')

class ProfileEditView(FormView):
  _updated = False
  form_class = ProfileEditForm
  template_name = 'marathon/userprofile_form.html'

  def get(self, *args, **kwargs):
    http_response = super(ProfileEditView, self).get(*args, **kwargs)
    self._updated = False
    return http_response

  def get_context_data(self, *args, **kwargs):
    kwargs['updated'] = self._updated
    return super(ProfileEditView, self).get_context_data(*args, **kwargs)

  def get_form_kwargs(self):
    kwargs = super(ProfileEditView, self).get_form_kwargs()
    user = self.request.user
    kwargs['user'] = user
    kwargs['initial'] = {
      'first_name': user.first_name,
      'last_name': user.last_name,
      'email': user.email,
      'url': user.profile.url,
      'twitter': user.profile.twitter,
    }
    return kwargs

  def form_valid(self, form):
    user = self.request.user
    profile = user.profile
    user.first_name = form.cleaned_data.get('first_name')
    user.last_name = form.cleaned_data.get('last_name')
    user.email = form.cleaned_data.get('email')
    profile.url = form.cleaned_data.get('url')
    profile.twitter = form.cleaned_data.get('twitter')
    user.save()
    profile.save()
    self._updated = True
    return self.get(self.request)

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

class ChallengeEditFormView(UpdateView):
  template_name = 'marathon/challenge_edit.html'
  form_class = ChallengeEditForm
  model = Challenge
  context_object_name = 'challenge'
  success_url = 'doesnt_matter'

  def form_valid(self, form):
    # Call super() to actually save the object
    http_response = super(ChallengeEditFormView, self).form_valid(form)
    return HttpResponse('SUCCESS')

class ChallengeCreateFormView(CreateView):
  template_name = 'marathon/challenge_add.html'
  form_class = ChallengeAddForm
  model = Challenge
  context_object_name = 'challenge'

  def form_valid(self, form):
    challenge = Challenge()
    challenge.name = form.cleaned_data.get('name')
    challenge.description = form.cleaned_data.get('description')
    challenge.accepted = False
    challenge.private = form.cleaned_data.get('private', False)
    challenge.bounty = form.cleaned_data.get('bounty', 0.0)
    challenge.user = self.request.user
    challenge.save()
    return HttpResponse('Submitted Successfully!')


class RaffleListView(ListView):
  context_object_name = 'raffles'

  def get_queryset(self):
    if self.request.user.is_staff:
      return Raffle.objects.all()
    else:
      return Raffle.get_open_raffles()


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

  def get_form_kwargs(self):
    kwargs = super(DonateFormView,self).get_form_kwargs()
    if self.request.user.is_authenticated():
      c = self.request.user.challenges
    else:
      c = Challenge.objects.filter(accepted=True,private=False)
    kwargs['challenges'] = c

    game = None
    game_pk = self.request.GET.get('game')
    if game_pk is not None:
      try:
        game = Game.objects.get(visible=True,pk=int(game_pk))
      except:
        pass

    raffle = None
    raffle_pk = self.request.GET.get('raffle')
    if raffle_pk is not None:
      try:
        raffle = Raffle.objects.get(visible=True,pk=int(raffle_pk))
      except:
        pass

    challenge = None
    challenge_pk = self.request.GET.get('challenge')
    if challenge_pk is not None:
      try:
        challenge = Challenge.objects.get(accepted=True,pk=int(challenge_pk))
      except:
        pass

    kwargs['initial'] = {
      'game': game,
      'raffle': raffle,
      'challenge': challenge
    }

    return kwargs

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





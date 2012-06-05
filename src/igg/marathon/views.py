from django.contrib.auth.models import User
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.views.generic import ListView, DetailView, FormView, View

from igg.marathon.mixins import JSONResponseMixin
from igg.marathon.models import *
from igg.marathon.forms import DonateForm

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
  model = Challenge

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

  def form_valid(self, form):
    email = form.cleaned_data.get('email').strip()
    name = form.cleaned_data.get('name', '').strip()
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
      user.first_name = names[:-1]
      user.last_name = names[-1]
    user.profile.url = form.cleaned_data.get('url', None)
    user.profile.twitter = form.cleaned_data.get('twitter', None)
    user.save()
    user.profile.save()
    return HttpResponseRedirect(self.get_success_url())

  def get_success_url(self):
    return "http://www.google.com"

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





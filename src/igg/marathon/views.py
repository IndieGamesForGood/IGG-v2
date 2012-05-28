from django.views.generic import ListView, DetailView
from igg.marathon.models import *

# Generic/Class-based Views: https://docs.djangoproject.com/en/dev/topics/class-based-views/

class GameListView(ListView):
  model = Game
  context_object_name = 'games'

class GameDetailView(DetailView):
  model = Game
  context_object_name = 'game'

class ChallengeListView(ListView):
  model = Challenge
  context_object_name = 'challenges'

class ChallengeDetailView(DetailView):
  model = Challenge
  context_object_name = 'challenge'

class RaffleListView(ListView):
  model = Raffle
  context_object_name = 'raffles'

class RaffleDetailView(DetailView):
  model = Raffle
  context_object_name = 'raffle'

class ScheduleListView(ListView):
  model = Schedule
  context_object_name = 'schedules'

class DonorListView(ListView):
  model = Donation
  context_object_name = 'donations'


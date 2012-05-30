from django.views.generic import ListView, DetailView

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
  model = Donation
  context_object_name = 'donations'


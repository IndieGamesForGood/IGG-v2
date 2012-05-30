from django.db import models
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from datetime import datetime, timedelta
from math import log, floor

import locale
locale.setlocale( locale.LC_ALL, 'en_CA.UTF-8' )

# https://docs.djangoproject.com/en/dev/ref/models/fields/
# https://docs.djangoproject.com/en/dev/topics/i18n/translation/

class Game(models.Model):
  name = models.CharField(max_length=200)
  developer = models.CharField(max_length=200)
  site = models.CharField(max_length=200)
  description = models.TextField()
  visible = models.BooleanField(default=False)
  slug = models.SlugField()
  points = models.IntegerField(default=0)

  def __unicode__(self):
    return _(u'Game: %(name)s%(status)s') %\
           {'name': self.name,
            'status': (' (NOT VISIBLE)' if not self.visible else '')}

  class Meta:
    ordering = ['visible','name']

class Challenge(models.Model):
  name = models.CharField(max_length=200)
  description = models.TextField()
  accepted = models.BooleanField(default=False)
  private = models.BooleanField(default=False)
  bounty = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
  total = models.DecimalField(max_digits=14, decimal_places=2, default=0.00, null=True, blank=True)
  user = models.ForeignKey(User)
  slug = models.SlugField()

  def __unicode__(self):
    return _(u'Challenge: %(name)s (%(status)s%(privacy)s)') %\
         {'name': self.name,
          'status': ('NOT ' if not self.accepted else '') + 'Accepted',
          'privacy':(', PRIVATE: ' + self.user.__unicode__() if self.private else '')}

class Raffle(models.Model):
  name = models.CharField(max_length=200)
  description = models.TextField(max_length=500)
  quantity = models.IntegerField(default=1)
  visible = models.BooleanField(default=False)
  start = models.DateTimeField(null=True, blank=True)
  end = models.DateTimeField(null=True, blank=True)
  slug = models.SlugField()

  def __unicode__(self):
    return _(u'Raffle: %(name)s%(status)s') %\
         {'name': self.name,
          'status': (' (HIDDEN)' if not self.visible else '')}

class Donation(models.Model):
  user = models.ForeignKey(User, related_name='donations')
  amount = models.DecimalField(max_digits=14, decimal_places=2, help_text=_(u'Maximum $999,999,999,999.99'))
  comment = models.TextField(null=True, blank=True)
  timestamp = models.DateTimeField(auto_now_add=True)
  game = models.ForeignKey(Game, null=True, blank=True)
  challenge = models.ForeignKey(Challenge, null=True, blank=True, related_name='donations')
  raffle = models.ForeignKey(Raffle, null=True, blank=True)
  approved = models.BooleanField(default=False)
  points = models.IntegerField(default=0)

  def __unicode__(self):
    return _(u'%(amount)s donation by %(user)s') % \
      {'amount': locale.currency(self.amount, grouping=True),
       'user': self.user.__unicode__()}

class PointTransaction(models.Model):
  user = models.ForeignKey(User, related_name='transactions')
  game = models.ForeignKey(Game, related_name='transactions')
  points = models.IntegerField()
  spent = models.IntegerField(default=0)
  timestamp = models.DateTimeField(auto_now_add=True)

  def __unicode__(self):
    return _(u'PointTransaction:  %(name)s %(type)s %(count)sP%(game)s') %\
         {'type': 'GEN' if self.game.id==1 else ( 'PUT' if self.points > 0 else 'GET'),
          'count': self.points,
          'name': self.user.__unicode__(),
          'game': '' if self.game.id==1 else ' | ' + self.game.name}

class RaffleEntry(models.Model):
  user = models.ForeignKey(User, related_name='entries')
  raffle = models.ForeignKey(Raffle, related_name='entries')
  tickets = models.IntegerField()
  timestamp = models.DateTimeField(auto_now_add=True)

  def __unicode__(self):
    return _(u'RaffleEntry:  %(name)s %(count)s into %(raffle)s') %\
           {'count': self.tickets,
            'name': self.user.__unicode__(),
            'raffle': self.raffle.name}

class Schedule(models.Model):
  start = models.DateTimeField()
  end = models.DateTimeField()
  game = models.ForeignKey(Game, null=True, blank=True, related_name='schedules')
  title = models.CharField(max_length=200, null=True, blank=True)
  description = models.TextField(max_length=500, null=True, blank=True)
  visible = models.BooleanField(default=False)

class UserProfile(models.Model):
  user = models.OneToOneField(User)
  tickets = models.IntegerField(default=0)
  points = models.IntegerField(default=0)

  def __unicode__(self):
    return self.user.__unicode__()

# http://www.turnkeylinux.org/blog/django-profile
User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])


class MarathonInfo(models.Model):
  total = models.DecimalField(max_digits=14, decimal_places=2, default=0.00)

  start = models.DateTimeField()
  end = models.DateTimeField()

  event = models.ForeignKey(Schedule)

  point_source = models.ForeignKey(Game)
  ticket_source = models.ForeignKey(Raffle)

  dollarsPerTicket = models.IntegerField(default=5)
  pointsPerMinute = models.IntegerField(default=100)

  initHourCost = models.DecimalField(max_digits=14, decimal_places=2, default=4.00)
  rate = models.DecimalField(max_digits=14, decimal_places=2, default=.06)


  def dollarsToPoints(self,dollars):
    return int((self.dollarsToTime(dollars).total_seconds() / 60.0) / self.pointsPerMinute)

  def dollarsToTickets(self,dollars):
    return int(dollars/self.dollarsPerTicket)

  def pointsToMinutes(self,points):
    return points * self.pointsPerMinute

  def dollarsToTime(self, dollars, oldTotal=None):
    if oldTotal is None:
      oldTotal = self.total
    f_dollars = float(dollars)
    f_rate = float(self.rate)
    f_ihcost = float(self.initHourCost)
    f_oldTotal = float(oldTotal)
    return timedelta(hours=((log(((f_oldTotal+f_dollars)/f_ihcost * f_rate)+1) / log(1.0 + f_rate)) -
                            (log((f_oldTotal/f_ihcost * f_rate)+1)/log(1.0 + f_rate))))

  def save(self, *args, **kwargs):
    self.total = sum(foo.amount for foo in Donation.objects.filter(approved=True))
    self.end = self.start + (self.dollarsToTime(self.total,0.00).__floordiv__(3600) * 3600) #Marathon changes in hour increments
    self.event.end = self.end
    self.event.save()
    super(MarathonInfo, self).save(*args, **kwargs)


# Signal handlers: https://docs.djangoproject.com/en/dev/topics/signals/#connecting-receiver-functions
@receiver(models.signals.pre_save,sender=Donation)
def donationSaving(sender, instance, **kwargs):
  try:
    if instance.approved and not Donation.objects.get(pk=instance.pk).approved:
      # Newly approved donation, make transactions appropriately
      thisMarathon = MarathonInfo.objects.get(id='1')
      points = thisMarathon.dollarsToPoints(instance.amount)
      tickets = thisMarathon.dollarsToTickets(instance.amount)

      cpt = PointTransaction(user=instance.user, game=thisMarathon.point_source, points=-points, spent=0)
      cpt.save()
      cre = RaffleEntry(user=instance.user, raffle=thisMarathon.ticket_source, tickets=-tickets)
      cre.save()

      if instance.game is not None:
        npt = PointTransaction(user=instance.user, game=instance.game, points=points, spent=0)
        npt.save()

      if instance.raffle is not None:
        nre = RaffleEntry(user=instance.user, raffle=instance.raffle, tickets=tickets)
        nre.save()

      instance.user.profile.save()

  except Donation.DoesNotExist:
    pass

@receiver(models.signals.post_save,sender=Donation)
def donationSaved(sender, instance, **kwargs):
  #Update affected models upon saved donation.
  if instance.challenge is not None:
    instance.challenge.save()
  MarathonInfo.objects.get(id='1').save()


@receiver(models.signals.pre_save,sender=Challenge)
def challengeSaving(sender, instance, **kwargs):
  instance.total = sum(foo.amount for foo in instance.donations.filter(approved=True))

@receiver(models.signals.post_save,sender=RaffleEntry)
def raffleEntrySaved(sender, instance, **kwargs):
  instance.user.tickets = -sum(foo.tickets for foo in instance.user.entries.all())
  instance.user.save()
  instance.raffle.tickets = sum(foo.tickets for foo in instance.raffle.entries.all())
  instance.raffle.save()

@receiver(models.signals.post_save,sender=PointTransaction)
def pointTransactionSaved(sender, instance, **kwargs):
  instance.user.profile.points = -sum(foo.points for foo in instance.user.transactions.all())
  instance.user.save()
  instance.game.points = sum(foo.points for foo in instance.game.transactions.all())
  instance.game.save()
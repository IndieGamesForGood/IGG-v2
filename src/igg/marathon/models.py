from django.db import models
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

import locale

locale.setlocale(locale.LC_ALL, '')

# https://docs.djangoproject.com/en/dev/ref/models/fields/
# https://docs.djangoproject.com/en/dev/topics/i18n/translation/



class Game(models.Model):
  name = models.CharField(max_length=200)
  developer = models.CharField(max_length=200)
  site = models.CharField(max_length=200)
  description = models.TextField()
  visible = models.BooleanField(default=False)
  slug = models.SlugField()

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

  def __unicode__(self):
    return _(u'%(amount)s donation by %(user)s') % \
      {'amount': locale.currency(self.amount, grouping=True),
       'user': self.user.__unicode__()}

class PointTransaction(models.Model):
  user = models.ForeignKey(User, related_name='transactions')
  game = models.ForeignKey(Game)
  amount = models.IntegerField()
  spent = models.IntegerField()
  timestamp = models.DateTimeField(auto_now_add=True)

  def __unicode__(self):
    return _(u'PointTransaction:  %(name)s %(type)s %(count)sP%(game)s') %\
         {'type': 'GEN' if self.game.id==1 else ( 'PUT' if self.amount > 0 else 'GET'),
          'count': self.amount,
          'name': self.user.__unicode__(),
          'game': '' if self.game.id==1 else ' | ' + self.game.name}

class RaffleEntry(models.Model):
  user = models.ForeignKey(User, related_name='entries')
  raffle = models.ForeignKey(Raffle)
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


# Signal handlers: https://docs.djangoproject.com/en/dev/topics/signals/#connecting-receiver-functions
@receiver(models.signals.pre_save,sender=Donation)
def donationSaving(sender, instance, **kwargs):
  try:
    if instance.approved and not Donation.objects.get(pk=instance.pk).approved:
      instance.user.profile.points += 500 #TODO: Remove these manual manipulations and put into Transactions
      instance.user.profile.tickets += 5  #TODO: Remove (see above)
      npt = PointTransaction(user=instance.user, game=Game.objects.get(id='1'), amount=-500, spent=0)
      npt.save()
      nre = RaffleEntry(user=instance.user, raffle=Raffle.objects.get(id='1'), tickets=-5)
      nre.save()
      if instance.game is not None:
        instance.user.profile.points -= 500  #TODO: Remove (see above)
        pt = PointTransaction(user=instance.user, game=instance.game, amount=500, spent=0)
        pt.save()
      if instance.raffle is not None:
        instance.user.profile.tickets += 5    #TODO: Remove (see above)
        re = RaffleEntry(user=instance.user, raffle=instance.raffle, tickets=5)
        re.save()
      instance.user.profile.save()
  except Donation.DoesNotExist:
    pass

@receiver(models.signals.post_save,sender=Donation)
def donationSaved(sender, instance, **kwargs):
  try:
    if instance.challenge is not None:
      instance.challenge.total = sum(foo.amount for foo in instance.challenge.donations.filter(approved=True))
      instance.challenge.save()
  except Challenge.DoesNotExist:
    pass
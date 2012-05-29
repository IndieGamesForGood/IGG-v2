from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

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
    import locale
    locale.setlocale(locale.LC_ALL, '')
    return _(u'Game: %(name)s') %\
           {'name': self.name}

  class Meta:
    ordering = ['name']

class Challenge(models.Model):
  name = models.CharField(max_length=200)
  description = models.TextField()
  accepted = models.BooleanField(default=False)
  private = models.BooleanField(default=False)
  bounty = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
  user = models.ForeignKey(User)
  slug = models.SlugField()

class Raffle(models.Model):
  name = models.CharField(max_length=200)
  description = models.TextField(max_length=500)
  quantity = models.IntegerField(default=1)
  visible = models.BooleanField(default=False)
  start = models.DateTimeField()
  end = models.DateTimeField()
  slug = models.SlugField()

class Donation(models.Model):
  user = models.ForeignKey(User)
  amount = models.DecimalField(max_digits=14, decimal_places=2, help_text=_(u'Maximum $999,999,999,999.99'))
  comment = models.TextField()
  timestamp = models.DateTimeField(auto_now_add=True)
  game = models.ForeignKey(Game)
  challenge = models.ForeignKey(Challenge)
  raffle = models.ForeignKey(Raffle)
  confirmed = models.BooleanField(default=False)

  def __unicode__(self):
    import locale
    locale.setlocale(locale.LC_ALL, '')
    return _(u'%(amount)s donation by %(user)s') % \
      {'amount': locale.currency(self.amount, grouping=True),
       'user': self.user.__unicode__()}

class PointTransaction(models.Model):
  user = models.ForeignKey(User)
  game = models.ForeignKey(Game)
  amount = models.IntegerField()
  spent = models.IntegerField()
  timestamp = models.DateTimeField(auto_now_add=True)

class RaffleEntry(models.Model):
  user = models.ForeignKey(User)
  raffle = models.ForeignKey(Raffle)
  tickets = models.IntegerField()
  timestamp = models.DateTimeField(auto_now_add=True)

class Schedule(models.Model):
  start = models.DateTimeField();
  end = models.DateTimeField();
  game = models.ForeignKey(Game);
  visible = models.BooleanField(default=False)

class UserProfile(models.Model):
  user = models.OneToOneField(User)

  def __unicode__(self):
    return self.user.__unicode__()

# http://www.turnkeylinux.org/blog/django-profile
User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])


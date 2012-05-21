from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

# https://docs.djangoproject.com/en/dev/ref/models/fields/
# https://docs.djangoproject.com/en/dev/topics/i18n/translation/


class Challenge(models.Model):
  pass


class Donation(models.Model):
  user = models.ForeignKey(User)
  amount = models.DecimalField(max_digits=14, decimal_places=2, help_text=_(u'Maximum $999,999,999,999.99'))

  def __unicode__(self):
    import locale
    locale.setlocale(locale.LC_ALL, '')
    return _(u'%(amount)s donation by %(user)s') % \
      {'amount': locale.currency(self.amount, grouping=True),
       'user': self.user.__unicode__()}


class Game(models.Model):
  name = models.CharField(max_length=200)


class Raffle(models.Model):
  name = models.CharField(max_length=200)


class UserProfile(models.Model):
  user = models.OneToOneField(User)

  def __unicode__(self):
    return self.user.__unicode__()

# http://www.turnkeylinux.org/blog/django-profile
User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])


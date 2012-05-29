import time

from django.conf import settings
from django.contrib.auth.models import User, check_password
from django.contrib.sites.models import RequestSite
from django.contrib.sites.models import Site
from django.db import transaction

from igg.marathon.forms import NoUsernameRegistrationForm

from registration.backends.default import DefaultBackend
from registration import signals
from registration.models import RegistrationProfile


class LoginUsingEmailAsUsernameBackend(object):
  """
  Custom Authentication backend that supports using an e-mail address
  to login instead of a username.

  See: http://blog.cingusoft.org/custom-django-authentication-backend
  """
  supports_object_permissions = False
  supports_anonymous_user = False
  supports_inactive_user = False

  def authenticate(self, username=None,password=None):
    try:
      # Check if the user exists in Django's database
      user = User.objects.get(email=username)
    except User.DoesNotExist:
      return None

    # Check password of the user we found
    if check_password(password, user.password):
      return user
    return None

  # Required for the backend to work properly - unchanged in most scenarios
  def get_user(self, user_id):
    try:
      return User.objects.get(pk=user_id)
    except User.DoesNotExist:
      return None

class IggRegistrationBackend(DefaultBackend):

  def register(self, request, **kwargs):
    email, password, \
    first_name, last_name = kwargs['email'], kwargs['password1'], \
                            kwargs['first_name'], kwargs['last_name']

    # Username is the current time plus part of the user's email, all truncated to 30 chars.
    username = (str(time.time()) + '_' + email.replace('@', '').replace('.', '').replace('_', ''))[:30]

    if Site._meta.installed:
      site = Site.objects.get_current()
    else:
      site = RequestSite(request)

    new_user = new_user = User.objects.create_user(username, email, password)
    new_user.is_active = False
    new_user.first_name = first_name
    new_user.last_name = last_name
    new_user.save()
    
    registration_profile = RegistrationProfile.objects.create_profile(new_user)
    registration_profile.send_activation_email(site)

    signals.user_registered.send(sender=self.__class__,
                                 user=new_user,
                                 request=request)
    return new_user
  register = transaction.commit_on_success(register)

  def get_form_class(self, request):
    return NoUsernameRegistrationForm

from django import forms
# from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _


from registration.forms import RegistrationFormUniqueEmail

class NoUsernameRegistrationForm(RegistrationFormUniqueEmail):
  username = forms.CharField(required=False, widget=forms.HiddenInput())
  first_name = forms.CharField(widget=forms.TextInput(attrs=dict(maxlength=30)),
                               label=_("First Name"))
  last_name = forms.CharField(widget=forms.TextInput(attrs=dict(maxlength=30)),
                               label=_("Last Name"))

  def __init__(self, *args, **kwargs):
    super(NoUsernameRegistrationForm, self).__init__(*args, **kwargs)
    self.fields.keyOrder = ['first_name', 'last_name', 'email',
                            'password1', 'password2', 'username']

  def clean_username(self):
    return self.cleaned_data['username']

  def clean_first_name(self):
    return self.cleaned_data['first_name'].title()

  def clean_last_name(self):
    return self.cleaned_data['last_name'].title()

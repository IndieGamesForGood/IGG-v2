from django.conf import settings
from igg.marathon.models import MarathonInfo

def marathon_info(request):
  """IGG Marathon Template Context Processor

  Adds the ``marathon`` object to the template context.
  """
  return {
    'marathon': MarathonInfo.info(),
    'IGG_PARAM_RATE': settings.IGG_PARAM_RATE,
    'IGG_PARAM_I_HR_COST': settings.IGG_PARAM_I_HR_COST,
    'IGG_PARAM_DOLLARS_PER_TICKET': settings.IGG_PARAM_DOLLARS_PER_TICKET,
    'IGG_PARAM_PTS_PER_MIN': settings.IGG_PARAM_PTS_PER_MIN
  }

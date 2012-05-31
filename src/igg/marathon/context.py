from django.conf import settings
from igg.marathon.models import MarathonInfo

def marathon_info(request):
  """IGG Marathon Template Context Processor

  Adds the ``marathon`` object to the template context.
  """
  return {'marathon': MarathonInfo.objects.get(pk=settings.IGG_PARAM_MARATHONINFO_PK)}

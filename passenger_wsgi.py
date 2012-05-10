"""
Passenger WSGI file for IGG.

Ensures that a virtualenv exists and that the current interpreter is the one
inside this virtualenv. Also appends ``apps`` and ``src`` to the current python
path so that the igg and third-party modules can be imported.

Imports the Django WSGI application handler from ``igg.wsgi``.

"""
import sys
import os

PYTHON = os.path.join(os.getcwd(), 'env/bin/python')

# First, make sure the virtualenv python exists.
if not os.path.exists(PYTHON):
  error = 'ERROR: VirtualEnv does not exist, see README!'
  print >> sys.stderr , error
  # Attempt to write to a file in case we can't see stderr
  try:
    from datetime import datetime
    f = open('error.log', 'a')
    f.write(str(datetime.now()) + ' - ' + error)
    f.close()
  except: # Fail silently
    pass
  sys.exit(1)

# Second, make sure we are being run by the virtualenv's python. If not, make
# it so. PYTHON is present twice so that the new python interpreter knows the
# actual executable path
if sys.executable != PYTHON:
  os.execl(PYTHON, PYTHON, *sys.argv)

# Inject some paths
sys.path.insert(0, os.path.join(os.getcwd(), 'apps'))
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

from igg.wsgi import application

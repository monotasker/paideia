import glob
import inspect
import os

path = os.path.join(
    '/home/jeff/src/ve/ocp/bin/applications',
    'paideia',
    'tests',
    '*',
    '*.py'
)

for f in glob.iglob(path):
    print 'DEBUG: f =', f
    name = f.split('tests/')[1].split('.')[0]
    name = name.replace('/', '.')
    mod = __import__(name, globals(), locals())
    print 'DEBUG: mod =', mod
    members = inspect.getmembers(mod, inspect.isclass)
    for cls in members:
       print cls
       if 'TestCase' in inspect.getmro(cls):
           print cls



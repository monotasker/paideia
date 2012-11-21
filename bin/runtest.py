'''
Run this app's tests via py.test

run with: python web2py.py -S paideia -R applications/paideia/bin/runtest.py
'''
import subprocess
import os
import sys
from copy import copy

def run_execfile(test_dir, app_name):
    if os.name == 'nt':
        errlist = (WindowsError,ValueError,SystemExit)
    else:
        errlist = (OSError,ValueError,SystemExit)

    try:
        file_dir = test_dir # os.path.split(test_file)[0]
        if file_dir not in sys.path:
            sys.path.append(file_dir)   # to support imports from current folder in the testfiles
        # modules are applications/[app_name]/modules
        modules_path = os.path.join('applications', app_name, 'modules')
        if modules_path not in sys.path:
            sys.path.append(modules_path)       # to support imports from modules folder
        if 'site-packages' not in sys.path:
            sys.path.append('site-packages')    # support imports from web2py/site-packages
        g = copy(globals())
        subprocess.Popen("py.test {}".format(test_dir), stdout=PIPE, shell=True).stdout.read()
        #execfile(test_file, g,)
    except errlist:
        pass # we know about the rotating logger error...
             # and SystemExit is not useful to detect
    except Exception, e:
        #showfeedback()
        print type(e), e

if __name__=='__main__':
    run_execfile('../tests/', 'paideia')


'''
Run this app's tests via py.test

run with: python ~/web/web2py/web2py.py -S paideia -R applications/paideia/bin/runtest.py
'''
import subprocess
import os
import sys
from copy import copy

def run_execfile(w2p_dir, test_dir, app_name):
    if os.name == 'nt':
        errlist = (WindowsError,ValueError,SystemExit)
    else:
        errlist = (OSError,ValueError,SystemExit)

    try:
        test_dir = os.path.join(w2p_dir, 'applications', app_name, test_dir)
        if test_dir not in sys.path:
            sys.path.append(test_dir)   # to support imports from current folder in the testfiles
        # modules are applications/[app_name]/modules
        modules_path = os.path.join('applications', app_name, 'modules')
        if modules_path not in sys.path:
            sys.path.append(modules_path)       # to support imports from modules folder
        if 'site-packages' not in sys.path:
            sys.path.append('site-packages')    # support imports from web2py/site-packages
        g = copy(globals())
        print current
        proc = subprocess.Popen("py.test {}".format(test_dir),
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    shell=True)
        stdout_val, stderr_val = proc.communicate()
        print stdout_val, stderr_val

    except errlist:
        pass

    except Exception, e:
        #showfeedback()
        print type(e), e

if __name__=='__main__':
    run_execfile('~/web/web2py/', 'tests', 'paideia')


"""
A collection of miscellaneous utility functions to be used in multiple modules.
"""
import traceback
from gluon import current


def send_error(instance, mymethod, myrequest):
    """
    Send an email reporting error and including debug info.
    """
    mail = current.mail
    msg = '<html>A user encountered an error in {myclass}.{mymethod}' \
          'report failed.\n\nTraceback: {tb}' \
          'Local variables: {ll}' \
          'Request:\n{rq}\n' \
          '</html>'.format(myclass=instance.__class__.__name__,
                           mymethod=mymethod,
                           tb=traceback.format_exc(5),
                           ll=instance.locals(),
                           rq=myrequest)
    title = 'Paideia error'
    mail.send(mail.settings.sender, title, msg)

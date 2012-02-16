# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

if 0:
    from gluon import DAL

#TODO: set track changes to false when dev is finished
from gluon.custom_import import track_changes
from gluon.tools import Recaptcha, Mail, Auth, Crud, Service, PluginManager, prettydate
from gluon.globals import current
response, request = current.response, current.request

#set to re-load modules instead of using cached versions
track_changes(True)

# define database storage
db = DAL('sqlite://storage.sqlite')
# add db to current object so that it can be accessed from modules
current.db = db

# by default give a view/generic.extension to all actions from localhost
# none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []

crud = Crud(db)                                # for CRUD helpers using auth
service = Service()                            # for json, xml, jsonrpc, xmlrpc, amfrpc
plugins = PluginManager()                      # for configuring plugins

#configure mail
mail = Mail()                                  # mailer
mail.settings.server = 'logging' or 'smtp.gmail.com:587'  # your SMTP server
mail.settings.sender = 'scottianw@gmail.com'         # your email
mail.settings.login = 'username:password'      # your credentials or None

#configure authorization
auth = Auth(db, hmac_key=Auth.get_or_create_key()) # authentication/authorization
auth.settings.hmac_key = 'sha512:c54d15af-368c-42ab-a500-2b185d53a969'

auth.define_tables()                           # creates all needed tables

auth.settings.mailer = mail                    # for user email verification
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.messages.verify_email = 'Click on the link http://'+request.env.http_host+URL('default','user',args=['verify_email'])+'/%(key)s to verify your email'
auth.settings.reset_password_requires_verification = True
auth.messages.reset_password = 'Click on the link http://'+request.env.http_host+URL('default','user',args=['reset_password'])+'/%(key)s to reset your password'
#place auth in current so it can be imported by modules
current.auth = auth

#enable recaptcha anti-spam for selected actions
auth.settings.login_captcha = None
auth.settings.register_captcha = Recaptcha(request, '6Ley58cSAAAAAAFpawl9roIBqjk_WKqdPz3eH4Tq', '6Ley58cSAAAAAJ4Wy-k-ixP1bmzNJl0xZom8BuRT')
auth.settings.retrieve_username_captcha = Recaptcha(request, '6Ley58cSAAAAAAFpawl9roIBqjk_WKqdPz3eH4Tq', '6Ley58cSAAAAAJ4Wy-k-ixP1bmzNJl0xZom8BuRT')
auth.settings.retrieve_password_captcha = Recaptcha(request, '6Ley58cSAAAAAAFpawl9roIBqjk_WKqdPz3eH4Tq', '6Ley58cSAAAAAJ4Wy-k-ixP1bmzNJl0xZom8BuRT')

crud.settings.auth = None        # =auth to enforce authorization on crud


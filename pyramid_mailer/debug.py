import os
from pyramid_mailer import _set_mailer
from pyramid_mailer.mailer import DebugMailer


def includeme(config):
    path = os.path.join(os.getcwd(), 'mail')
    mailer = DebugMailer(path)
    _set_mailer(config, mailer)

import os
from pyramid_mailer.interfaces import IMailer
from pyramid_mailer.mailer import DebugMailer


def includeme(config):
    path = os.path.join(os.getcwd(), 'mail')
    mailer = DebugMailer(path)
    config.registry.registerUtility(mailer, IMailer)

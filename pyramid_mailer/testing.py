from pyramid_mailer.interfaces import IMailer
from pyramid_mailer.mailer import DummyMailer

def includeme(config):
    mailer = DummyMailer()
    config.registry.registerUtility(mailer, IMailer)

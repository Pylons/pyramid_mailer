from pyramid_mailer import set_mailer
from pyramid_mailer.mailer import DummyMailer


def includeme(config):
    mailer = DummyMailer()
    set_mailer(config, mailer)

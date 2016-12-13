from pyramid_mailer import _set_mailer
from pyramid_mailer.mailer import DummyMailer


def includeme(config):
    mailer = DummyMailer()
    _set_mailer(config, mailer)

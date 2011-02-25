from pyramid_mailer.mailer import Mailer

def mailer_factory_from_settings(settings, prefix='mail.'):
    return Mailer.from_settings(settings, prefix)

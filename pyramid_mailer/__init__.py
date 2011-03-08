from pyramid_mailer.mailer import Mailer
from pyramid_mailer.interfaces import IMailer

def mailer_factory_from_settings(settings, prefix='mail.'):
    """
    Factory function to create a Mailer instance from settings.
    Equivalent to **Mailer.from_settings**

    :versionadded: 0.2.2
    """
    return Mailer.from_settings(settings, prefix)


def includeme(config):
    """
    Registers a mailer instance.

    :versionadded: 0.4
    """
    settings = config.registry.settings
    prefix = settings.get('pyramid_mailer.prefix', 'mail.')
    mailer = mailer_factory_from_settings(settings, prefix=prefix)
    config.registry.registerUtility(mailer, IMailer)


def get_mailer(request):
    """Obtain a mailer previously registered via
    ``config.include('pyramid_mailer')`` or
    ``config.include('pyramid_mailer.testing')``.

    :versionadded: 0.4
    """
    registry = getattr(request, 'registry', None)
    if registry is None:
        registry = request
    return registry.getUtility(IMailer)

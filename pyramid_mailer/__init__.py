from pyramid_mailer import mailer
from pyramid_mailer.interfaces import IMailer

def mailer_factory_from_settings(settings, prefix='mail.'):
    """
    Factory function to create a Mailer instance from settings.
    Equivalent to **Mailer.from_settings**

    :versionadded: 0.2.2
    """
    import importlib

    mailer_import_path = settings.pop(prefix + 'mailer',
                                      'pyramid_mailer.mailer.Mailer')
    import_parts = mailer_import_path.split('.')
    mailer_classname = import_parts.pop(-1)
    import_path = '.'.join(import_parts)

    try:
        module = importlib.import_module(import_path)
        Mailer = getattr(module, mailer_classname)
    except (ImportError, ValueError):
        raise ImportError("Can't import module `%s`" % (import_path))
    except AttributeError:
        raise NameError("Invalid value for `mail.mailer` in config")

    settings = settings or {}

    kwarg_names = [prefix + k for k in (
                   'host', 'port', 'username',
                   'password', 'tls', 'ssl', 'keyfile',
                   'certfile', 'queue_path', 'debug', 'default_sender')]

    size = len(prefix)

    kwargs = dict(((k[size:], settings[k]) for k in settings.keys() if
                    k in kwarg_names))

    return Mailer(**kwargs)


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

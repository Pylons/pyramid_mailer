from pyramid_mailer.mailer import Mailer

def mailer_factory_from_settings(settings, prefix='mail.'):
    """
    Factory function to create a Mailer instance from settings.
    Equivalent to **Mailer.from_settings**

    :versionadded: 0.2.2
    """
    return Mailer.from_settings(settings, prefix)

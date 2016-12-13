import unittest


class TestIncludemeDebug(unittest.TestCase):
    def test_includeme(self):
        from pyramid_mailer import get_mailer
        from pyramid_mailer.interfaces import IMailer
        from pyramid_mailer.mailer import DebugMailer
        from pyramid_mailer.debug import includeme

        registry = DummyRegistry()
        config = DummyConfig(registry, {})
        includeme(config)
        self.assertEqual(registry.registered[IMailer].__class__, DebugMailer)
        self.assertEqual(config.request_methods['mailer'], {
            'callable': get_mailer,
            'reify': True,
            })


class DummyRegistry(object):
    def __init__(self, result=None):
        self.result = result
        self.registered = {}

    def registerUtility(self, impl, iface):
        self.registered[iface] = impl


class DummyConfig(object):
    def __init__(self, registry, settings):
        self.registry = registry
        self.registry.settings = settings
        self.request_methods = {}

    def add_request_method(self, callable, name, reify=False):
        self.request_methods[name] = {
            'callable': callable,
            'reify': reify,
            }

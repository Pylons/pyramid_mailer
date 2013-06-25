import unittest

class TestIncludemeTesting(unittest.TestCase):
    def test_includeme(self):
        from pyramid_mailer.interfaces import IMailer
        from pyramid_mailer.mailer import DummyMailer
        from pyramid_mailer.testing import includeme

        registry = DummyRegistry()
        config = DummyConfig(registry, {})
        includeme(config)
        self.assertEqual(registry.registered[IMailer].__class__, DummyMailer)


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



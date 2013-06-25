import unittest

class TestEncodingError(unittest.TestCase):
    def _makeOne(self):
        from pyramid_mailer.exceptions import EncodingError
        return EncodingError()

    def test_it(self):
        inst = self._makeOne()
        self.assertTrue(isinstance(inst, Exception))



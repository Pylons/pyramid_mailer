import errno
import unittest

class TestMailerSendmail(unittest.TestCase):

    def test_dummy_send_immediately_sendmail(self):

        from pyramid_mailer.mailer import DummyMailer
        from pyramid_mailer.message import Message

        mailer = DummyMailer()

        msg = Message(subject="testing",
                      sender="sender@example.com",
                      recipients=["tester@example.com"],
                      body="test")

        mailer.send_immediately_sendmail(msg)

        self.assertEqual(len(mailer.outbox), 1)

    def test_dummy_send_immediately_sendmail_and_fail_silently(self):

        from pyramid_mailer.mailer import DummyMailer
        from pyramid_mailer.message import Message

        mailer = DummyMailer()

        msg = Message(subject="testing",
                      sender="sender@example.com",
                      recipients=["tester@example.com"],
                      body="test")

        mailer.send_immediately_sendmail(msg, True)

        self.assertEqual(len(mailer.outbox), 1)

    def test_dummy_send_sendmail(self):

        from pyramid_mailer.mailer import DummyMailer
        from pyramid_mailer.message import Message

        mailer = DummyMailer()

        msg = Message(subject="testing",
                      sender="sender@example.com",
                      recipients=["tester@example.com"],
                      body="test")

        mailer.send_sendmail(msg)

        self.assertEqual(len(mailer.outbox), 1)

    def test_send_sendmail(self):
        from pyramid_mailer.mailer import Mailer
        from pyramid_mailer.message import Message

        mailer = Mailer()

        msg = Message(subject="test_send_sendmail",
                      sender="sender@example.com",
                      recipients=["tester@example.com"],
                      body="body-test_send_sendmail")
        mailer.send_sendmail(msg)

    def test_send_immediately_sendmail(self):
        email_sender = "sender@example.com"
        email_recipient = "tester@example.com"
        from pyramid_mailer.mailer import Mailer
        from pyramid_mailer.message import Message

        mailer = Mailer()
        sendmail_mailer = DummyMailer()
        mailer.sendmail_mailer = sendmail_mailer

        msg = Message(subject="test_send_immediately_sendmail",
                      sender = email_sender,
                      recipients = [ email_recipient ],
                      body="body-test_send_immediately_sendmail")
        mailer.send_immediately_sendmail(msg)
        out = sendmail_mailer.out
        self.assertEqual(len(out), 1)
        first = out[0]
        self.assertEqual(first[0], 'sender@example.com')
        self.assertEqual(first[1], set(['tester@example.com']))

    def test_send_immediately_sendmail_with_exc_fail_silently(self):
        email_sender = "sender@example.com"
        email_recipient = "tester@example.com"
        from pyramid_mailer.mailer import Mailer
        from pyramid_mailer.message import Message

        mailer = Mailer()
        sendmail_mailer = DummyMailer(ValueError())
        mailer.sendmail_mailer = sendmail_mailer

        msg = Message(subject="test_send_immediately_sendmail",
                      sender = email_sender,
                      recipients = [ email_recipient ],
                      body="body-test_send_immediately_sendmail")
        mailer.send_immediately_sendmail(msg, fail_silently=True)
        out = sendmail_mailer.out
        self.assertEqual(len(out), 0)

    def test_send_immediately_sendmail_with_exc_fail_loudly(self):
        email_sender = "sender@example.com"
        email_recipient = "tester@example.com"
        from pyramid_mailer.mailer import Mailer
        from pyramid_mailer.message import Message

        mailer = Mailer()
        sendmail_mailer = DummyMailer(ValueError())
        mailer.sendmail_mailer = sendmail_mailer

        msg = Message(subject="test_send_immediately_sendmail",
                      sender = email_sender,
                      recipients = [ email_recipient ],
                      body="body-test_send_immediately_sendmail")
        self.assertRaises(ValueError, mailer.send_immediately_sendmail, msg)
        
class TestMailer(unittest.TestCase):

    def test_dummy_send_immediately(self):

        from pyramid_mailer.mailer import DummyMailer
        from pyramid_mailer.message import Message

        mailer = DummyMailer()

        msg = Message(subject="testing",
                      sender="sender@example.com",
                      recipients=["tester@example.com"],
                      body="test")

        mailer.send_immediately(msg)

        self.assertEqual(len(mailer.outbox), 1)

    def test_dummy_send_immediately_and_fail_silently(self):

        from pyramid_mailer.mailer import DummyMailer
        from pyramid_mailer.message import Message

        mailer = DummyMailer()

        msg = Message(subject="testing",
                      sender="sender@example.com",
                      recipients=["tester@example.com"],
                      body="test")

        mailer.send_immediately(msg, True)

        self.assertEqual(len(mailer.outbox), 1)

    def test_dummy_send(self):

        from pyramid_mailer.mailer import DummyMailer
        from pyramid_mailer.message import Message

        mailer = DummyMailer()

        msg = Message(subject="testing",
                      sender="sender@example.com",
                      recipients=["tester@example.com"],
                      body="test")

        mailer.send(msg)

        self.assertEqual(len(mailer.outbox), 1)

    def test_dummy_send_to_queue(self):

        from pyramid_mailer.mailer import DummyMailer
        from pyramid_mailer.message import Message

        mailer = DummyMailer()

        msg = Message(subject="testing",
                      sender="sender@example.com",
                      recipients=["tester@example.com"],
                      body="test")

        mailer.send_to_queue(msg)

        self.assertEqual(len(mailer.queue), 1)

    def test_send_immediately(self):

        import socket

        from pyramid_mailer.mailer import Mailer
        from pyramid_mailer.message import Message

        mailer = Mailer(host='localhost', port='28322')

        msg = Message(subject="testing",
                      sender="sender@example.com",
                      recipients=["tester@example.com"],
                      body="test")

        self.assertRaises(socket.error,
                          mailer.send_immediately,
                          msg)

    def test_send_immediately_and_fail_silently(self):

        from pyramid_mailer.mailer import Mailer
        from pyramid_mailer.message import Message

        mailer = Mailer(host='localhost', port='28322')

        msg = Message(subject="testing",
                      sender="sender@example.com",
                      recipients=["tester@example.com"],
                      body="test")

        result = mailer.send_immediately(msg, True)
        self.assertEqual(result, None)

    def test_send_immediately_multipart(self):

        from pyramid_mailer.mailer import Mailer
        from pyramid_mailer.message import Message

        mailer = Mailer()

        utf_8_encoded = b'mo \xe2\x82\xac'
        utf_8 = utf_8_encoded.decode('utf_8')

        text_string = utf_8
        html_string = '<p>' + utf_8 + '</p>'

        msg = Message(subject="testing",
                      sender="sender@example.com",
                      recipients=["tester@example.com"],
                      body=text_string,
                      html=html_string)

        smtp_mailer = DummyMailer()

        mailer.smtp_mailer = smtp_mailer

        mailer.send_immediately(msg, True)

        self.assertEqual(len(smtp_mailer.out), 1)

    def test_send(self):

        from pyramid_mailer.mailer import Mailer
        from pyramid_mailer.message import Message

        mailer = Mailer()

        msg = Message(subject="testing",
                      sender="sender@example.com",
                      recipients=["tester@example.com"],
                      body="test")

        smtp_mailer = DummyMailer()
        mailer.smtp_mailer = smtp_mailer
        mailer.send(msg)
        self.assertEqual(len(smtp_mailer.out), 0)

    def test_send_to_queue_unconfigured(self):

        from pyramid_mailer.mailer import Mailer
        from pyramid_mailer.message import Message

        msg = Message(subject="testing",
                      sender="sender@example.com",
                      recipients=["tester@example.com"],
                      body="test")
        mailer = Mailer()

        self.assertRaises(RuntimeError, mailer.send_to_queue, msg)

    def test_send_to_queue(self):

        import os
        import tempfile
        import shutil

        from pyramid_mailer.mailer import Mailer
        from pyramid_mailer.message import Message

        tmpdir = tempfile.mkdtemp()
        try:
            test_queue = os.path.join(tmpdir, 'test_queue')
            for dir in ('cur', 'new', 'tmp'):
                os.makedirs(os.path.join(test_queue, dir))

            mailer = Mailer(queue_path=test_queue)

            msg = Message(subject="testing",
                          sender="sender@example.com",
                          recipients=["tester@example.com"],
                          body="test")

            queuedelivery = DummyMailer()
            mailer.queue_delivery = queuedelivery

            mailer.send_to_queue(msg)
            self.assertEqual(len(queuedelivery.out), 1)
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_use_ssl_mailer(self):

        from pyramid_mailer.mailer import Mailer
        from pyramid_mailer._compat import SMTP_SSL
        from smtplib import SMTP

        mailer = Mailer(ssl=True)
        mailer
        if SMTP_SSL is not None:
            self.assertEqual(mailer.direct_delivery.mailer.smtp, SMTP_SSL)

        else:  # pragma: no cover
            self.assertEqual(mailer.direct_delivery.mailer.smtp, SMTP)

    def test_from_settings_factory(self):

        from pyramid_mailer._compat import SMTP_SSL
        from smtplib import SMTP
        from pyramid_mailer import mailer_factory_from_settings

        settings = {'mymail.host': 'my.server.com',
                    'mymail.port': 123,
                    'mymail.username': 'tester',
                    'mymail.password': 'test',
                    'mymail.tls': True,
                    'mymail.ssl': True,
                    'mymail.keyfile': 'ssl.key',
                    'mymail.certfile': 'ssl.crt',
                    'mymail.queue_path': '/tmp',
                    'mymail.debug': 1}

        mailer = mailer_factory_from_settings(settings, prefix='mymail.')

        self.assertEqual(mailer.direct_delivery.mailer.hostname,
                         'my.server.com')
        self.assertEqual(mailer.direct_delivery.mailer.port, 123)
        self.assertEqual(mailer.direct_delivery.mailer.username, 'tester')
        self.assertEqual(mailer.direct_delivery.mailer.password, 'test')
        self.assertEqual(mailer.direct_delivery.mailer.force_tls, True)
        if SMTP_SSL is not None:
            self.assertEqual(mailer.direct_delivery.mailer.smtp, SMTP_SSL)
        else:  # pragma: no cover
            self.assertEqual(mailer.direct_delivery.mailer.smtp, SMTP)

        self.assertEqual(mailer.direct_delivery.mailer.keyfile, 'ssl.key')
        self.assertEqual(mailer.direct_delivery.mailer.certfile, 'ssl.crt')
        self.assertEqual(mailer.queue_delivery.queuePath, '/tmp')
        self.assertEqual(mailer.direct_delivery.mailer.debug_smtp, 1)

    def test_from_settings(self):

        from pyramid_mailer._compat import SMTP_SSL
        from smtplib import SMTP
        from pyramid_mailer.mailer import Mailer

        settings = {'mymail.host': 'my.server.com',
                    'mymail.port': 123,
                    'mymail.username': 'tester',
                    'mymail.password': 'test',
                    'mymail.tls': 'false',
                    'mymail.ssl': True,
                    'mymail.keyfile': 'ssl.key',
                    'mymail.certfile': 'ssl.crt',
                    'mymail.queue_path': '/tmp',
                    'mymail.debug': 1}

        mailer = Mailer.from_settings(settings, prefix='mymail.')

        self.assertEqual(mailer.direct_delivery.mailer.hostname,
                         'my.server.com')
        self.assertEqual(mailer.direct_delivery.mailer.port, 123)
        self.assertEqual(mailer.direct_delivery.mailer.username, 'tester')
        self.assertEqual(mailer.direct_delivery.mailer.password, 'test')
        self.assertEqual(mailer.direct_delivery.mailer.force_tls, False)
        if SMTP_SSL is not None:
            self.assertEqual(mailer.direct_delivery.mailer.smtp, SMTP_SSL)
        else:  # pragma: no cover
            self.assertEqual(mailer.direct_delivery.mailer.smtp, SMTP)

        self.assertEqual(mailer.direct_delivery.mailer.keyfile, 'ssl.key')
        self.assertEqual(mailer.direct_delivery.mailer.certfile, 'ssl.crt')
        self.assertEqual(mailer.queue_delivery.queuePath, '/tmp')
        self.assertEqual(mailer.direct_delivery.mailer.debug_smtp, 1)

class TestSMTP_SSLMailer(unittest.TestCase):
    def _makeOne(self, *arg, **kw):
        from pyramid_mailer.mailer import SMTP_SSLMailer
        return SMTP_SSLMailer(*arg, **kw)
    
    def test_ctor(self):
        inst = self._makeOne(keyfile='keyfile', certfile='certfile')
        self.assertEqual(inst.keyfile, 'keyfile')
        self.assertEqual(inst.certfile, 'certfile')
        
    def test_smtp_factory_smtp_is_None(self):
        inst = self._makeOne()
        inst.smtp = None
        self.assertRaises(RuntimeError, inst.smtp_factory)

    def test_smtp_factory_smtp_is_not_None(self):
        inst = self._makeOne(
            debug_smtp=9,
            hostname='hostname',
            port=25,
            certfile='certfile',
            keyfile='keyfile'
            )
        inst.smtp = DummyConnectionFactory
        conn = inst.smtp_factory()
        self.assertEqual(conn.hostname, 'hostname')
        self.assertEqual(conn.port, '25')
        self.assertEqual(conn.certfile, 'certfile')
        self.assertEqual(conn.keyfile, 'keyfile')
        self.assertEqual(conn.debuglevel, 9)

class DummyConnectionFactory(object):
    def __init__(self, hostname, port, keyfile=None, certfile=None):
        self.hostname = hostname
        self.port = port
        self.keyfile = keyfile
        self.certfile = certfile

    def set_debuglevel(self, level):
        self.debuglevel = level

class DummyMailer(object):
    def __init__(self, raises=None):
        self.out = []
        self.raises = raises

    def send(self, frm, to, msg):
        if self.raises:
            raise self.raises
        self.out.append((frm, to, msg))


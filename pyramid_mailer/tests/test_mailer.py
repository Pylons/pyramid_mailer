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
        sendmail_mailer = DummySendmailMailer()
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
        sendmail_mailer = DummySendmailMailer(ValueError())
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
        sendmail_mailer = DummySendmailMailer(ValueError())
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

        mailer.send_immediately(msg, True)

    def test_send(self):

        from pyramid_mailer.mailer import Mailer
        from pyramid_mailer.message import Message

        mailer = Mailer()

        msg = Message(subject="testing",
                      sender="sender@example.com",
                      recipients=["tester@example.com"],
                      body="test")

        mailer.send(msg)

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

        from pyramid_mailer.mailer import Mailer
        from pyramid_mailer.message import Message

        test_queue = os.path.join(tempfile.gettempdir(), 'test_queue')
        for dir in ('cur', 'new', 'tmp'):
            try:
                os.makedirs(os.path.join(test_queue, dir))
            except OSError:
                pass

        mailer = Mailer(queue_path=test_queue)

        msg = Message(subject="testing",
                      sender="sender@example.com",
                      recipients=["tester@example.com"],
                      body="test")

        mailer.send_to_queue(msg)

    def test_use_ssl_mailer(self):

        try:
            from smtplib import SMTP_SSL
            ssl_enabled = True
        except ImportError:  # pragma: no cover
            from smtplib import SMTP
            ssl_enabled = False
        from pyramid_mailer.mailer import Mailer

        mailer = Mailer(ssl=True)
        if ssl_enabled:
            self.assertEqual(mailer.direct_delivery.mailer.smtp, SMTP_SSL)
            from ssl import SSLError
            try:
                self.assertTrue(mailer.direct_delivery.mailer.smtp_factory())
            except (IOError, SSLError):
                pass

        else:  # pragma: no cover
            self.assertEqual(mailer.direct_delivery.mailer.smtp, SMTP)
            import socket
            try:
                self.assertTrue(mailer.direct_delivery.mailer.smtp_factory())
            except socket.error as e:
                error_number = e.args[0]
                # smtp mailer might fail to resolve hostname
                self.assertTrue(error_number in
                                (errno.ENODATA,
                                 errno.ECONNREFUSED  # BBB Python 2.5 compat
                                 ))

    def test_from_settings_factory(self):

        try:
            from smtplib import SMTP_SSL
            ssl_enabled = True
        except ImportError:  # pragma: no cover
            from smtplib import SMTP
            ssl_enabled = False
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
        if ssl_enabled:
            self.assertEqual(mailer.direct_delivery.mailer.smtp, SMTP_SSL)
        else:  # pragma: no cover
            self.assertEqual(mailer.direct_delivery.mailer.smtp, SMTP)

        self.assertEqual(mailer.direct_delivery.mailer.keyfile, 'ssl.key')
        self.assertEqual(mailer.direct_delivery.mailer.certfile, 'ssl.crt')
        self.assertEqual(mailer.queue_delivery.queuePath, '/tmp')
        self.assertEqual(mailer.direct_delivery.mailer.debug_smtp, 1)

    def test_from_settings(self):

        try:
            from smtplib import SMTP_SSL
            ssl_enabled = True
        except ImportError:  # pragma: no cover
            from smtplib import SMTP
            ssl_enabled = False
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
        if ssl_enabled:
            self.assertEqual(mailer.direct_delivery.mailer.smtp, SMTP_SSL)
        else:  # pragma: no cover
            self.assertEqual(mailer.direct_delivery.mailer.smtp, SMTP)

        self.assertEqual(mailer.direct_delivery.mailer.keyfile, 'ssl.key')
        self.assertEqual(mailer.direct_delivery.mailer.certfile, 'ssl.crt')
        self.assertEqual(mailer.queue_delivery.queuePath, '/tmp')
        self.assertEqual(mailer.direct_delivery.mailer.debug_smtp, 1)


class DummySendmailMailer(object):
    def __init__(self, raises=None):
        self.out = []
        self.raises = raises

    def send(self, frm, to, msg):
        if self.raises:
            raise self.raises
        self.out.append((frm, to, msg))
        

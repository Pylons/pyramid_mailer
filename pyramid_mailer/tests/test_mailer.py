import os
import unittest


class _Base(unittest.TestCase):

    _tempdir = None

    def tearDown(self):
        if self._tempdir is not None:
            from shutil import rmtree
            rmtree(self._tempdir)

    def _makeTempdir(self):
        from tempfile import mkdtemp
        if self._tempdir is None:
            self._tempdir = mkdtemp()
        return self._tempdir


class DebugMailerTests(_Base):

    def _getTargetClass(self):
        from pyramid_mailer.mailer import DebugMailer
        return DebugMailer

    def _makeOne(self, tld=None):
        if tld is None:
            tld = self._makeTempdir()
        return self._getTargetClass()(tld)

    def _listFiles(self):
        from os import listdir
        return listdir(self._tempdir)

    def test___init___wo_existing_directory(self):
        from os.path import isdir
        from shutil import rmtree
        tempdir = self._makeTempdir()
        rmtree(tempdir)
        mailer = self._makeOne(tempdir)
        self.assertTrue(isdir(tempdir))

    def test_from_settings(self):
        tempdir = self._makeTempdir()
        settings = {'mail.top_level_directory': tempdir}
        mailer = self._getTargetClass().from_settings(settings, 'mail.')
        self.assertEqual(mailer.tld, tempdir)

    def test_from_settings_wo_tld(self):
        tempdir = self._makeTempdir()
        self.assertRaises(ValueError,
                          self._getTargetClass().from_settings, None)

    def test_invalid_bind_options(self):
        mailer = self._makeOne()
        self.assertRaises(ValueError, mailer.bind, foo='bar')

    def test_bind(self):
        mailer = self._makeOne()
        dummy = object()
        result = mailer.bind(transaction_manager=dummy, default_sender='foo')
        self.assertIs(result, mailer)

    def test__send(self):
        mailer = self._makeOne()
        msg = _makeMessage()
        mailer.send_sendmail(msg)
        files = self._listFiles()
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0][-4:], '.eml')

    def test_default_sender(self):
        mailer = self._makeOne()
        msg = _makeMessage(sender=None)
        mailer.send_sendmail(msg)
        files = self._listFiles()
        self.assertEqual(len(files), 1)
        with open(os.path.join(self._tempdir, files[0]), 'r') as msg:
            self.assertTrue('From: nobody' in msg.read())


class DummyMailerTests(unittest.TestCase):

    def _getTargetClass(self):
        from pyramid_mailer.mailer import DummyMailer
        return DummyMailer

    def _makeOne(self):
        return self._getTargetClass()()

    def test_invalid_bind_options(self):
        mailer = self._makeOne()
        self.assertRaises(ValueError, mailer.bind, foo='bar')

    def test_bind(self):
        mailer = self._makeOne()
        dummy = object()
        result = mailer.bind(transaction_manager=dummy, default_sender='foo')
        self.assertIs(result, mailer)

    def test_send(self):
        mailer = self._makeOne()
        msg = _makeMessage()
        mailer.send(msg)
        self.assertEqual(mailer.outbox, [msg])

    def test_send_immediately(self):
        mailer = self._makeOne()
        msg = _makeMessage()
        mailer.send_immediately(msg)
        self.assertEqual(mailer.outbox, [msg])

    def test_send_immediately_w_fail_silently(self):
        mailer = self._makeOne()
        msg = _makeMessage()
        mailer.send_immediately(msg, True)
        self.assertEqual(mailer.outbox, [msg])

    def test_send_to_queue(self):
        mailer = self._makeOne()
        msg = _makeMessage()
        mailer.send_to_queue(msg)
        self.assertEqual(mailer.queue, [msg])

    def test_send_sendmail(self):
        mailer = self._makeOne()
        msg = _makeMessage()
        mailer.send_sendmail(msg)
        self.assertEqual(mailer.outbox, [msg])

    def test_send_immediately_sendmail(self):
        mailer = self._makeOne()
        msg = _makeMessage()
        mailer.send_immediately_sendmail(msg)
        self.assertEqual(mailer.outbox, [msg])

    def test_send_immediately_sendmail_w_fail_silently(self):
        mailer = self._makeOne()
        msg = _makeMessage()
        mailer.send_immediately_sendmail(msg, True)
        self.assertEqual(mailer.outbox, [msg])


class TestSMTP_SSLMailer(unittest.TestCase):

    def _getTargetClass(self):
        from pyramid_mailer.mailer import SMTP_SSLMailer
        return SMTP_SSLMailer

    def _makeOne(self, *arg, **kw):
        return self._getTargetClass()(*arg, **kw)

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

class MailerTests(_Base):

    def _getTargetClass(self):
        from pyramid_mailer.mailer import Mailer
        return Mailer

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test___init___w_ssl(self):
        from smtplib import SMTP
        from pyramid_mailer._compat import SMTP_SSL
        mailer = self._makeOne(ssl=True)
        mailer
        if SMTP_SSL is not None:
            self.assertEqual(mailer.direct_delivery.mailer.smtp, SMTP_SSL)
        else:  # pragma: no cover
            self.assertEqual(mailer.direct_delivery.mailer.smtp, SMTP)

    def test_from_settings(self):
        from smtplib import SMTP
        from pyramid_mailer._compat import SMTP_SSL
        settings = {'mymail.host': 'my.server.com',
                    'mymail.port': 123,
                    'mymail.username': 'tester',
                    'mymail.password': 'test',
                    'mymail.tls': 'false',
                    'mymail.ssl': True,
                    'mymail.keyfile': 'ssl.key',
                    'mymail.certfile': 'ssl.crt',
                    'mymail.queue_path': '/tmp',
                    'mymail.debug': 1,
                    'mymail.sendmail_app': 'sendmail_app',
                    'mymail.sendmail_template':
                        '{sendmail_app} --option1 --option2 {sender}'}
        mailer = self._getTargetClass().from_settings(settings,
                                                      prefix='mymail.')
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
        self.assertEqual(mailer.sendmail_mailer.sendmail_app, 'sendmail_app')
        self.assertEqual(mailer.sendmail_mailer.sendmail_template,
                    ['{sendmail_app}', '--option1', '--option2', '{sender}'])

    def test_from_settings_with_str_values(self):
        from smtplib import SMTP
        from pyramid_mailer._compat import SMTP_SSL
        settings = {'mymail.host': 'my.server.com',
                    'mymail.port': '123',
                    'mymail.username': 'tester',
                    'mymail.password': 'test',
                    'mymail.tls': 'false',
                    'mymail.ssl': True,
                    'mymail.keyfile': 'ssl.key',
                    'mymail.certfile': 'ssl.crt',
                    'mymail.queue_path': '/tmp',
                    'mymail.debug': '1',
                    'mymail.sendmail_app': 'sendmail_app',
                    'mymail.sendmail_template':
                        '{sendmail_app} --option1 --option2 {sender}'}
        mailer = self._getTargetClass().from_settings(settings,
                                                      prefix='mymail.')
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
        self.assertEqual(mailer.sendmail_mailer.sendmail_app, 'sendmail_app')
        self.assertEqual(mailer.sendmail_mailer.sendmail_template,
                    ['{sendmail_app}', '--option1', '--option2', '{sender}'])

    def test_invalid_init_options(self):
        self.assertRaises(ValueError, self._makeOne, foo='bar')

    def test_invalid_bind_options(self):
        mailer = self._makeOne()
        self.assertRaises(ValueError, mailer.bind, foo='bar')

    def test_bind(self):
        mailer = self._makeOne()
        dummy = object()
        result = mailer.bind(transaction_manager=dummy, default_sender='foo')
        self.assertTrue(result.transaction_manager is dummy)
        self.assertEqual(result.default_sender, 'foo')

    def test_from_settings_with_empty_username(self):
        settings = {'mymail.username': '',
                    'mymail.password': ''}
        mailer = self._getTargetClass().from_settings(settings,
                                                      prefix='mymail.')
        self.assertEqual(mailer.direct_delivery.mailer.username, None)
        self.assertEqual(mailer.direct_delivery.mailer.password, None)

    def test_send_immediately(self):
        import socket
        mailer = self._makeOne(host='localhost', port='28322')
        msg = _makeMessage()
        self.assertRaises(socket.error,
                          mailer.send_immediately,
                          msg)

    def test_send_immediately_and_fail_silently(self):
        mailer = self._makeOne(host='localhost', port='28322')
        msg = _makeMessage()

        result = mailer.send_immediately(msg, True)
        self.assertEqual(result, None)

    def test_send_immediately_multipart(self):
        mailer = self._makeOne()
        utf_8_encoded = b'mo \xe2\x82\xac'
        utf_8 = utf_8_encoded.decode('utf_8')
        text_string = utf_8
        html_string = '<p>' + utf_8 + '</p>'
        msg = _makeMessage(body=text_string, html=html_string)
        smtp_mailer = DummyMailer()
        mailer.smtp_mailer = smtp_mailer
        mailer.send_immediately(msg, True)
        self.assertEqual(len(smtp_mailer.out), 1)

    def test_send(self):
        mailer = self._makeOne()
        msg = _makeMessage()
        smtp_mailer = DummyMailer()
        mailer.smtp_mailer = smtp_mailer
        mailer.send(msg)
        self.assertEqual(len(smtp_mailer.out), 0)

    def test_send_to_queue_unconfigured(self):
        msg = _makeMessage()
        mailer = self._makeOne()
        self.assertRaises(RuntimeError, mailer.send_to_queue, msg)

    def test_send_to_queue(self):
        import os
        test_queue = os.path.join(self._makeTempdir(), 'test_queue')
        for dir in ('cur', 'new', 'tmp'):
            os.makedirs(os.path.join(test_queue, dir))
        mailer = self._makeOne(queue_path=test_queue)
        msg = _makeMessage()
        queuedelivery = DummyMailer()
        mailer.queue_delivery = queuedelivery
        mailer.send_to_queue(msg)
        self.assertEqual(len(queuedelivery.out), 1)

    def test_send_sendmail(self):
        mailer = self._makeOne()
        msg = _makeMessage()
        mailer.send_sendmail(msg)

    def test_send_immediately_sendmail(self):
        email_sender = "sender@example.com"
        email_recipient = "tester@example.com"
        mailer = self._makeOne()
        sendmail_mailer = DummyMailer()
        mailer.sendmail_mailer = sendmail_mailer
        msg = _makeMessage(subject="test_send_immediately_sendmail",
                           body="body-test_send_immediately_sendmail")
        mailer.send_immediately_sendmail(msg)
        out = sendmail_mailer.out
        self.assertEqual(len(out), 1)
        first = out[0]
        self.assertEqual(first[0], 'sender@example.com')
        self.assertEqual(first[1], {'tester@example.com'})

    def test_send_immediately_sendmail_with_exc_fail_silently(self):
        email_sender = "sender@example.com"
        email_recipient = "tester@example.com"
        mailer = self._makeOne()
        sendmail_mailer = DummyMailer(ValueError())
        mailer.sendmail_mailer = sendmail_mailer
        msg = _makeMessage(subject="test_send_immediately_sendmail",
                           body="body-test_send_immediately_sendmail")
        mailer.send_immediately_sendmail(msg, fail_silently=True)
        out = sendmail_mailer.out
        self.assertEqual(len(out), 0)

    def test_send_immediately_sendmail_with_exc_fail_loudly(self):
        email_sender = "sender@example.com"
        email_recipient = "tester@example.com"
        mailer = self._makeOne()
        sendmail_mailer = DummyMailer(ValueError())
        mailer.sendmail_mailer = sendmail_mailer
        msg = _makeMessage(subject="test_send_immediately_sendmail",
                           body="body-test_send_immediately_sendmail")
        self.assertRaises(ValueError, mailer.send_immediately_sendmail, msg)


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


def _makeMessage(subject="testing",
                sender="sender@example.com",
                recipients=["tester@example.com"],
                body="test",
                **kw):
    from pyramid_mailer.message import Message
    return Message(subject=subject,
                   sender=sender,
                   recipients=recipients,
                   body=body,
                   **kw)

# -*- coding: utf-8 -*-
import unittest
import os

from pyramid import testing

here = os.path.dirname(os.path.abspath(__file__))

class TestAttachment(unittest.TestCase):

    def test_data_from_string(self):

        from pyramid_mailer.message import Attachment

        a = Attachment(data="foo")
        self.assert_(a.data == "foo")

    def test_data_from_file_obj(self):

        from StringIO import StringIO
        from pyramid_mailer.message import Attachment

        a = Attachment(data=StringIO("foo"))
        self.assert_(a.data == "foo")


class TestMessage(unittest.TestCase):

    def test_initialize(self):

        from pyramid_mailer.message import Message

        msg = Message(subject="subject",
                      sender="support@mysite.com",
                      recipients=["to@example.com"])


        self.assert_(msg.subject == "subject")
        self.assert_(msg.sender == "support@mysite.com")
        self.assert_(msg.recipients == ["to@example.com"])

    def test_recipients_properly_initialized(self):

        from pyramid_mailer.message import Message

        msg = Message(subject="subject")

        self.assert_(msg.recipients == [])

        msg2 = Message(subject="subject")
        msg2.add_recipient("somebody@here.com")

        self.assert_(len(msg.recipients) == 0)

        msg3 = Message(subject="subject")
        msg3.add_recipient("somebody@here.com")

        self.assert_(len(msg.recipients) == 0)

    def test_add_recipient(self):

        from pyramid_mailer.message import Message

        msg = Message("testing")
        msg.add_recipient("to@example.com")

        self.assert_(msg.recipients == ["to@example.com"])

    def test_add_cc(self):

        from pyramid_mailer.message import Message

        msg = Message("testing")
        msg.add_cc("to@example.com")

        self.assert_(msg.cc == ["to@example.com"])

    def test_add_bcc(self):

        from pyramid_mailer.message import Message

        msg = Message("testing")
        msg.add_bcc("to@example.com")

        self.assert_(msg.bcc == ["to@example.com"])
    
    def test_send_without_sender(self):

        from pyramid_mailer.message import Message
        from pyramid_mailer.mailer import Mailer
        from pyramid_mailer.exceptions import InvalidMessage

        msg = Message(subject="testing",
                      recipients=["to@example.com"],
                      body="testing")

        mailer = Mailer()

        self.assertRaises(InvalidMessage, mailer.send, msg)

    def test_send_without_recipients(self):

        from pyramid_mailer.message import Message
        from pyramid_mailer.mailer import Mailer
        from pyramid_mailer.exceptions import InvalidMessage

        mailer = Mailer()

        msg = Message(subject="testing",
                      recipients=[],
                      body="testing")

        self.assertRaises(InvalidMessage, mailer.send, msg)

    def test_send_without_body(self):

        from pyramid_mailer.message import Message
        from pyramid_mailer.mailer import Mailer
        from pyramid_mailer.exceptions import InvalidMessage

        msg = Message(subject="testing",
                      sender="sender@example.com",
                      recipients=["to@example.com"])

        mailer = Mailer()

        self.assertRaises(InvalidMessage, mailer.send, msg)

        msg.html = "<b>test</b>"

        mailer.send(msg)

    def test_cc(self):

        from pyramid_mailer.message import Message

        msg = Message(subject="testing",
                      sender="sender@example.com",
                      recipients=["to@example.com"],
                      body="testing",
                      cc=["tosomeoneelse@example.com"])

        response = msg.get_response()
        self.assert_("Cc: tosomeoneelse@example.com" in str(response))

    def test_attach(self):

        from pyramid_mailer.message import Message
        from pyramid_mailer.message import Attachment

        msg = Message(subject="testing",
                      recipients=["to@example.com"],
                      body="testing")
        
        msg.attach(Attachment(data="this is a test", 
                              content_type="text/plain"))
        

        a = msg.attachments[0]
        
        self.assert_(a.filename is None)
        self.assert_(a.disposition == 'attachment')
        self.assert_(a.content_type == "text/plain")
        self.assert_(a.data == "this is a test")
 
        response = msg.get_response()
        
        self.assert_(len(response.attachments) == 1)

    def test_bad_header_subject(self):

        from pyramid_mailer.message import Message
        from pyramid_mailer.mailer import Mailer

        from pyramid_mailer.exceptions import BadHeaders

        msg = Message(subject="testing\n\r",
                      sender="from@example.com",
                      body="testing",
                      recipients=["to@example.com"])

        mailer = Mailer()

        self.assertRaises(BadHeaders, mailer.send, msg)

    def test_bad_header_sender(self):

        from pyramid_mailer.message import Message
        from pyramid_mailer.mailer import Mailer

        from pyramid_mailer.exceptions import BadHeaders

        mailer = Mailer()

        msg = Message(subject="testing",
                      sender="from@example.com\n\r",
                      recipients=["to@example.com"],
                      body="testing")

        self.assertRaises(BadHeaders, mailer.send, msg)

    def test_bad_header_recipient(self):

        from pyramid_mailer.message import Message
        from pyramid_mailer.mailer import Mailer

        from pyramid_mailer.exceptions import BadHeaders

        mailer = Mailer()

        msg = Message(subject="testing",
                      sender="from@example.com",
                      recipients=[
                          "to@example.com",
                          "to\r\n@example.com"],
                      body="testing")

        self.assertRaises(BadHeaders, mailer.send, msg)

    def test_send_to(self):

        from pyramid_mailer.message import Message

        msg = Message(subject="testing",
                      sender="from@example.com",
                      recipients=[
                          "to@example.com"],
                      cc=['somebodyelse@example.com', 
                          'to@example.com'],
                      bcc=['anotherperson@example.com'],
                      body="testing")


        self.assert_(msg.send_to == set(["to@example.com",
                                        "somebodyelse@example.com",
                                        "anotherperson@example.com"]))

    def test_is_bad_headers_if_no_bad_headers(self):
        from pyramid_mailer.message import Message
        msg = Message(subject="testing",
                      sender="from@example.com",
                      body="testing",
                      recipients=["to@example.com"])

        self.assert_(not(msg.is_bad_headers()))

    def test_is_bad_headers_if_subject_empty(self):
        from pyramid_mailer.message import Message
        msg = Message(sender="from@example.com",
                      body="testing",
                      recipients=["to@example.com"])

        self.assert_(not(msg.is_bad_headers()))

    def test_is_bad_headers_if_bad_headers(self):

        from pyramid_mailer.message import Message
        msg = Message(subject="testing\n\r",
                      sender="from@\nexample.com",
                      body="testing",
                      recipients=["to@example.com"])

        self.assert_(msg.is_bad_headers())

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

        self.assert_(len(mailer.outbox)) == 1
 

    def test_dummy_send_immediately_and_fail_silently(self):

        from pyramid_mailer.mailer import DummyMailer
        from pyramid_mailer.message import Message

        mailer = DummyMailer()

        msg = Message(subject="testing",
                      sender="sender@example.com",
                      recipients=["tester@example.com"],
                      body="test")

        mailer.send_immediately(msg, True)

        self.assert_(len(mailer.outbox)) == 1
 
    def test_dummy_send(self):

        from pyramid_mailer.mailer import DummyMailer
        from pyramid_mailer.message import Message

        mailer = DummyMailer()

        msg = Message(subject="testing",
                      sender="sender@example.com",
                      recipients=["tester@example.com"],
                      body="test")

        mailer.send(msg)

        self.assert_(len(mailer.outbox)) == 1

    def test_dummy_send_to_queue(self):

        from pyramid_mailer.mailer import DummyMailer
        from pyramid_mailer.message import Message

        mailer = DummyMailer()

        msg = Message(subject="testing",
                      sender="sender@example.com",
                      recipients=["tester@example.com"],
                      body="test")

        mailer.send_to_queue(msg)

        self.assert_(len(mailer.queue)) == 1

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

        mailer = Mailer()

        msg = Message(subject="testing",
                      sender="sender@example.com",
                      recipients=["tester@example.com"],
                      body="test")

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
        except ImportError: # pragma: no cover
            from smtplib import SMTP
            ssl_enabled = False
        from pyramid_mailer.mailer import Mailer

        mailer = Mailer(ssl=True)
        if ssl_enabled:
            self.assert_(mailer.direct_delivery.mailer.smtp == SMTP_SSL)
            from ssl import SSLError
            try:
                self.assert_(mailer.direct_delivery.mailer.smtp_factory())
            except (IOError, SSLError):
                pass

        else: # pragma: no cover
            self.assert_(mailer.direct_delivery.mailer.smtp == SMTP)
            import socket
            try:
                self.assert_(mailer.direct_delivery.mailer.smtp_factory())
            except socket.error, e:
                # smtp mailer might fail to resolve hostname
                self.assert_(e.args[0] == 61)

                          
    def test_from_settings_factory(self):

        try:
            from smtplib import SMTP_SSL
            ssl_enabled = True
        except ImportError: # pragma: no cover
            from smtplib import SMTP
            ssl_enabled = False
        from pyramid_mailer import mailer_factory_from_settings

        settings = {'mymail.host' : 'my.server.com',
                    'mymail.port' : 123,
                    'mymail.username' : 'tester',
                    'mymail.password' : 'test',
                    'mymail.tls' : True,
                    'mymail.ssl' : True,
                    'mymail.keyfile' : 'ssl.key',
                    'mymail.certfile' : 'ssl.crt',
                    'mymail.queue_path' : '/tmp',
                    'mymail.debug' : 1}

        mailer = mailer_factory_from_settings(settings, prefix='mymail.')

        self.assert_(mailer.direct_delivery.mailer.hostname=='my.server.com')
        self.assert_(mailer.direct_delivery.mailer.port==123)
        self.assert_(mailer.direct_delivery.mailer.username=='tester')
        self.assert_(mailer.direct_delivery.mailer.password=='test')
        self.assert_(mailer.direct_delivery.mailer.force_tls==True)
        if ssl_enabled:
            self.assert_(mailer.direct_delivery.mailer.smtp == SMTP_SSL)
        else: # pragma: no cover
            self.assert_(mailer.direct_delivery.mailer.smtp == SMTP)

        self.assert_(mailer.direct_delivery.mailer.keyfile == 'ssl.key')
        self.assert_(mailer.direct_delivery.mailer.certfile == 'ssl.crt')
        self.assert_(mailer.queue_delivery.queuePath == '/tmp')
        self.assert_(mailer.direct_delivery.mailer.debug_smtp == 1)


    def test_from_settings(self):
        
        try:
            from smtplib import SMTP_SSL
            ssl_enabled = True
        except ImportError: # pragma: no cover
            from smtplib import SMTP
            ssl_enabled = False
        from pyramid_mailer.mailer import Mailer

        settings = {'mymail.host' : 'my.server.com',
                    'mymail.port' : 123,
                    'mymail.username' : 'tester',
                    'mymail.password' : 'test',
                    'mymail.tls' : True,
                    'mymail.ssl' : True,
                    'mymail.keyfile' : 'ssl.key',
                    'mymail.certfile' : 'ssl.crt',
                    'mymail.queue_path' : '/tmp',
                    'mymail.debug' : 1}

        mailer = Mailer.from_settings(settings, prefix='mymail.')

        self.assert_(mailer.direct_delivery.mailer.hostname=='my.server.com')
        self.assert_(mailer.direct_delivery.mailer.port==123)
        self.assert_(mailer.direct_delivery.mailer.username=='tester')
        self.assert_(mailer.direct_delivery.mailer.password=='test')
        self.assert_(mailer.direct_delivery.mailer.force_tls==True)
        if ssl_enabled:
            self.assert_(mailer.direct_delivery.mailer.smtp == SMTP_SSL)
        else: # pragma: no cover
            self.assert_(mailer.direct_delivery.mailer.smtp == SMTP)

        self.assert_(mailer.direct_delivery.mailer.keyfile == 'ssl.key')
        self.assert_(mailer.direct_delivery.mailer.certfile == 'ssl.crt')
        self.assert_(mailer.queue_delivery.queuePath == '/tmp')
        self.assert_(mailer.direct_delivery.mailer.debug_smtp == 1)


class TestGetMailer(unittest.TestCase):

    def _get_mailer(self, arg):
        from pyramid_mailer import get_mailer
        return get_mailer(arg)

    def test_arg_is_registry(self):
        mailer = object()
        registry = DummyRegistry(mailer)
        result = self._get_mailer(registry)
        self.assertEqual(result, mailer)

    def test_arg_is_request(self):
        class Dummy(object):
            pass
        mailer = object()
        registry = DummyRegistry(mailer)
        request = Dummy()
        request.registry = registry
        result = self._get_mailer(request)
        self.assertEqual(result, mailer)


class Test_includeme(unittest.TestCase):
    def _do_includeme(self, config):
        from pyramid_mailer import includeme
        includeme(config)

    def test_with_default_prefix(self):
        from pyramid_mailer.interfaces import IMailer
        registry = DummyRegistry()
        settings = {'mail.default_sender':'sender'}
        config = DummyConfig(registry, settings)
        self._do_includeme(config)
        self.assertEqual(registry.registered[IMailer].default_sender, 'sender')

    def test_with_specified_prefix(self):
        from pyramid_mailer.interfaces import IMailer
        registry = DummyRegistry()
        settings = {'pyramid_mailer.prefix':'foo.',
                    'foo.default_sender':'sender'}
        config = DummyConfig(registry, settings)
        self._do_includeme(config)
        self.assertEqual(registry.registered[IMailer].default_sender, 'sender')


class TestIncludemeTesting(unittest.TestCase):
    def test_includeme(self):
        from pyramid_mailer.interfaces import IMailer
        from pyramid_mailer.mailer import DummyMailer
        from pyramid_mailer.testing import includeme

        registry = DummyRegistry()
        config = DummyConfig(registry, {})
        includeme(config)
        self.assertEqual(registry.registered[IMailer].__class__, DummyMailer)

class TestFunctional(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_get_mailer_realthing(self):
        from pyramid_mailer import get_mailer
        from pyramid_mailer.mailer import Mailer
        self.config.include('pyramid_mailer')
        request = testing.DummyRequest()
        mailer = get_mailer(request)
        self.assertEqual(mailer.__class__, Mailer)

    def test_get_mailer_dummy(self):
        from pyramid_mailer import get_mailer
        from pyramid_mailer.testing import DummyMailer
        self.config.include('pyramid_mailer.testing')
        request = testing.DummyRequest()
        mailer = get_mailer(request)
        self.assertEqual(mailer.__class__, DummyMailer)

class DummyConfig(object):
    def __init__(self, registry, settings):
        self.registry = registry
        self.registry.settings = settings


class DummyRegistry(object):
    def __init__(self, result=None):
        self.result = result
        self.registered = {}

    def getUtility(self, iface):
        return self.result

    def registerUtility(self, impl, iface):
        self.registered[iface] = impl

class TestEncodingError(unittest.TestCase):
    def _makeOne(self):
        from pyramid_mailer.response import EncodingError
        return EncodingError()

    def test_it(self):
        inst = self._makeOne()
        self.assertTrue(isinstance(inst, Exception))

class Test_normalize_header(unittest.TestCase):
    def _callFUT(self, header):
        from pyramid_mailer.response import normalize_header
        return normalize_header(header)

    def test_it(self):
        result = self._callFUT('content-type')
        self.assertEqual(result, 'Content-Type')

class TestMailBase(unittest.TestCase):
    def _makeOne(self, items=()):
        from pyramid_mailer.response import MailBase
        return MailBase(items)

    def test___getitem__hit(self):
        base = self._makeOne([('Content-Type', 'text/html')])
        self.assertEqual(base['content-type'], 'text/html')
        
    def test___getitem__miss(self):
        base = self._makeOne([('Content-Type', 'text/html')])
        self.assertEqual(base['Wrong'], None)

    def test___iter__(self):
        base = self._makeOne([('Content-Type', 'text/html')])
        self.assertEqual(list(base), ['Content-Type'])

    def test___contains__(self):
        base = self._makeOne([('Content-Type', 'text/html')])
        self.assertTrue('content-type' in base)

    def test___delitem__(self):
        base = self._makeOne([('Content-Type', 'text/html')])
        del base['content-type']
        self.assertFalse(base.headers)

    def test___nonzero__false(self):
        base = self._makeOne()
        self.assertFalse(base)

    def test___nonzero__true_body(self):
        base = self._makeOne()
        base.body = 'body'
        self.assertTrue(base)
        
    def test___nonzero__true_headers(self):
        base = self._makeOne([('Content-Type', 'text/html')])
        self.assertTrue(base)
        
    def test___nonzero__true_parts(self):
        base = self._makeOne()
        base.parts = [True]
        self.assertTrue(base)

    def test_keys(self):
        base = self._makeOne([('Content-Type', 'text/html'),
                              ('Content-Disposition', 'inline')])
        self.assertEqual(base.keys(), ['Content-Disposition', 'Content-Type'])

    def test_attach_file(self):
        base = self._makeOne()
        base.attach_file('filename', 'data', 'ctype', 'inline')
        self.assertEqual(len(base.parts), 1)
        part = base.parts[0]
        self.assertEqual(part.content_encoding['Content-Type'],
                         ('ctype', {'name':'filename'}))
        self.assertEqual(part.content_encoding['Content-Disposition'],
                         ('inline', {'filename':'filename'}))
        self.assertEqual(part.body, 'data')

    def test_attach_text(self):
        base = self._makeOne()
        base.attach_text('data', 'ctype')
        self.assertEqual(len(base.parts), 1)
        part = base.parts[0]
        self.assertEqual(part.content_encoding['Content-Type'], ('ctype', {}))
        self.assertEqual(part.body, 'data')

    def test_walk(self):
        base1 = self._makeOne()
        base2 = self._makeOne()
        base3 = self._makeOne()
        base1.parts = [base2]
        base2.parts = [base3]
        self.assertEqual(list(base1.walk()), [base2, base3])

class TestMailResponse(unittest.TestCase):
    def _makeOne(self, **kw):
        from pyramid_mailer.response import MailResponse
        return MailResponse(**kw)

    def test_ctor(self):
        response = self._makeOne(To='To', From='From', Subject='Subject',
                                 Body='Body', Html='Html')
        self.assertEqual(response.Body, 'Body')
        self.assertEqual(response.Html, 'Html')
        self.assertEqual(response.base.headers['To'], 'To')
        self.assertEqual(response.base.headers['From'], 'From')
        self.assertEqual(response.base.headers['Subject'], 'Subject')
        self.assertEqual(response.multipart, 'Html')
        self.assertEqual(response.attachments, [])

    def test___contains__(self):
        response = self._makeOne(To='To')
        self.assertTrue('To' in response)
        
    def test___getitem__(self):
        response = self._makeOne(To='To')
        self.assertEqual(response['To'], 'To')
        
    def test___setitem__(self):
        response = self._makeOne(To='To')
        response['To'] = 'To2'
        self.assertEqual(response.base['To'], 'To2')

    def test___delitem__(self):
        response = self._makeOne(To='To')
        del response['To']
        self.assertFalse('To' in response.base)

    def test_attach(self):
        import os
        this = os.path.abspath(__file__)
        response = self._makeOne()
        response.attach(filename=this, content_type='content_type',
                        data='data', disposition='disposition')
        self.assertEqual(len(response.attachments), 1)
        attachment = response.attachments[0]
        self.assertEqual(attachment['filename'], this)
        self.assertEqual(attachment['content_type'], 'content_type')
        self.assertEqual(attachment['data'], 'data')
        self.assertEqual(attachment['disposition'], 'disposition') 

    def test_attach_no_content_type(self):
        import os
        this = os.path.abspath(__file__)
        response = self._makeOne()
        response.attach(filename=this, data='data', disposition='disposition')
        self.assertEqual(len(response.attachments), 1)
        attachment = response.attachments[0]
        self.assertEqual(attachment['filename'], this)
        self.assertTrue('python' in attachment['content_type'])
        self.assertEqual(attachment['data'], 'data')
        self.assertEqual(attachment['disposition'], 'disposition') 

    def test_attach_part(self):
        response = self._makeOne()
        response.attach_part('part')
        self.assertEqual(len(response.attachments), 1)
        attachment = response.attachments[0]
        self.assertEqual(attachment['filename'], None)
        self.assertEqual(attachment['content_type'], None)
        self.assertEqual(attachment['data'], None)
        self.assertEqual(attachment['disposition'], None)
        self.assertEqual(attachment['part'], 'part')

    def test_attach_all_parts(self):
        response = self._makeOne()
        request = DummyMailRequest()
        response.attach_all_parts(request)
        self.assertEqual(len(response.attachments), 1)
        attachment = response.attachments[0]
        self.assertEqual(attachment['part'], request)
        self.assertEqual(response.base.content_encoding, {})

    def test_clear(self):
        response = self._makeOne()
        response.attachments = [True]
        response.base.parts = [True]
        response.clear()
        self.assertEqual(response.attachments, [])
        self.assertEqual(response.base.parts, [])
        self.assertEqual(response.multipart, False)

    def test_update(self):
        response = self._makeOne()
        response.update({'a':'1'})
        self.assertEqual(response.base['a'], '1')

    def test___str__(self):
        response = self._makeOne(To='To', From='From', Subject='Subject',
                                 Body='Body', Html='Html')
        s = str(response)
        self.assertTrue('Content-Type' in s)

    def test_to_message(self):
        from pyramid_mailer.response import MIMEPart
        response = self._makeOne(To='To', From='From', Subject='Subject',
                                 Body='Body', Html='Html')
        message = response.to_message()
        self.assertEqual(message.__class__, MIMEPart)

    def test_to_message_multiple_to_recipients(self):
        response = self._makeOne(
            To=['chrism@plope.com', 'billg@microsoft.com'],
            From='From', Subject='Subject',
            Body='Body', Html='Html')
        message = response.to_message()
        self.assertEqual(message['To'], 'chrism@plope.com, billg@microsoft.com')

    def test_to_message_multipart(self):
        from pyramid_mailer.response import MIMEPart
        response = self._makeOne(To='To', From='From', Subject='Subject',
                                 Body='Body', Html='Html')
        import os
        this = os.path.abspath(__file__)
        response = self._makeOne()
        response.attach(filename=this, content_type='text/html',
                        data='data', disposition='disposition')
        message = response.to_message()
        self.assertEqual(message.__class__, MIMEPart)

    def test_to_message_with_parts(self):
        from pyramid_mailer.response import MIMEPart
        part = DummyPart()
        response = self._makeOne(To='To', From='From', Subject='Subject')
        response.multipart = True
        response.attachments = [{'part':part}]
        message = response.to_message()
        self.assertEqual(message.__class__, MIMEPart)

    def test_to_message_with_parts2(self):
        this = os.path.join(here, 'tests.py')
        from pyramid_mailer.response import MIMEPart
        response = self._makeOne(To='To', From='From', Subject='Subject')
        response.multipart = True
        response.attachments = [{'filename':this, 'content_type':'text/python'}]
        message = response.to_message()
        self.assertEqual(message.__class__, MIMEPart)

    def test_to_message_with_parts3(self):
        from pyramid_mailer.response import MIMEPart
        response = self._makeOne(To='To', From='From', Subject='Subject')
        response.multipart = True
        response.attachments = [{'data':'data', 'content_type':'text/html'}]
        message = response.to_message()
        self.assertEqual(message.__class__, MIMEPart)

    def test_to_message_with_parts4(self):
        from pyramid_mailer.response import MIMEPart
        response = self._makeOne(To='To', From='From', Subject='Subject')
        response.multipart = True
        response.base.content_encoding['Content-Type'] = ('text/html', None)
        response.attachments = [{'data':'data', 'content_type':'text/html'}]
        message = response.to_message()
        self.assertEqual(message.__class__, MIMEPart)

    def test_to_message_with_parts5(self):
        from pyramid_mailer.response import MIMEPart
        response = self._makeOne(To='To', From='From', Subject='Subject')
        response.multipart = True
        data = os.urandom(100)
        response.attachments = [{'data': data,
                                 'content_type':'application/octet-stream'}]
        message = response.to_message()
        self.assertEqual(message.__class__, MIMEPart)

    def test_all_parts(self):
        response = self._makeOne()
        self.assertEqual(response.all_parts(), [])
        
    def test_keys(self):
        response = self._makeOne()
        self.assertEqual(response.keys(), ['From', 'Subject', 'To'])

class Test_to_message(unittest.TestCase):
    def _callFUT(self, mail):
        from pyramid_mailer.response import to_message
        return to_message(mail)

    def _makeBase(self, items=()):
        from pyramid_mailer.response import MailBase
        return MailBase(items)

    def test_no_ctype(self):
        from pyramid_mailer.response import MIMEPart
        mail = self._makeBase()
        result = self._callFUT(mail)
        self.assertEqual(result.__class__, MIMEPart)

    def test_no_ctype_no_parts(self):
        from pyramid_mailer.response import MIMEPart
        mail = self._makeBase()
        mail.parts = []
        result = self._callFUT(mail)
        self.assertEqual(result.__class__, MIMEPart)

class TestMIMEPart(unittest.TestCase):
    def _makeOne(self, type, **params):
        from pyramid_mailer.response import MIMEPart
        return MIMEPart(type, **params)

    def test_add_text_string(self):
        part = self._makeOne('text/html')
        part.add_text('a')
        self.assertEqual(part.get_payload(), 'a')

    def test_add_text_unicode(self):
        part = self._makeOne('text/html')
        la = unicode('LaPe\xc3\xb1a', 'utf-8')
        part.add_text(la)
        self.assertEqual(part.get_payload(), 'TGFQZcOxYQ==\n')

    def test_extract_payload(self):
        mail = DummyPart()
        mail.content_encoding['Content-Type'] = ('application/json', {})
        part = self._makeOne('application/json')
        part.extract_payload(mail)
        self.assertEqual(part.get_payload(), 'Ym9keQ==')

    def test___repr__(self):
        part = self._makeOne('text/html')
        result = repr(part)
        self.assertEqual(
            result,
            "<MIMEPart 'html/text': 'text/html', None, multipart=False>")

class Test_header_to_mime_encoding(unittest.TestCase):
    def _callFUT(self, value, not_email=False):
        from pyramid_mailer.response import header_to_mime_encoding
        return header_to_mime_encoding(value, not_email=not_email)

    def test_empty_value(self):
        result = self._callFUT('')
        self.assertEqual(result, '')

    def test_list_value(self):
        L = ['chrism@plope.com', 'billg@microsoft.com']
        result = self._callFUT(L)
        self.assertEqual(result, 'chrism@plope.com, billg@microsoft.com')

    def test_nonempty_nonlist_value(self):
        val = 'chrism@plope.com'
        result = self._callFUT(val)
        self.assertEqual(result, 'chrism@plope.com')

class Test_properly_encode_header(unittest.TestCase):
    def _callFUT(self, value, encoder, not_email):
        from pyramid_mailer.response import properly_encode_header
        return properly_encode_header(value, encoder, not_email)

    def test_ascii_encodable(self):
        result = self._callFUT('a', None, None)
        self.assertEqual(result, 'a')

    def test_not_ascii_encodable_email(self):
        la = unicode('LaPe\xc3\xb1a@plope.com', 'utf-8')
        class Encoder(object):
            def header_encode(self, val):
                return 'encoded'
        encoder = Encoder()
        result = self._callFUT(la, encoder, False)
        self.assertEqual(result,  u'"encoded" <LaPe\xf1a@plope.com>')

    def test_not_ascii_encodable(self):
        la = unicode('LaPe\xc3\xb1a', 'utf-8')
        class Encoder(object):
            def header_encode(self, val):
                return 'encoded'
        encoder = Encoder()
        result = self._callFUT(la, encoder, False)
        self.assertEqual(result,  'encoded')

class Dummy(object):
    pass

class DummyMailRequest(object):
    def __init__(self):
        self.base = Dummy()
        self.base.content_encoding = {}

    def all_parts(self):
        return [self]

class DummyPart(object):
    def __init__(self):
        self.content_encoding = {'Content-Type':('text/html', {}),
                                 'Content-Disposition':('inline', {})}
        self.parts = []
        self.body = 'body'

    def keys(self):
        return []
        

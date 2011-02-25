# -*- coding: utf-8 -*-


import unittest

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

    def test_bcc(self):

        from pyramid_mailer.message import Message

        msg = Message(subject="testing",
                      recipients=["to@example.com"],
                      body="testing",
                      bcc=["tosomeoneelse@example.com"])

        response = msg.get_response()
        self.assert_("Bcc: tosomeoneelse@example.com" in str(response))

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

    def dummy_test_send_immediately(self):

        from pyramid_mailer.mailer import DummyMailer
        from pyramid_mailer.message import Message

        mailer = DummyMailer()

        msg = Message(subject="testing",
                      sender="sender@example.com",
                      recipients=["tester@example.com"],
                      body="test")

        mailer.send_immediately(msg)

        self.assert_(len(mailer.outbox)) == 1
 

    def dummy_test_send_immediately_and_fail_silently(self):

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

        mailer = Mailer()

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
        except ImportError:
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

        else:
            self.assert_(mailer.direct_delivery.mailer.smtp == SMTP)
            self.assert_(mailer.direct_delivery.mailer.smtp_factory())

                          
    def test_from_settings_factory(self):

        try:
            from smtplib import SMTP_SSL
            ssl_enabled = True
        except ImportError:
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
        else:
            self.assert_(mailer.direct_delivery.mailer.smtp == SMTP)

        self.assert_(mailer.direct_delivery.mailer.keyfile == 'ssl.key')
        self.assert_(mailer.direct_delivery.mailer.certfile == 'ssl.crt')
        self.assert_(mailer.queue_delivery.queuePath == '/tmp')
        self.assert_(mailer.direct_delivery.mailer.debug_smtp == 1)


    def test_from_settings(self):
        
        try:
            from smtplib import SMTP_SSL
            ssl_enabled = True
        except ImportError:
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
        else:
            self.assert_(mailer.direct_delivery.mailer.smtp == SMTP)

        self.assert_(mailer.direct_delivery.mailer.keyfile == 'ssl.key')
        self.assert_(mailer.direct_delivery.mailer.certfile == 'ssl.crt')
        self.assert_(mailer.queue_delivery.queuePath == '/tmp')
        self.assert_(mailer.direct_delivery.mailer.debug_smtp == 1)


# -*- coding: utf-8 -*-


import transaction
import unittest
import mailbox

from email import encoders


class TestMessage(unittest.TestCase):

    def test_initialize(self):

        from pyramid_mailer import Message

        msg = Message(subject="subject",
                      sender="support@mysite.com",
                      recipients=["to@example.com"])


        assert msg.subject == "subject"
        assert msg.sender == "support@mysite.com"
        assert msg.recipients == ["to@example.com"]

    def test_recipients_properly_initialized(self):

        from pyramid_mailer import Message

        msg = Message(subject="subject")

        assert msg.recipients == []

        msg2 = Message(subject="subject")
        msg2.add_recipient("somebody@here.com")

        assert len(msg.recipients) == 0

        msg3 = Message(subject="subject")
        msg3.add_recipient("somebody@here.com")

        assert len(msg.recipients) == 0

    def test_add_recipient(self):

        from pyramid_mailer import Message

        msg = Message("testing")
        msg.add_recipient("to@example.com")

        assert msg.recipients == ["to@example.com"]

    
    def test_sender_as_tuple(self):

        from pyramid_mailer import Message

        msg = Message(subject="testing",
                      sender=("tester", "tester@example.com"))

    
    def test_send_without_sender(self):

        from pyramid_mailer import Message
        from pyramid_mailer import Mailer

        msg = Message(subject="testing",
                      recipients=["to@example.com"],
                      body="testing")

        mailer = Mailer()

        transaction.begin()
        self.assertRaises(AssertionError, mailer.send, msg)
        transaction.commit()

    def test_send_without_recipients(self):

        from pyramid_mailer import Message
        from pyramid_mailer import Mailer

        msg = Message(subject="testing",
                      recipients=[],
                      body="testing")

        self.assertRaises(AssertionError, mailer.send, msg)

    def test_send_without_body(self):

        from pyramid_mailer import Message
        from pyramid_mailer import Mailer

        msg = Message(subject="testing",
                      recipients=["to@example.com"])

        mailer = Mailer()

        self.assertRaises(AssertionError, mailer.send, msg)

        msg.html = "<b>test</b>"

        mailer.send(msg)

    def test_bcc(self):

        from pyramid_mailer import Message

        msg = Message(subject="testing",
                      recipients=["to@example.com"],
                      body="testing",
                      bcc=["tosomeoneelse@example.com"])

        response = msg.get_response()
        assert "Bcc: tosomeoneelse@example.com" in str(response)

    def test_cc(self):

        from pyramid_mailer import Message

        msg = Message(subject="testing",
                      recipients=["to@example.com"],
                      body="testing",
                      cc=["tosomeoneelse@example.com"])

        response = msg.get_response()
        assert "Cc: tosomeoneelse@example.com" in str(response)

    def test_attach(self):

        from pyramid_mailer import Message

        msg = Message(subject="testing",
                      recipients=["to@example.com"],
                      body="testing")
        
        msg.attach(data="this is a test", 
                   content_type="text/plain")
        

        a = msg.attachments[0]
        
        assert a.filename is None
        assert a.disposition == 'attachment'
        assert a.content_type == "text/plain"
        assert a.data == "this is a test"
 

    def test_bad_header_subject(self):

        from pyramid_mailer import Message
        from pyramid_mailer import Mailer

        msg = Message(subject="testing\n\r",
                      sender="from@example.com",
                      body="testing",
                      recipients=["to@example.com"])

        mailer = Mailer()

        self.assertRaises(BadHeaderError, mailer.send, msg)

    def test_bad_header_sender(self):

        from pyramid_mailer import Message
        from pyramid_mailer import Mailer

        mailer = Mailer()

        msg = Message(subject="testing",
                      sender="from@example.com\n\r",
                      recipients=["to@example.com"],
                      body="testing")

        self.assertRaises(BadHeaderError, mailer.send, msg)

    def test_bad_header_recipient(self):

        from pyramid_mailer import Message
        from pyramid_mailer import Mailer

        mailer = Mailer()

        msg = Message(subject="testing",
                      sender="from@example.com",
                      recipients=[
                          "to@example.com",
                          "to\r\n@example.com"],
                      body="testing")

        self.assertRaises(BadHeaderError, mailer.send, msg)


class TestMail(unittest.TestCase):

    def test_send(self):

        from pyramid_mailer import Mailer
        from pyramid_mailer import Message

        mailer = Mailer()

        msg = Message(subject="testing",
                      recipients=["tester@example.com"],
                      body="test")

        mailer.send(msg)

        assert len(outbox) == 1 

    def test_send_to_queue(self):

        from pyramid_mailer import Mailer

        mailer = Mailer()

        mailer.send_message(subject="testing",
                            recipients=["tester@example.com"],
                            body="test")

        assert len(outbox) == 1

        msg = outbox[0]

        assert msg.subject == "testing"
        assert msg.recipients == ["tester@example.com"]
        assert msg.body == "test"




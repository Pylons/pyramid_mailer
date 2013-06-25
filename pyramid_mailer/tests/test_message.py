# -*- coding: utf-8 -*-

import unittest
import os

from pyramid_mailer._compat import (
    text_type,
    StringIO,
    )

class TestAttachment(unittest.TestCase):

    def test_data_from_string(self):

        from pyramid_mailer.message import Attachment

        a = Attachment(data="foo")
        self.assertEqual(a.data, "foo")

    def test_data_from_file_obj(self):

        from pyramid_mailer.message import Attachment

        a = Attachment(data=StringIO(text_type("foo")))
        self.assertEqual(a.data, "foo")


class TestMessage(unittest.TestCase):

    def test_initialize(self):

        from pyramid_mailer.message import Message

        msg = Message(subject="subject",
                      sender="support@mysite.com",
                      recipients=["to@example.com"])

        self.assertEqual(msg.subject, "subject")
        self.assertEqual(msg.sender, "support@mysite.com")
        self.assertEqual(msg.recipients, ["to@example.com"])

    def test_recipients_properly_initialized(self):

        from pyramid_mailer.message import Message

        msg = Message(subject="subject")

        self.assertEqual(msg.recipients, [])

        msg2 = Message(subject="subject")
        msg2.add_recipient("somebody@here.com")

        self.assertEqual(len(msg.recipients), 0)

        msg3 = Message(subject="subject")
        msg3.add_recipient("somebody@here.com")

        self.assertEqual(len(msg.recipients), 0)

    def test_add_recipient(self):

        from pyramid_mailer.message import Message

        msg = Message("testing")
        msg.add_recipient("to@example.com")

        self.assertEqual(msg.recipients, ["to@example.com"])

    def test_add_cc(self):

        from pyramid_mailer.message import Message

        msg = Message("testing")
        msg.add_cc("to@example.com")

        self.assertEqual(msg.cc, ["to@example.com"])

    def test_add_bcc(self):

        from pyramid_mailer.message import Message

        msg = Message("testing")
        msg.add_bcc("to@example.com")

        self.assertEqual(msg.bcc, ["to@example.com"])

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
        self.assertTrue("Cc: tosomeoneelse@example.com" in text_type(response))

    def test_cc_without_recipients(self):

        from pyramid_mailer.message import Message
        from pyramid_mailer.mailer import Mailer

        msg = Message(subject="testing",
                      sender="sender@example.com",
                      body="testing",
                      cc=["tosomeoneelse@example.com"])
        mailer = Mailer()
        msgid = mailer.send(msg)
        response = msg.get_response()

        self.assertTrue("Cc: tosomeoneelse@example.com" in text_type(response))
        self.assertTrue(msgid)

    def test_cc_without_recipients_2(self):

        from pyramid_mailer.message import Message

        msg = Message(subject="testing",
                      sender="sender@example.com",
                      body="testing",
                      cc=["tosomeoneelse@example.com"])
        response = msg.get_response()
        self.assertTrue("Cc: tosomeoneelse@example.com" in text_type(response))

    def test_bcc_without_recipients(self):

        from pyramid_mailer.message import Message
        from pyramid_mailer.mailer import Mailer

        msg = Message(subject="testing",
                      sender="sender@example.com",
                      body="testing",
                      bcc=["tosomeoneelse@example.com"])
        mailer = Mailer()
        msgid = mailer.send(msg)
        response = msg.get_response()

        self.assertFalse(
            "Bcc: tosomeoneelse@example.com" in text_type(response))
        self.assertTrue(msgid)

    def test_attach(self):

        from pyramid_mailer.message import Message
        from pyramid_mailer.message import Attachment

        msg = Message(subject="testing",
                      recipients=["to@example.com"],
                      body="testing")

        msg.attach(Attachment(data="this is a test",
                              content_type="text/plain"))

        a = msg.attachments[0]

        self.assertTrue(a.filename is None)
        self.assertEqual(a.disposition, 'attachment')
        self.assertEqual(a.content_type, "text/plain")
        self.assertEqual(a.data, "this is a test")

        response = msg.get_response()

        self.assertEqual(len(response.attachments), 1)

    def test_attach_as_body_and_html_latin1(self):
        import codecs
        from pyramid_mailer.message import Message
        from pyramid_mailer.message import Attachment

        charset = 'iso-8859-1'
        text_encoded = b'LaPe\xf1a'
        text = text_encoded.decode(charset)
        text_html = '<p>' + text + '</p>'
        transfer_encoding = 'quoted-printable'
        body = Attachment(data=text,
                          transfer_encoding=transfer_encoding)
        html = Attachment(data=text_html,
                          transfer_encoding=transfer_encoding)
        msg = Message(subject="testing",
                      sender="from@example.com",
                      recipients=["to@example.com"],
                      body=body, html=html)
        message = msg.to_message()
        body_part, html_part = message.get_payload()

        # different repoze.sendmail versions use a different string to
        # represent the charset, so we permit either.
        self.assertTrue(
            body_part['Content-Type'] in 
                ('text/plain; charset="iso-8859-1"',
                 'text/plain; charset="latin_1"'),
                )
        self.assertEqual(
            body_part['Content-Transfer-Encoding'], transfer_encoding)
        encoder = codecs.getencoder('quopri_codec')
        payload = body_part.get_payload()
        encoded_text = text.encode(charset)
        expected = encoder(encoded_text)[0].decode('ascii')
        self.assertEqual(payload, expected)

        # different repoze.sendmail versions use a different string to
        # represent the charset, so we permit either.
        self.assertTrue(
            html_part['Content-Type'] in 
                ('text/html; charset="iso-8859-1"',
                 'text/html; charset="latin_1"'),
                )
        self.assertEqual(
            html_part['Content-Transfer-Encoding'], transfer_encoding)
        payload = html_part.get_payload()
        encoded_html = text_html.encode(charset)
        expected = encoder(encoded_html)[0].decode('ascii')
        self.assertEqual(payload, expected)

    def test_attach_as_body_and_html_utf8(self):
        import codecs
        from pyramid_mailer.message import Message
        from pyramid_mailer.message import Attachment

        charset = 'utf-8'
        # greek small letter iota with dialtyika and tonos; this character
        # cannot be encoded to either ascii or latin-1, so utf-8 is chosen
        text_encoded = b'\xce\x90'
        text = text_encoded.decode(charset)
        text_html = '<p>' + text + '</p>'
        transfer_encoding = 'quoted-printable'
        body = Attachment(data=text,
                          transfer_encoding=transfer_encoding)
        html = Attachment(data=text_html,
                          transfer_encoding=transfer_encoding)
        msg = Message(subject="testing",
                      sender="from@example.com",
                      recipients=["to@example.com"],
                      body=body, html=html)
        message = msg.to_message()
        body_part, html_part = message.get_payload()

        # different repoze.sendmail versions use a different string to
        # represent the charset, so we permit either.
        self.assertTrue(
            body_part['Content-Type'] in 
                ('text/plain; charset="utf-8"',
                 'text/plain; charset="utf_8"'),
                )
        self.assertEqual(
            body_part['Content-Transfer-Encoding'], transfer_encoding)
        encoder = codecs.getencoder('quopri_codec')
        payload = body_part.get_payload()
        encoded_text = text.encode(charset)
        expected = encoder(encoded_text)[0].decode('ascii')
        self.assertEqual(payload, expected)

        # different repoze.sendmail versions use a different string to
        # represent the charset, so we permit either.
        self.assertTrue(
            html_part['Content-Type'] in 
                ('text/html; charset="utf-8"',
                 'text/html; charset="utf_8"'),
                )
        self.assertEqual(
            html_part['Content-Transfer-Encoding'], transfer_encoding)
        payload = html_part.get_payload()
        encoded_html = text_html.encode(charset)
        expected = encoder(encoded_html)[0].decode('ascii')
        self.assertEqual(payload, expected)

    def test_attach_as_body(self):
        import codecs
        from pyramid_mailer.message import Message
        from pyramid_mailer.message import Attachment

        charset = 'iso-8859-1'
        text_encoded = b'LaPe\xf1a'
        text = text_encoded.decode(charset)
        transfer_encoding = 'quoted-printable'
        body = Attachment(data=text,
                          transfer_encoding=transfer_encoding)
        msg = Message(subject="testing",
                      sender="from@example.com",
                      recipients=["to@example.com"],
                      body=body)
        body_part = msg.to_message()

        # different repoze.sendmail versions use a different string to
        # represent the charset, so we permit either.
        self.assertTrue(
            body_part['Content-Type'] in 
                ('text/plain; charset="iso-8859-1"',
                 'text/plain; charset="latin_1"'),
                )
        self.assertEqual(
            body_part['Content-Transfer-Encoding'], transfer_encoding)
        self.assertEqual(body_part.get_payload(),
                         codecs.getencoder('quopri_codec')(
                             text.encode(charset))[0].decode('ascii'))

    def test_attach_as_html(self):
        import codecs
        from pyramid_mailer.message import Message
        from pyramid_mailer.message import Attachment

        charset = 'iso-8859-1'
        text_encoded = b'LaPe\xf1a'
        text = text_encoded.decode(charset)
        text_html = '<p>' + text + '</p>'
        transfer_encoding = 'quoted-printable'
        html = Attachment(data=text_html,
                          transfer_encoding=transfer_encoding)
        msg = Message(subject="testing",
                      sender="from@example.com",
                      recipients=["to@example.com"],
                      html=html)
        html_part = msg.to_message()

        # different repoze.sendmail versions use a different string to
        # represent the charset, so we permit either.
        self.assertTrue(
            html_part['Content-Type'] in 
                ('text/html; charset="iso-8859-1"',
                 'text/html; charset="latin_1"'),
                )
        self.assertEqual(
            html_part['Content-Transfer-Encoding'], transfer_encoding)
        self.assertEqual(html_part.get_payload(),
                         codecs.getencoder('quopri_codec')(
                             text_html.encode(charset))[0].decode('ascii'))

    def test_repoze_sendmail_send_to_queue_functional(self):
        # functest that emulates the interaction between pyramid_mailer and
        # repoze.maildir.add and queuedelivery.send.
        
        import codecs
        import tempfile
        from email.generator import Generator
        from email.parser import Parser
        from pyramid_mailer.message import Message
        from pyramid_mailer.message import Attachment
        from repoze.sendmail.encoding import cleanup_message
        from repoze.sendmail.delivery import copy_message

        def checkit(msg):
            self.assertTrue(
                msg['Content-Type'] in 
                    ('text/plain; charset="iso-8859-1"',
                     'text/plain; charset="latin_1"'),
                    )
            self.assertEqual(
                msg['Content-Transfer-Encoding'], transfer_encoding)

            payload = msg.get_payload()

            self.assertEqual(payload,
                             codecs.getencoder('quopri_codec')(
                                 text.encode(charset))[0].decode('ascii'))

        charset = 'iso-8859-1'
        text_encoded = b'LaPe\xf1a'
        text = text_encoded.decode(charset)
        transfer_encoding = 'quoted-printable'
        body = Attachment(
            data=text,
            transfer_encoding=transfer_encoding
            )
        msg = Message(
            subject="testing",
            sender="from@example.com",
            recipients=["to@example.com"],
            body=body
            )

        # done in pyramid_mailer via mailer/send_to_queue
        msg = msg.to_message()

        checkit(msg)

        # done in repoze.sendmail via delivery/AbstractMailDelivery/send
        cleanup_message(msg)

        checkit(msg)

        # done in repoze.sendmail via
        # delivery/AbstractMailDelivery/createDataManager
        msg_copy = copy_message(msg)

        checkit(msg_copy)

        try:
            # emulate what repoze.sendmail maildir.py/add does
            fn = tempfile.mktemp()
            fd = os.open(fn,
                         os.O_CREAT|os.O_EXCL|os.O_WRONLY,
                         0o600
                         )
            with os.fdopen(fd, 'w') as f:
                writer = Generator(f)
                writer.flatten(msg_copy)

            # emulate what repoze.sendmail.queue _parseMessage does
            with open(fn) as foo:
                parser = Parser()
                reconstituted = parser.parse(foo)
                checkit(reconstituted)
                
        finally: # pragma: no cover
            try:
                os.remove(fn)
            except:
                pass

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

        self.assertEqual(msg.send_to,
                         set(["to@example.com",
                              "somebodyelse@example.com",
                              "anotherperson@example.com"]))

    def test_is_bad_headers_if_no_bad_headers(self):
        from pyramid_mailer.message import Message
        msg = Message(subject="testing",
                      sender="from@example.com",
                      body="testing",
                      recipients=["to@example.com"])

        self.assertFalse(msg.is_bad_headers())

    def test_is_bad_headers_if_subject_empty(self):
        from pyramid_mailer.message import Message
        msg = Message(sender="from@example.com",
                      body="testing",
                      recipients=["to@example.com"])

        self.assertFalse((msg.is_bad_headers()))

    def test_is_bad_headers_if_bad_headers(self):

        from pyramid_mailer.message import Message
        msg = Message(subject="testing\n\r",
                      sender="from@\nexample.com",
                      body="testing",
                      recipients=["to@example.com"])

        self.assertTrue(msg.is_bad_headers())



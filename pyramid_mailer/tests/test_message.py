# -*- coding: utf-8 -*-

import unittest
import os

from pyramid_mailer._compat import (
    text_type,
    StringIO,
    _qencode,
    )

from email.encoders import (
    _bencode,
    )

class TestAttachment(unittest.TestCase):

    def _makeOne(self, **kw):
        from pyramid_mailer.message import Attachment
        return Attachment(**kw)

    def test_data_from_string(self):
        a = self._makeOne(data="foo")
        self.assertEqual(a.data, "foo")

    def test_data_from_file_obj(self):
        a = self._makeOne(data=StringIO(text_type("foo")))
        self.assertEqual(a.data, "foo")

    def test_to_mailbase_no_data(self):
        a = self._makeOne()
        self.assertRaises(RuntimeError, a.to_mailbase)

    def test_to_mailbase_content_type_derives_from_filename(self):
        a = self._makeOne(filename='foo.txt', data='bar')
        base = a.to_mailbase()
        self.assertEqual(
            base.get_content_type(),
            ('text/plain', {'name':'foo.txt', 'charset':'us-ascii'})
            )
        self.assertEqual(
            base.get_content_disposition(),
            ('attachment', {'filename':'foo.txt'})
            )

    def test_to_mailbase_content_type_cannot_be_derived_from_filename(self):
        a = self._makeOne(data='bar')
        self.assertRaises(RuntimeError, a.to_mailbase)
        
    def test_to_mailbase_disposition_header_provides_filename(self):
        a = self._makeOne(
            data='bar',
            disposition='attachment; filename="foo.txt"',
            content_type='text/plain',
            )
        base = a.to_mailbase()
        self.assertEqual(
            base.get_content_type(),
            ('text/plain', {'name':'foo.txt', 'charset':'us-ascii'})
            )
        self.assertEqual(
            base.get_content_disposition(),
            ('attachment', {'filename':'foo.txt'})
            )

    def test_to_mailbase_text_type_sets_charset_ascii(self):
        text = 'bar'
        a = self._makeOne(
            data=text,
            disposition='attachment',
            content_type='text/plain',
            )
        base = a.to_mailbase()
        self.assertEqual(
            base.get_content_type(),
            ('text/plain', {'charset':'us-ascii'})
            )
        self.assertEqual(base.get_body(), text)

    def test_to_mailbase_text_type_sets_charset_unicode_latin1(self):
        charset = 'iso-8859-1'
        text_encoded = b'LaPe\xf1a'
        text = text_encoded.decode(charset)
        a = self._makeOne(
            data=text,
            disposition='attachment',
            content_type='text/plain',
            )
        base = a.to_mailbase()
        self.assertEqual(
            base.get_content_type(),
            ('text/plain', {'charset':'iso-8859-1'})
            )
        self.assertEqual(base.get_body(), text)

    def test_to_mailbase_text_type_sets_charset_unicode_utf8(self):
        charset = 'utf-8'
        # greek small letter iota with dialtyika and tonos; this character
        # cannot be encoded to either ascii or latin-1, so utf-8 is chosen
        text_encoded = b'\xce\x90'
        text = text_encoded.decode(charset)
        a = self._makeOne(
            data=text,
            disposition='attachment',
            content_type='text/plain',
            )
        base = a.to_mailbase()
        self.assertEqual(
            base.get_content_type(),
            ('text/plain', {'charset':'utf-8'})
            )
        self.assertEqual(base.get_body(), text)

    def test_to_mailbase_disposition_set(self):
        a = self._makeOne(
            data='abc',
            disposition='foo',
            content_type='text/plain',
            )
        base = a.to_mailbase()
        self.assertEqual(
            base.get_content_disposition(),
            ('foo', {})
            )

    def test_to_mailbase_content_id_set(self):
        a = self._makeOne(
            data='abc',
            content_type='text/plain',
            content_id='foo-content',
            )
        base = a.to_mailbase()
        self.assertEqual(
            base['content-id'],
            'foo-content'
            )
        
class TestMessage(unittest.TestCase):

    def _read_filedata(self, filename, mode='r'):
        f = open(filename, mode)
        try:
            data = f.read()
        finally:
            f.close()
        return data
    
    def test_initialize(self):

        from pyramid_mailer.message import Message

        msg = Message(
            subject="subject",
            sender="support@mysite.com",
            recipients=["to@example.com"]
            )

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

        msg = Message(
            subject="testing",
            recipients=["to@example.com"],
            body="testing"
            )

        mailer = Mailer()

        self.assertRaises(InvalidMessage, mailer.send, msg)

    def test_send_without_recipients(self):

        from pyramid_mailer.message import Message
        from pyramid_mailer.mailer import Mailer
        from pyramid_mailer.exceptions import InvalidMessage

        mailer = Mailer()

        msg = Message(
            subject="testing",
            recipients=[],
            body="testing"
            )

        self.assertRaises(InvalidMessage, mailer.send, msg)

    def test_send_without_body(self):

        from pyramid_mailer.message import Message
        from pyramid_mailer.mailer import Mailer
        from pyramid_mailer.exceptions import InvalidMessage

        msg = Message(
            subject="testing",
            sender="sender@example.com",
            recipients=["to@example.com"]
            )

        mailer = Mailer()

        self.assertRaises(InvalidMessage, mailer.send, msg)

        msg.html = "<b>test</b>"

        mailer.send(msg)

    def test_cc(self):

        from pyramid_mailer.message import Message

        msg = Message(
            subject="testing",
            sender="sender@example.com",
            recipients=["to@example.com"],
            body="testing",
            cc=["tosomeoneelse@example.com"]
            )

        response = msg.to_message()
        self.assertTrue("Cc: tosomeoneelse@example.com" in text_type(response))

    def test_cc_without_recipients(self):

        from pyramid_mailer.message import Message
        from pyramid_mailer.mailer import Mailer

        msg = Message(
            subject="testing",
            sender="sender@example.com",
            body="testing",
            cc=["tosomeoneelse@example.com"]
            )
        mailer = Mailer()
        msgid = mailer.send(msg)
        response = msg.to_message()

        self.assertTrue("Cc: tosomeoneelse@example.com" in text_type(response))
        self.assertTrue(msgid)

    def test_cc_without_recipients_2(self):

        from pyramid_mailer.message import Message

        msg = Message(
            subject="testing",
            sender="sender@example.com",
            body="testing",
            cc=["tosomeoneelse@example.com"]
            )
        response = msg.to_message()
        self.assertTrue("Cc: tosomeoneelse@example.com" in text_type(response))

    def test_bcc_without_recipients(self):

        from pyramid_mailer.message import Message
        from pyramid_mailer.mailer import Mailer

        msg = Message(
            subject="testing",
            sender="sender@example.com",
            body="testing",
            bcc=["tosomeoneelse@example.com"]
            )
        mailer = Mailer()
        msgid = mailer.send(msg)
        response = msg.to_message()

        self.assertFalse(
            "Bcc: tosomeoneelse@example.com" in text_type(response))
        self.assertTrue(msgid)

    def test_extra_headers(self):

        from pyramid_mailer.message import Message

        msg = Message(
            subject="testing",
            sender="sender@example.com",
            recipients=["to@example.com"],
            body="testing",
            extra_headers=[('X-Foo', 'Joe')]
            )

        response = msg.to_message()
        self.assertTrue("X-Foo: Joe" in text_type(response))

    def test_attach(self):

        from pyramid_mailer.message import Message
        from pyramid_mailer.message import Attachment

        msg = Message(
            subject="testing",
            recipients=["to@example.com"],
            sender='sender',
            body="testing"
            )

        attachment = Attachment(
            data=b"this is a test",
            content_type="text/plain"
            )

        msg.attach(attachment)

        a = msg.attachments[0]

        self.assertTrue(a.filename is None)
        self.assertEqual(a.disposition, 'attachment')
        self.assertEqual(a.content_type, "text/plain")
        self.assertEqual(a.data, b"this is a test")

    def test_attach_as_body_and_html_latin1(self):
        from pyramid_mailer.message import Message
        from pyramid_mailer.message import Attachment

        charset = 'iso-8859-1'
        text_encoded = b'LaPe\xf1a'
        text = text_encoded.decode(charset)
        html_encoded = b'<p>' + text_encoded + b'</p>'
        html_text = html_encoded.decode(charset)
        transfer_encoding = 'quoted-printable'
        body = Attachment(
            data=text,
            transfer_encoding=transfer_encoding
            )
        html = Attachment(
            data=html_text,
            transfer_encoding=transfer_encoding
            )
        msg = Message(
            subject="testing",
            sender="from@example.com",
            recipients=["to@example.com"],
            body=body,
            html=html,
            )
        message = msg.to_message()
        body_part, html_part = message.get_payload()

        self.assertEqual(
            body_part['Content-Type'],
            'text/plain; charset="iso-8859-1"'
            )
        self.assertEqual(
            body_part['Content-Transfer-Encoding'],
            transfer_encoding
            )
        payload = body_part.get_payload()
        self.assertEqual(
            payload,
            _qencode(text_encoded).decode('ascii')
            )

        self.assertEqual(
            html_part['Content-Type'], 
            'text/html; charset="iso-8859-1"'
            )
        self.assertEqual(
            html_part['Content-Transfer-Encoding'],
            transfer_encoding
            )
        payload = html_part.get_payload()
        self.assertEqual(
            payload,
            _qencode(html_encoded).decode('ascii')
            )

    def test_attach_as_body_and_html_utf8(self):
        from pyramid_mailer.message import Message
        from pyramid_mailer.message import Attachment

        charset = 'utf-8'
        # greek small letter iota with dialtyika and tonos; this character
        # cannot be encoded to either ascii or latin-1, so utf-8 is chosen
        text_encoded =  b'\xce\x90'
        text = text_encoded.decode(charset)
        html_encoded = b'<p>' + text_encoded + b'</p>'
        html_text = html_encoded.decode(charset)
        transfer_encoding = 'quoted-printable'
        body = Attachment(
            data=text,
            transfer_encoding=transfer_encoding,
            )
        html = Attachment(
            data=html_text,
            transfer_encoding=transfer_encoding,
            )
        msg = Message(
            subject="testing",
            sender="from@example.com",
            recipients=["to@example.com"],
            body=body,
            html=html,
            )
        message = msg.to_message()
        body_part, html_part = message.get_payload()

        self.assertEqual(
            body_part['Content-Type'],
            'text/plain; charset="utf-8"'
            )
        
        self.assertEqual(
            body_part['Content-Transfer-Encoding'],
            transfer_encoding
            )

        payload = body_part.get_payload()
        self.assertEqual(
            payload,
            _qencode(text_encoded).decode('ascii')
            )

        self.assertEqual(
            html_part['Content-Type'],
            'text/html; charset="utf-8"'
            )
        self.assertEqual(
            html_part['Content-Transfer-Encoding'],
            transfer_encoding
            )
        payload = html_part.get_payload()
        self.assertEqual(
            payload,
            _qencode(html_encoded).decode('ascii')
            )

    def test_attach_as_body(self):
        from pyramid_mailer.message import Message
        from pyramid_mailer.message import Attachment

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
        body_part = msg.to_message()

        self.assertEqual(
            body_part['Content-Type'],
            'text/plain; charset="iso-8859-1"'
            )
        self.assertEqual(
            body_part['Content-Transfer-Encoding'],
            transfer_encoding
            )
        self.assertEqual(
            body_part.get_payload(),
            _qencode(text_encoded).decode('ascii')
            )

    def test_attach_as_html(self):
        from pyramid_mailer.message import Message
        from pyramid_mailer.message import Attachment

        charset = 'iso-8859-1'
        text_encoded = b'LaPe\xf1a'
        html_encoded = b'<p>' + text_encoded + b'</p>'
        html_text = html_encoded.decode(charset)
        transfer_encoding = 'quoted-printable'
        html = Attachment(
            data=html_text,
            transfer_encoding=transfer_encoding
            )
        msg = Message(
            subject="testing",
            sender="from@example.com",
            recipients=["to@example.com"],
            html=html,
            )

        html_part = msg.to_message()

        self.assertEqual(
            html_part['Content-Type'],
            'text/html; charset="iso-8859-1"'
            )
        self.assertEqual(
            html_part['Content-Transfer-Encoding'],
            transfer_encoding
            )
        self.assertEqual(
            html_part.get_payload(),
            _qencode(html_encoded).decode('ascii')
            )

    def test_bad_header_subject(self):

        from pyramid_mailer.message import Message
        from pyramid_mailer.mailer import Mailer

        from pyramid_mailer.exceptions import BadHeaders

        msg = Message(
            subject="testing\n\r",
            sender="from@example.com",
            body="testing",
            recipients=["to@example.com"]
            )

        mailer = Mailer()

        self.assertRaises(BadHeaders, mailer.send, msg)

    def test_bad_header_sender(self):

        from pyramid_mailer.message import Message
        from pyramid_mailer.mailer import Mailer

        from pyramid_mailer.exceptions import BadHeaders

        mailer = Mailer()

        msg = Message(
            subject="testing",
            sender="from@example.com\n\r",
            recipients=["to@example.com"],
            body="testing"
            )
        self.assertRaises(BadHeaders, mailer.send, msg)

    def test_bad_header_recipient(self):

        from pyramid_mailer.message import Message
        from pyramid_mailer.mailer import Mailer

        from pyramid_mailer.exceptions import BadHeaders

        mailer = Mailer()

        msg = Message(
            subject="testing",
            sender="from@example.com",
            recipients=[
                "to@example.com",
                "to\r\n@example.com"],
            body="testing"
            )

        self.assertRaises(BadHeaders, mailer.send, msg)

    def test_send_to(self):

        from pyramid_mailer.message import Message

        msg = Message(
            subject="testing",
            sender="from@example.com",
            recipients=[
                "to@example.com"],
            cc=['somebodyelse@example.com',
                'to@example.com'],
            bcc=['anotherperson@example.com'],
            body="testing"
            )
        
        self.assertEqual(
            msg.send_to,
            {"to@example.com",
             "somebodyelse@example.com",
             "anotherperson@example.com"}
            )
        
    def test_is_bad_headers_if_no_bad_headers(self):
        from pyramid_mailer.message import Message
        msg = Message(
            subject="testing",
            sender="from@example.com",
            body="testing",
            recipients=["to@example.com"]
            )

        self.assertFalse(msg.is_bad_headers())

    def test_is_bad_headers_if_subject_empty(self):
        from pyramid_mailer.message import Message
        msg = Message(
            sender="from@example.com",
            body="testing",
            recipients=["to@example.com"]
            )

        self.assertFalse((msg.is_bad_headers()))

    def test_is_bad_headers_if_bad_headers(self):

        from pyramid_mailer.message import Message
        msg = Message(
            subject="testing\n\r",
            sender="from@\nexample.com",
            body="testing",
            recipients=["to@example.com"]
            )

        self.assertTrue(msg.is_bad_headers())

    def test_to_message_multiple_to_recipients(self):
        from pyramid_mailer.message import Message
        response = Message(
            subject="Subject",
            sender="From",
            recipients=["chrism@plope.com", "billg@microsoft.com"],
            body="Body",
            html="Html",
            )
        message = response.to_message()
        self.assertEqual(text_type(message['To']),
                         'chrism@plope.com, billg@microsoft.com')

    def test_to_message_multipart(self):
        from pyramid_mailer.message import Message, Attachment
        response = Message(
            recipients=['To'],
            sender='From',
            subject='Subject',
            body='Body',
            html='Html'
            )
        attachment_type = 'text/html'
        this = os.path.abspath(__file__)
        attachment = Attachment(
            filename=this,
            content_type=attachment_type,
            data='data'.encode('ascii'),
            disposition='disposition'
            )
        response.attach(attachment)
        message = response.to_message()
        self.assertEqual(message['Content-Type'], 'multipart/mixed')

        payload = message.get_payload()
        self.assertEqual(len(payload), 2)
        self.assertEqual(
            payload[0]['Content-Type'],
            'multipart/alternative'
            )
        self.assertTrue(
            payload[1]['Content-Type'].startswith(attachment_type)
            )

        alt_payload = payload[0].get_payload()
        self.assertTrue(
            alt_payload[0]['Content-Type'].startswith('text/plain')
            )
        self.assertTrue(
            alt_payload[1]['Content-Type'].startswith('text/html')
            )

    def test_to_message_multipart_with_b64encoding(self):
        from pyramid_mailer.message import Message, Attachment
        
        response = Message(
            recipients=['To'],
            sender='From',
            subject='Subject',
            body='Body',
            html='Html'
            )

        this = os.path.abspath(__file__)
        with open(this, 'rb') as data:
            attachment = Attachment(
                filename=this,
                content_type='application/octet-stream',
                disposition='disposition',
                transfer_encoding='base64',
                data=data,
                )
            response.attach(attachment)
            message = response.to_message()
            payload = message.get_payload()[1]
        self.assertEqual(payload.get('Content-Transfer-Encoding'), 'base64')
        self.assertEqual(
            payload.get_payload(),
            _bencode(self._read_filedata(this, 'rb')).decode('ascii')
            )

    def test_to_message_multipart_with_qpencoding(self):
        from pyramid_mailer.message import Message, Attachment
        response = Message(
            recipients=['To'],
            sender='From',
            subject='Subject',
            body='Body',
            html='Html'
            )
        this = os.path.abspath(__file__)
        with open(this, 'rb') as data:
            attachment = Attachment(
                filename=this,
                content_type='application/octet-stream',
                disposition='disposition',
                transfer_encoding='quoted-printable',
                data=data,
                )
            response.attach(attachment)
            message = response.to_message()
            payload = message.get_payload()[1]
        self.assertEqual(
            payload.get('Content-Transfer-Encoding'),
            'quoted-printable'
            )
        self.assertEqual(
            payload.get_payload(),
            _qencode(self._read_filedata(this,'rb')).decode('ascii')
            )

    def test_to_message_with_html_attachment(self):
        from pyramid_mailer.message import Message, Attachment
        response = Message(
            recipients=['To'],
            sender='From',
            subject='Subject',
            body='Body',
            )
        attachment = Attachment(
            data=b'data',
            content_type='text/html'
            )
        response.attach(attachment)
        message = response.to_message()
        att_payload = message.get_payload()[1]
        self.assertEqual(
            att_payload['Content-Type'],
            'text/html; charset="us-ascii"'
            )
        self.assertEqual(
            att_payload.get_payload(),
            _bencode(b'data').decode('ascii')
            )

    def test_to_message_with_binary_attachment(self):
        from pyramid_mailer.message import Message, Attachment
        response = Message(
            recipients=['To'],
            sender='From',
            subject='Subject',
            body='Body',
            )
        data = os.urandom(100)
        attachment = Attachment(
            data=data,
            content_type='application/octet-stream',
            )
        response.attach(attachment)
        message = response.to_message()
        att_payload = message.get_payload()[1]
        self.assertEqual(
            att_payload['Content-Type'],
            'application/octet-stream'
            )
        self.assertEqual(
            att_payload.get_payload(),
            _bencode(data).decode('ascii')
            )

    def test_message_is_quoted_printable_with_text_body(self):
        from pyramid_mailer.message import Message

        msg = Message(
            recipients=['test@example.com'],
            subject="testing",
            sender="sender@example.com",
            body="THISSHOULDBEINMESSAGEBODY",
            )

        response = msg.to_message()
        self.assertTrue("THISSHOULDBEINMESSAGEBODY" in text_type(response))

class Test_normalize_header(unittest.TestCase):
    def _callFUT(self, header):
        from pyramid_mailer.message import normalize_header
        return normalize_header(header)

    def test_it(self):
        result = self._callFUT('content-type')
        self.assertEqual(result, 'Content-Type')

class TestMailBase(unittest.TestCase):
    def _makeOne(self, items=()):
        from pyramid_mailer.message import MailBase
        return MailBase(items)

    def test_set_content_type(self):
        base = self._makeOne()
        base.set_content_type('text/html')
        self.assertEqual(
            base.content_encoding['Content-Type'],
            ('text/html', {})
            )

    def test_set_content_type_with_params(self):
        base = self._makeOne()
        base.set_content_type('text/html', {'a':'b'})
        self.assertEqual(
            base.content_encoding['Content-Type'],
            ('text/html', {'a':'b'})
            )

    def test_get_content_type(self):
        base = self._makeOne()
        self.assertEqual(
            base.get_content_type(),
            (None, {})
            )

    def test_set_content_disposition(self):
        base = self._makeOne()
        base.set_content_disposition('inline')
        self.assertEqual(
            base.content_encoding['Content-Disposition'],
            ('inline', {})
            )

    def test_set_content_disposition_with_params(self):
        base = self._makeOne()
        base.set_content_disposition('inline', {'a':'b'})
        self.assertEqual(
            base.content_encoding['Content-Disposition'],
            ('inline', {'a':'b'})
            )

    def test_get_content_disposition(self):
        base = self._makeOne()
        self.assertEqual(
            base.get_content_disposition(),
            (None, {})
            )

    def test_set_transfer_encoding(self):
        base = self._makeOne()
        base.set_transfer_encoding('base64')
        self.assertEqual(
            base.content_encoding['Content-Transfer-Encoding'],
            'base64'
            )
       
    def test_get_transfer_encoding(self):
        base = self._makeOne()
        self.assertEqual(
            base.get_transfer_encoding(),
            None
            )

    def test_set_body(self):
        base = self._makeOne()
        base.set_body('foo')
        self.assertEqual(base.body, 'foo')

    def test_get_body(self):
        base = self._makeOne()
        base.body = 'foo'
        self.assertEqual(base.get_body(), 'foo')

    def test_merge_part(self):
        base = self._makeOne()
        another = self._makeOne()
        another.body = 'foo'
        another.content_encoding['foo'] = 'bar'
        another.headers = {'a':'b'}
        another.parts = [1]
        base.merge_part(another)
        self.assertEqual(base.body, 'foo')
        self.assertEqual(base.content_encoding['foo'], 'bar')
        self.assertEqual(base.headers['a'], 'b')
        self.assertEqual(base.parts, [1])

    def test_attach_part(self):
        base = self._makeOne()
        base.attach_part(1)
        self.assertEqual(base.parts, [1])
        
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

class Test_to_message(unittest.TestCase):
    def _callFUT(self, mail):
        from pyramid_mailer.message import to_message
        return to_message(mail)

    def _makeBase(self, items=()):
        from pyramid_mailer.message import MailBase
        return MailBase(items)

    def test_empty_header(self):
        mail = self._makeBase()
        mail['To'] = ''
        result = self._callFUT(mail)
        self.assertFalse('To' in result)

    def test_no_ctype(self):
        from email.mime.text import MIMENonMultipart
        mail = self._makeBase()
        result = self._callFUT(mail)
        self.assertEqual(result.__class__, MIMENonMultipart)

    def test_no_ctype_with_parts(self):
        mail = self._makeBase()
        another = self._makeBase()
        mail.parts = [another]
        result = self._callFUT(mail)
        self.assertEqual(result['Content-Type'], 'multipart/mixed')

    def test_no_ctype_without_parts(self):
        mail = self._makeBase()
        mail.set_body(b'')
        result = self._callFUT(mail)
        self.assertEqual(
            result['Content-Type'],
            'text/plain'
            )

    def test_ctype_doesnt_match_parts(self):
        mail = self._makeBase()
        mail.set_content_type('text/plain')
        another = self._makeBase()
        mail.parts = [another]
        self.assertRaises(RuntimeError, self._callFUT, mail)

    def test_body_is_text_ct_is_text_no_charset(self):
        mail = self._makeBase()
        mail.set_content_type('text/plain')
        mail.set_body(b'foo'.decode('ascii'))
        result = self._callFUT(mail)
        self.assertEqual(
            result['Content-Type'],
            'text/plain; charset="us-ascii"'
            )
        self.assertEqual(result['Content-Transfer-Encoding'], '7bit')
        payload = result.get_payload()
        self.assertEqual(payload, b'foo'.decode('ascii'))

    def test_body_is_text_ct_is_nontext_no_charset(self):
        mail = self._makeBase()
        mail.set_content_type('application/octet-stream')
        mail.set_body(b'foo'.decode('ascii'))
        # XXX note that if we dont set the transfer encoding, it will still
        # be encoded using bas64 but using a codec that doesnt strip the last
        # character on py27 (but not on py33).
        mail.set_transfer_encoding('base64')
        result = self._callFUT(mail)
        self.assertEqual(
            result['Content-Type'],
            'application/octet-stream; charset="utf-8"'
            )
        self.assertEqual(result['Content-Transfer-Encoding'], 'base64')
        payload = result.get_payload()
        self.assertEqual(payload, _bencode(b'foo').decode('ascii'))
        
    def test_recursion(self):
        mail = self._makeBase()
        another = self._makeBase()
        another.set_content_type('text/plain')
        another.set_body('hello')
        mail.parts = [another]
        result = self._callFUT(mail)
        self.assertTrue('hello' in result.as_string())
        
class Test_transfer_encode(unittest.TestCase):
    def _callFUT(self, encoding, payload):
        from pyramid_mailer.message import transfer_encode
        return transfer_encode(encoding, payload)

    def test_body_is_text_base64(self):
        from email.encoders import _bencode
        text_encoded = b'LaPe\xf1a'
        result = self._callFUT('base64', text_encoded)
        self.assertEqual(
            result,
            _bencode(text_encoded)
            )

    def test_body_is_text_quopri(self):
        text_encoded = b'LaPe\xf1a'
        result = self._callFUT('quoted-printable', text_encoded)
        self.assertEqual(
            result,
            _qencode(text_encoded)
            )

    def test_body_is_7bit(self):
        text_encoded = b'LaPe\xf1a'
        text_7bit = b'LaPena'
        self.assertEqual(
            self._callFUT('7bit', text_7bit),
            text_7bit
            )
        with self.assertRaises(RuntimeError):
            self._callFUT('7bit', text_encoded) 

    def test_body_is_8bit(self):
        text_encoded = b'LaPe\xf1a'
        self.assertEqual(
            self._callFUT('8bit', text_encoded),
            text_encoded
            )

    def test_unknown_encoding(self):
        text_encoded = b'LaPe\xf1a'
        self.assertRaises(
            RuntimeError,
            self._callFUT, 'bogus', text_encoded
            )
        
class TestFunctional(unittest.TestCase):
    def test_repoze_sendmail_send_to_queue_functional(self):
        # functest that emulates the interaction between pyramid_mailer and
        # repoze.maildir.add and queuedelivery.send.
        
        import tempfile
        from email.generator import Generator
        from email.parser import Parser
        from pyramid_mailer.message import Message
        from pyramid_mailer.message import Attachment
        from repoze.sendmail.encoding import cleanup_message
        from repoze.sendmail.delivery import copy_message

        def checkit(msg):
            self.assertEqual(
                msg['Content-Type'],
                'text/plain; charset="iso-8859-1"'
                )
            self.assertEqual(
                msg['Content-Transfer-Encoding'], transfer_encoding)

            payload = msg.get_payload()
            self.assertEqual(payload, expected)

        charset = 'iso-8859-1'
        text_encoded = b'LaPe\xf1a'
        text = text_encoded.decode(charset)
        expected = _qencode(text_encoded).decode('ascii')
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
        msg.as_string()

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


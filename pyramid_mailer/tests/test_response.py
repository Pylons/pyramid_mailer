import unittest
import os

from pyramid_mailer._compat import (
    text_type,
    PY2,
    )

here = os.path.dirname(os.path.abspath(__file__))

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
        base.attach_file('filename', b'data', 'ctype', 'inline', 'base64')
        self.assertEqual(len(base.parts), 1)
        part = base.parts[0]
        self.assertEqual(part.content_encoding['Content-Type'],
                         ('ctype', {'name': 'filename'}))
        self.assertEqual(part.content_encoding['Content-Disposition'],
                         ('inline', {'filename': 'filename'}))
        self.assertEqual(part.content_encoding['Content-Transfer-Encoding'],
                         'base64')
        self.assertEqual(part.body, b'data') # XXX should this differ on py3

    def test_attach_text(self):
        base = self._makeOne()
        base.attach_text('data', 'ctype')
        self.assertEqual(len(base.parts), 1)
        part = base.parts[0]
        self.assertEqual(part.content_encoding['Content-Type'], ('ctype', {}))
        if PY2:
            self.assertEqual(part.body, b'data')
        else: # pragma: no cover
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

    def _read_filedata(self, filename, mode='r'):
        f = open(filename, mode)
        try:
            data = f.read()
        finally:
            f.close()
        return data

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
                        data='data', disposition='disposition',
                        transfer_encoding='base64')
        self.assertEqual(len(response.attachments), 1)
        attachment = response.attachments[0]
        self.assertEqual(attachment['filename'], this)
        self.assertEqual(attachment['content_type'], 'content_type')
        self.assertEqual(attachment['data'], 'data')
        self.assertEqual(attachment['disposition'], 'disposition')
        self.assertEqual(attachment['transfer_encoding'], 'base64')

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
        self.assertEqual(attachment['transfer_encoding'], None)

    def test_attach_part(self):
        response = self._makeOne()
        response.attach_part('part')
        self.assertEqual(len(response.attachments), 1)
        attachment = response.attachments[0]
        self.assertEqual(attachment['filename'], None)
        self.assertEqual(attachment['content_type'], None)
        self.assertEqual(attachment['data'], None)
        self.assertEqual(attachment['disposition'], None)
        self.assertEqual(attachment['transfer_encoding'], None)
        self.assertEqual(attachment['part'], 'part')

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
        response.update({'a': '1'})
        self.assertEqual(response.base['a'], '1')

    def test___str__(self):
        response = self._makeOne(To='To', From='From', Subject='Subject',
                                 Body='Body', Html='Html')
        s = text_type(response)
        self.assertTrue('Content-Type' in s)

    def test_to_message(self):
        from pyramid_mailer.response import MIMEPart
        response = self._makeOne(To='To', From='From', Subject='Subject',
                                 Body='Body', Html='Html')
        message = response.to_message()
        self.assertEqual(message.__class__, MIMEPart)
        self.assertEqual(message['Content-Type'], 'multipart/alternative')

    def test_to_message_multiple_to_recipients(self):
        response = self._makeOne(
            To=['chrism@plope.com', 'billg@microsoft.com'],
            From='From', Subject='Subject',
            Body='Body', Html='Html')
        message = response.to_message()
        self.assertEqual(text_type(message['To']),
                         'chrism@plope.com, billg@microsoft.com')

    def test_to_message_multipart(self):
        from pyramid_mailer.response import MIMEPart
        response = self._makeOne(To='To', From='From', Subject='Subject',
                                 Body='Body', Html='Html')
        import os
        this = os.path.abspath(__file__)
        attachment_type = 'text/html'
        response.attach(filename=this, content_type=attachment_type,
                        data='data'.encode('ascii'), disposition='disposition')
        message = response.to_message()
        self.assertEqual(message.__class__, MIMEPart)
        self.assertEqual(message['Content-Type'], 'multipart/mixed')

        payload = message.get_payload()
        self.assertEqual(len(payload), 2)
        self.assertTrue(
            payload[0]['Content-Type'].startswith('multipart/alternative'))
        self.assertTrue(
            payload[1]['Content-Type'].startswith(attachment_type))

        alt_payload = payload[0].get_payload()
        self.assertTrue(
            alt_payload[0]['Content-Type'].startswith('text/plain'))
        self.assertTrue(
            alt_payload[1]['Content-Type'].startswith('text/html'))

    def test_to_message_multipart_with_b64encoding(self):
        from pyramid_mailer.response import MIMEPart
        response = self._makeOne(To='To', From='From', Subject='Subject',
                                 Body='Body', Html='Html')
        try:
            from base64 import encodebytes as base64_encodebytes
            # pyflakes
            base64_encodebytes  # pragma: no cover
        except ImportError:  # pragma: no cover
            # BBB Python 2 compat
            from base64 import encodestring as base64_encodebytes
        import os
        this = os.path.abspath(__file__)
        data = self._read_filedata(this, mode='rb')
        response = self._makeOne()
        response.attach(filename=this, content_type='text/plain',
                        disposition='disposition', transfer_encoding='base64')
        message = response.to_message()
        self.assertEqual(message.__class__, MIMEPart)
        payload = message.get_payload()[0]
        self.assertEqual(payload.get('Content-Transfer-Encoding'), 'base64')
        self.assertEqual(payload.get_payload(),
                         base64_encodebytes(data).decode('ascii'))

    def test_to_message_multipart_with_qpencoding(self):
        from pyramid_mailer.response import MIMEPart
        response = self._makeOne(To='To', From='From', Subject='Subject',
                                 Body='Body', Html='Html')
        import os
        import quopri
        this = os.path.abspath(__file__)
        data = self._read_filedata(this, mode='rb')
        response = self._makeOne()
        response.attach(filename=this, content_type='text/plain',
                        disposition='disposition',
                        transfer_encoding='quoted-printable')
        message = response.to_message()
        self.assertEqual(message.__class__, MIMEPart)
        payload = message.get_payload()[0]
        self.assertEqual(payload.get('Content-Transfer-Encoding'),
                         'quoted-printable')
        self.assertEqual(payload.get_payload(),
                         quopri.encodestring(data).decode('ascii'))

    def test_to_message_with_parts(self):
        from pyramid_mailer.response import MIMEPart
        part = DummyPart()
        response = self._makeOne(To='To', From='From', Subject='Subject')
        response.multipart = True
        response.attachments = [{'part':part}]
        message = response.to_message()
        self.assertEqual(message.__class__, MIMEPart)

    def test_to_message_with_parts2(self):
        this = os.path.join(here, 'test_response.py')
        from pyramid_mailer.response import MIMEPart
        response = self._makeOne(To='To', From='From', Subject='Subject')
        response.multipart = True
        response.attachments = [{'filename': this,
                                 'content_type': 'text/python'}]
        message = response.to_message()
        self.assertEqual(message.__class__, MIMEPart)

    def test_to_message_with_parts3(self):
        from pyramid_mailer.response import MIMEPart
        response = self._makeOne(To='To', From='From', Subject='Subject')
        response.multipart = True
        response.attachments = [{'data': b'data', 'content_type': 'text/html'}]
        message = response.to_message()
        self.assertEqual(message.__class__, MIMEPart)

    def test_to_message_with_parts4(self):
        from pyramid_mailer.response import MIMEPart
        response = self._makeOne(To='To', From='From', Subject='Subject')
        response.multipart = True
        response.base.content_encoding['Content-Type'] = ('text/html', None)
        response.attachments = [{'data': b'data', 'content_type': 'text/html'}]
        message = response.to_message()
        self.assertEqual(message.__class__, MIMEPart)

    def test_to_message_with_parts5(self):
        from pyramid_mailer.response import MIMEPart
        response = self._makeOne(To='To', From='From', Subject='Subject')
        response.multipart = True
        data = os.urandom(100)
        response.attachments = [{'data': data,
                                 'content_type': 'application/octet-stream'}]
        message = response.to_message()
        self.assertEqual(message.__class__, MIMEPart)

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

    def test_empty_header(self):
        mail = self._makeBase()
        mail['To'] = ''
        result = self._callFUT(mail)
        self.assertFalse('To' in result)


class TestMIMEPart(unittest.TestCase):
    def _makeOne(self, type, **params):
        from pyramid_mailer.response import MIMEPart
        return MIMEPart(type, **params)

    def test___repr__(self):
        part = self._makeOne('text/html')
        result = repr(part)
        self.assertEqual(
            result,
            "<MIMEPart 'html/text': 'text/html', None, multipart=False>")

    def test_extract_payload_text_type(self):
        part = self._makeOne('text/html')
        L = []
        part.set_payload = lambda body, charset=None: L.append((body, charset))
        mail = DummyPart('body')
        part.extract_payload(mail)
        self.assertEqual(L, [('body', None)])

    def test_extract_payload_non_text_type_no_cdisp(self):
        part = self._makeOne('text/html')
        L = []
        part.set_payload = lambda body, charset=None: L.append((body, charset))
        mail = DummyPart('body', 'application/octet-stream')
        part.extract_payload(mail)
        self.assertEqual(L, [('body', None)])

    def test_extract_payload_non_text_type_with_cdisp(self):
        part = self._makeOne('text/html')
        L = []
        part.set_payload = lambda body, charset=None: L.append((body, charset))
        part.add_header = lambda h, d, **x: L.append((h, d, x))
        mail = DummyPart('body', 'application/octet-stream', 'foo')
        part.extract_payload(mail)
        self.assertEqual(
            L,
            [('Content-Disposition', 'foo', {}), ('body', None)]
            )

    def test_extract_payload_with_charset(self):
        part = self._makeOne('text/html')
        L = []
        part.set_payload = lambda body, charset=None: L.append((body, charset))
        mail = DummyPart('body')
        mail.set_content_type('text/html', {'charset':'utf-8'})
        part.extract_payload(mail)
        self.assertEqual(L, [('body', 'utf-8')])

class Dummy(object):
    pass

class DummyMailRequest(object):
    def __init__(self):
        self.base = Dummy()
        self.base.content_encoding = {}

class DummyPart(object):
    def __init__(
        self,
        body='body',
        content_type='text/html',
        content_disposition='inline',
        transfer_encoding=None,
        ):
        self.content_encoding = {
            'Content-Type': (content_type, {}),
            'Content-Disposition': (content_disposition, {}),
            'Content-Transfer-Encoding': transfer_encoding,
            }
        self.parts = []
        self.body = body

    def keys(self):
        return []

    def get_body(self):
        return self.body

    def get_content_type(self):
        return self.content_encoding['Content-Type']

    def set_content_type(self, type, params=None):
        if params is None: # pragma: no cover
            params = {}
        self.content_encoding['Content-Type'] = (type, params)

    def get_content_disposition(self):
        return self.content_encoding['Content-Disposition']

    def get_transfer_encoding(self):
        return self.content_encoding['Content-Transfer-Encoding']


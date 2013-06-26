# The code in this module is partially lifted from the Lamson project
# (http://lamsonproject.org/).  Its copyright is:

# Copyright (c) 2008, Zed A. Shaw
# All rights reserved.

# It is provided under this license:

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.

# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.

# * Neither the name of the Zed A. Shaw nor the names of its contributors may
#   be used to endorse or promote products derived from this software without
#   specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import cgi
import mimetypes
import os
import string
import sys
import quopri

from email.mime.base import MIMEBase

from .exceptions import (
    BadHeaders,
    InvalidMessage,
    EncodingError,
    )

from ._compat import (
    base64_encodestring,
    is_nonstr_iter,
    text_type
    )


class Attachment(object):
    """
    Encapsulates file attachment information.

    :param filename: filename of attachment (if any)
    :param content_type: file mimetype (if any, may contain extra params in
           the form "text/plain; charset='utf-8'").
    :param data: the raw file data, either as text or a file object
    :param disposition: content-disposition (if any, may contain extra
           params in the form 'attachment; filename="fred.txt"').  If filename
           is supplied in the disposition, it will be used if no filename
           is supplied to the Attachment constructor.  If disposition is
           not supplied, it will default to 'attachment'.
    :param transfer_encoding: content-transfer-encoding (if any, may be
           'base64' or 'quoted-printable').  If it is not supplied, it will
           default to 'base64'.
    """

    def __init__(
        self,
        filename=None,
        content_type=None,
        data=None,
        disposition=None,
        transfer_encoding=None
        ):
        self.filename = filename
        self.content_type = content_type
        self.disposition = disposition or 'attachment'
        self.transfer_encoding = transfer_encoding or 'base64'
        self._data = data

    @property
    def data(self):
        if hasattr(self._data, 'read'):
            self._data = self._data.read()
        return self._data

    def to_mailbase(self, default_content_type=None, encode=False):
        filename = self.filename
        data = self.data
        content_type = self.content_type or default_content_type
        disposition = self.disposition or 'attachment'
        transfer_encoding = self.transfer_encoding or 'base64'
        
        assert filename or data, ("You must give a filename or some data to "
                                  "attach.")

        assert data or os.path.exists(filename), ("File doesn't exist, and no "
                                                  "data given.")

        if filename and not content_type:
            content_type, _ = mimetypes.guess_type(filename)

        assert content_type, ("No content type given, and couldn't guess "
                              "from the filename: %r" % filename)

        content_type, ctparams = parse_header(content_type)
        disposition, dparams = parse_header(disposition)
        
        if filename:
            tmp = {'name':filename}
            tmp.update(ctparams)
            ctparams = tmp
            tmp = {'filename':filename}
            tmp.update(dparams)
            dparams = tmp
            if not data:
                # should be opened with binary mode to encode the data later
                with open(filename, mode='rb') as f:
                    data = f.read()

        base = MailBase()
        base.set_content_type(content_type, ctparams)
        
        if not filename:
            if not isinstance(data, bytes):
                if encode:
                    charset = ctparams.pop('charset', None)
                    body_text = self.data
                    charset, data = charset_encode_body(charset, body_text)
                    if charset:
                        ctparams['charset'] = charset
                else:
                    raise EncodingError(
                        'Attachment data must be bytes if it is not a file: '
                        'got %s' % data
                        )

        base.set_body(data)
        base.set_content_type(content_type, ctparams)
        base.set_content_disposition(disposition, dparams)
        base.set_transfer_encoding(transfer_encoding)

        return base

class Message(object):
    """
    Encapsulates an email message.

    :param subject: email subject header
    :param recipients: list of email addresses
    :param body: plain text message (may be an Attachment or text)
    :param html: HTML message (may be an Attachment or text)
    :param sender: email sender address
    :param cc: CC list
    :param bcc: BCC list
    :param extra_headers: dict of extra email headers
    :param attachments: list of Attachment instances

    The message must have a body or html part (or both) to be successfully
    sent.
    """

    def __init__(
        self,
        subject=None,
        recipients=None,
        body=None,
        html=None,
        sender=None,
        cc=None,
        bcc=None,
        extra_headers=None,
        attachments=None
        ):
        
        self.subject = subject or ''
        self.sender = sender
        self.body = body
        self.html = html

        self.recipients = recipients or []
        self.attachments = attachments or []
        self.cc = cc or []
        self.bcc = bcc or []
        self.extra_headers = extra_headers or {}

    @property
    def send_to(self):
        return set(self.recipients) | set(self.bcc or ()) | set(self.cc or ())

    def to_message(self):
        """
        Returns raw email.Message instance.  Validates message first.
        """

        self.validate()
        
        bodies = [(self.body, 'text/plain'), (self.html, 'text/html')]

        for idx, (val, content_type) in enumerate(bodies):
            if val is None:
                bodies[idx] = None
            elif isinstance(val, Attachment):
                bodies[idx] = val.to_mailbase(content_type, encode=True)
            else:
                # presumed to be text
                attachment = Attachment(
                    data=val,
                    content_type=content_type,
                    disposition='inline'
                    )
                bodies[idx] = attachment.to_mailbase(content_type, encode=True)

        body, html = bodies

        base = MailBase([
            ('To', self.recipients),
            ('From', self.sender),
            ('Subject', self.subject),
            ])

        # base represents the outermost mime part; it will be one of the
        # following types:
        #
        # - a multipart/mixed type if there are attachments.  this
        #   part will contain a single multipart/alternative type if there
        #   is both an html part and a plaintext part (the alternative part
        #   will contain both the text and html), it will contain
        #   a single text/plain part if there is only a plaintext part,
        #   or it will contain a single text/html part if there is only
        #   an html part.  it will also contain N parts representing
        #   each attachment as children of the base mixed type.
        #
        # - a multipart/alternative type if there are no attachments but
        #   both an html part and a plaintext part.  it will contain
        #   a single text/plain part if there is only a plaintext part,
        #   or it will contain a single text/html part if there is only
        #   an html part.
        #
        # - a text/plain type if there is only a plaintext part
        #
        # - a text/html type if there is only an html part

        if self.cc:
            base['Cc'] = self.cc
            
        if self.extra_headers:
            base.update(dict(self.extra_headers))

        if self.attachments:
            base.set_content_type('multipart/mixed')
            altpart = MailBase()
            base.attach_part(altpart)
        else:
            altpart = base
            
        if body and html:
            altpart.set_content_type('multipart/alternative')
            altpart.set_body(None)
            # Per RFC2046, HTML part comes last in multipart/alternative
            altpart.attach_part(body)
            altpart.attach_part(html)

        elif body is not None:
            altpart.merge_part(body)
        elif html is not None:
            altpart.merge_part(html)

        for attachment in self.attachments:
            attachment_mailbase = attachment.to_mailbase()
            base.attach_part(attachment_mailbase)

        return to_message(base)

    def is_bad_headers(self):
        """
        Checks for bad headers i.e. newlines in subject, sender or recipients.
        """

        headers = [self.subject, self.sender]
        headers += list(self.send_to)
        headers += dict(self.extra_headers).values()

        for val in headers:
            for c in '\r\n':
                if c in val:
                    return True
        return False

    def validate(self):
        """
        Checks if message is valid and raises appropriate exception.
        """

        if not (self.recipients or self.cc or self.bcc):
            raise InvalidMessage("No recipients have been added")

        if not self.body and not self.html:
            raise InvalidMessage("No body has been set")

        if not self.sender:
            raise InvalidMessage("No sender address has been set")

        if self.is_bad_headers():
            raise BadHeaders

    def add_recipient(self, recipient):
        """
        Adds another recipient to the message.

        :param recipient: email address of recipient.
        """

        self.recipients.append(recipient)

    def add_cc(self, recipient):
        """
        Adds an email address to the CC list.

        :param recipient: email address of recipient.
        """

        self.cc.append(recipient)

    def add_bcc(self, recipient):
        """
        Adds an email address to the BCC list.

        :param recipient: email address of recipient.
        """

        self.bcc.append(recipient)

    def attach(self, attachment):
        """
        Adds an attachment to the message.

        :param attachment: an **Attachment** instance.
        """

        self.attachments.append(attachment)


class MailBase(object):
    """MailBase is used as the basis of lamson.mail and contains the basics of
    encoding an email.  You actually can do all your email processing with this
    class, but it's more raw.
    """
    def __init__(self, items=()):
        self.headers = dict(items)
        self.parts = []
        self.body = None
        self.content_encoding = {'Content-Type': (None, {}),
                                 'Content-Disposition': (None, {}),
                                 'Content-Transfer-Encoding': None}

    def set_content_type(self, content_type, params=None):
        if params is None:
            params = {}
        content_type, ct_params = parse_header(content_type)
        ct_params.update(params)
        self.content_encoding['Content-Type'] = (content_type, ct_params)

    def get_content_type(self):
        return self.content_encoding['Content-Type']

    def set_content_disposition(self, disposition, params=None):
        if params is None:
            params = {}
        disp, disp_params = parse_header(disposition)
        disp_params.update(params)
        self.content_encoding['Content-Disposition'] = (disp, disp_params)

    def get_content_disposition(self):
        return self.content_encoding['Content-Disposition']

    def set_transfer_encoding(self, encoding):
        self.content_encoding['Content-Transfer-Encoding'] = encoding

    def get_transfer_encoding(self):
        return self.content_encoding['Content-Transfer-Encoding']

    def set_body(self, body):
        self.body = body

    def get_body(self):
        return self.body

    def __getitem__(self, key):
        return self.headers.get(normalize_header(key), None)

    def __len__(self):
        return len(self.headers)

    def __iter__(self):
        return iter(self.headers)

    def __contains__(self, key):
        return normalize_header(key) in self.headers

    def __setitem__(self, key, value):
        self.headers[normalize_header(key)] = value

    def __delitem__(self, key):
        del self.headers[normalize_header(key)]

    def __nonzero__(self):
        return self.body != None or len(
            self.headers) > 0 or len(self.parts) > 0
    
    __bool__ = __nonzero__

    def keys(self):
        """Returns the sorted keys."""
        return sorted(self.headers.keys())

    def update(self, other):
        for k, v in other.items():
            self[k] = v

    def merge_part(self, part):
        body = part.get_body()
        self.set_body(body)
        self.content_encoding.update(part.content_encoding)
        self.headers.update(part.headers)
        self.parts = part.parts[:]

    def attach_part(self, part):
        self.parts.append(part)

    def walk(self):
        for p in self.parts:
            yield p
            for x in p.walk():
                yield x
        

class MIMEPart(MIMEBase):
    """
    A reimplementation of nearly everything in email.mime to be more useful
    for actually attaching things.  Rather than one class for every type of
    thing you'd encode, there's just this one, and it figures out how to
    encode what you ask it.
    """
    def __init__(self, type, **params):
        self.maintype, self.subtype = type.split('/')
        MIMEBase.__init__(self, self.maintype, self.subtype, **params)

    def extract_payload(self, mail):
        body = mail.get_body()
        if body is None:
            return

        ctype, ctype_params = mail.get_content_type()
        cdisp, cdisp_params = mail.get_content_disposition()
        ctenc = mail.get_transfer_encoding()

        assert ctype, ("Extract payload requires that mail.content_encoding "
                       "have a valid Content-Type.")

        charset = ctype_params.get('charset')

        if cdisp:
            # replicate the content-disposition settings
            self.add_header('Content-Disposition', cdisp, **cdisp_params)
        if ctenc:
            # need to encode because repoze.sendmail don't handle attachments
            if isinstance(body, text_type):
                # probably only true on py3
                if charset is None:
                    charset = 'ascii'
                body = body.encode(charset)
            body = transfer_encode_string(ctenc, body)
            self.add_header('Content-Transfer-Encoding', ctenc)

        self.set_payload(body, charset=charset)

    def __repr__(self):
        return "<MIMEPart '%s/%s': '%s', %r, multipart=%r>" % (
            self.subtype,
            self.maintype,
            self['Content-Type'],
            self['Content-Disposition'],
            self.is_multipart()
            )

def to_message(base):
    """
    Given a MailBase, this will construct a MIMEPart that is canonicalized for
    use with the Python email API.
    """
    ctype, params = base.get_content_type()

    if not ctype:
        if base.parts:
            ctype = 'multipart/mixed'
        else:
            ctype = 'text/plain'
    else:
        if base.parts:
            assert ctype.startswith(("multipart", "message")), (
                "Content type should be multipart or message, not %r" % ctype)

    # adjust the content type according to what it should be now
    base.set_content_type(ctype, params)

    try:
        out = MIMEPart(ctype, **params)
    except TypeError as exc:  # pragma: no cover
        raise EncodingError("Content-Type malformed, not allowed: %r; "
                            "%r (Python ERROR: %s" %
                            (ctype, params, exc.message))

    for k in base.keys():
        value = base[k]
        if k.lower() in ADDR_HEADERS:
            if is_nonstr_iter(value):  # not a string
                value = ", ".join(value)
        if value == '':
            continue
        out[k] = value

    out.extract_payload(base)

    # go through the children
    for part in base.parts:
        out.attach(to_message(part))

    return out


def parse_header(header):
    # cope with header value being None or ''
    if header:
        return cgi.parse_header(header)
    else:
        return header, {}


def normalize_header(header):
    return string.capwords(header.lower(), '-')


if sys.version < '3': # on python 2, we must return bytes
    def charset_encode_body(charset, data):
        # on python 2, must return bytes
        if isinstance(data, bytes):
            # - data is bytes and there's a charset
            #   trust that body and charset match and do nothing
            if charset:
                return charset, data
            else:
                # - data is bytes and there's no charset
                #   try to decode body from ascii and raise an exception if cant
                try:
                    data.decode('ascii')
                except UnicodeError:
                    raise EncodingError(
                        'Body is bytes, but no charset supplied and '
                        'cannot decode body from ascii'
                        )
                return None, data
        else:
            if charset:
                # - data is text and there's a charset
                #   trust that body can be encoded using charset and encode it
                return charset, data.encode(charset)
            else:
                # - data is text and there's no charset
                #   use best_charset
                charset, encoded = best_charset(data)
                if charset == 'ascii':
                    charset = None
                return charset, encoded
else: # pragma: no cover (on python 3, we must return text)
    def charset_encode_body(charset, data):
        if isinstance(data, bytes):
            # - data is bytes and there's a charset
            #   trust that body and charset match and do nothing
            if charset:
                return charset, data.decode(charset)
            else:
                # - data is bytes and there's no charset
                #   try to decode body from ascii and raise an exception if cant
                try:
                    return None, data.decode('ascii')
                except UnicodeError:
                    raise EncodingError(
                        'Body is bytes, but no charset supplied and '
                        'cannot decode body from ascii'
                        )
        else:
            if charset:
                # - data is text and there's a charset
                #   trust that body can be encoded using charset and encode it
                return charset, data
            else:
                # - data is text and there's no charset
                #   use best_charset
                charset, encoded = best_charset(data)
                if charset == 'ascii':
                    charset = None
                return charset, data


def transfer_encode_string(encoding, data):
    if encoding == 'base64':
        return base64_encodestring(data).decode('ascii')
    elif encoding == 'quoted-printable':
        return quopri.encodestring(data).decode('ascii')
    raise RuntimeError('Unknown transfer encoding %s' % encoding)


def best_charset(text):
    """
    Find the most human-readable and/or conventional encoding for unicode text.

    Prefers `ascii` or `iso-8859-1` and falls back to `utf-8`.
    """
    encoded = text
    for charset in 'ascii', 'iso-8859-1', 'utf-8':
        try:
            encoded = text.encode(charset)
        except UnicodeError:
            pass
        else:
            return charset, encoded

def setbody(part, body, default_content_type):
    if isinstance(body, MailBase):
        body_text = body.get_body()
        part.set_body(body_text)
        part.content_encoding.update(**body.content_encoding)
    else:
        params = {}
        charset, encbody = charset_encode_body(None, body)
        part.set_body(encbody)
        if charset:
            params['charset'] = charset
        part.set_content_type(default_content_type, params)

    return part

# From http://tools.ietf.org/html/rfc5322#section-3.6
ADDR_HEADERS = (
    'resent-from',
    'resent-sender',
    'resent-to',
    'resent-cc',
    'resent-bcc',
    'from',
    'sender',
    'reply-to',
    'to',
    'cc',
    'bcc'
    )

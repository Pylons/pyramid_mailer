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

from email.mime.nonmultipart import MIMENonMultipart
from email.mime.multipart import MIMEMultipart

from email.encoders import _bencode

from .exceptions import (
    BadHeaders,
    InvalidMessage,
    )

from ._compat import (
    text_type,
    PY2,
    _qencode,
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
        transfer_encoding=None,
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

    def to_mailbase(self, default_content_type=None):
        filename = self.filename
        data = self.data
        content_type = self.content_type or default_content_type
        disposition = self.disposition or 'attachment'
        transfer_encoding = self.transfer_encoding or 'base64'

        if not data:
            raise RuntimeError('No data provided to attachment')
        
        if filename and not content_type:
            content_type, _ = mimetypes.guess_type(filename)

        if not content_type:
            raise RuntimeError(
                "No content type given, and couldn't guess "
                "the content type from a filename provided (%r)" % filename
                )

        content_type, ctparams = cgi.parse_header(content_type)
        disposition, dparams = cgi.parse_header(disposition)

        if filename is None:
            filename = dparams.get('filename')
        
        if filename:
            filename = os.path.split(filename)[1]
            ctparams['name'] = filename
            dparams['filename'] = filename

        base = MailBase()
        base.set_content_type(content_type, ctparams)
        
        charset = ctparams.get('charset', None)
        
        if content_type.startswith('text/'):
            if charset is None:
                charset = best_charset(self.data)[0]
            ctparams['charset'] = charset

        base.set_body(self.data)
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
                bodies[idx] = val.to_mailbase(content_type)
            else:
                # presumed to be a textual val
                attachment = Attachment(
                    data=val,
                    content_type=content_type,
                    transfer_encoding='quoted-printable',
                    disposition='inline'
                    )
                bodies[idx] = attachment.to_mailbase(content_type)

        body, html = bodies

        base = MailBase([
            ('To', ', '.join(self.recipients)),
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
            base['Cc'] = ', '.join(self.cc)
            
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
        self.content_encoding['Content-Type'] = (content_type, params)

    def get_content_type(self):
        return self.content_encoding['Content-Type']

    def set_content_disposition(self, disposition, params=None):
        if params is None:
            params = {}
        self.content_encoding['Content-Disposition'] = (disposition, params)

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

def to_message(base):
    """
    Given a MailBase, this will construct a MIME part that is canonicalized for
    use with the Python email API.
    """
    ctype, ctparams = base.get_content_type()

    if not ctype:
        if base.parts:
            ctype = 'multipart/mixed'
        else:
            ctype = 'text/plain'

    maintype, subtype = ctype.split('/')
    is_text = maintype == 'text'
    is_multipart = maintype == 'multipart'

    if base.parts and not is_multipart:
        raise RuntimeError(
            'Content type should be multipart, not %r' % ctype
            )

    body = base.get_body()
    ctenc = base.get_transfer_encoding()
    charset = ctparams.get('charset')

    if is_multipart:
        out = MIMEMultipart(subtype, **ctparams)
    else:
        out = MIMENonMultipart(maintype, subtype, **ctparams)
        if ctenc:
            out['Content-Transfer-Encoding'] = ctenc
        if isinstance(body, text_type):
            if not charset:
                if is_text:
                    charset, _ = best_charset(body)
                else:
                    charset = 'utf-8'
            if PY2:
                body = body.encode(charset)
            else: # pragma: no cover
                body = body.encode(charset, 'surrogateescape')
        if body is not None:
            if ctenc:
                body = transfer_encode(ctenc, body)
            if not PY2: # pragma: no cover
                body = body.decode(charset or 'ascii', 'replace')
        out.set_payload(body, charset) 

    for k in base.keys(): # returned sorted
        value = base[k]
        if not value:
            continue
        out[k] = value

    cdisp, cdisp_params = base.get_content_disposition()

    if cdisp:
        out.add_header('Content-Disposition', cdisp, **cdisp_params)

    # go through the children
    for part in base.parts:
        sub = to_message(part)
        out.attach(sub)

    return out

def normalize_header(header):
    return string.capwords(header.lower(), '-')

def transfer_encode(encoding, payload):
    # payload must be bytes
    encoding = encoding.lower()
    if encoding == 'base64':
        return _bencode(payload)
    elif encoding == 'quoted-printable':
        return _qencode(payload)
    else:
        raise RuntimeError('Unknown transfer encoding %s' % encoding)

def best_charset(text):
    """
    Find the most human-readable and/or conventional encoding for unicode text.

    Prefers `us-ascii` or `iso-8859-1` and falls back to `utf-8`.
    """
    if isinstance(text, bytes):
        text = text.decode('ascii')
    for charset in 'us-ascii', 'iso-8859-1', 'utf-8':
        try:
            encoded = text.encode(charset)
        except UnicodeError:
            pass
        else:
            return charset, encoded

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

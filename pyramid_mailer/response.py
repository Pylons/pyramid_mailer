# The code in this module is entirely lifted from the Lamson project
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

import os
import sys
import mimetypes
import string
from email.mime.base import MIMEBase

from repoze.sendmail import encoding


def normalize_header(header):
    return string.capwords(header.lower(), '-')

class EncodingError(Exception): 
    """Thrown when there is an encoding error."""
    pass

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
                                 'Content-Transfer-Encoding': (None, {})}

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
        return self.body != None or len(self.headers) > 0 or len(self.parts) > 0
    __bool__ = __nonzero__

    def keys(self):
        """Returns the sorted keys."""
        return sorted(self.headers.keys())

    def attach_file(self, filename, data, ctype, disposition):
        """
        A file attachment is a raw attachment with a disposition that
        indicates the file name.
        """
        assert filename, "You can't attach a file without a filename."
        ctype = ctype.lower()

        part = MailBase()
        part.body = data
        part.content_encoding['Content-Type'] = (ctype, {'name': filename})
        part.content_encoding['Content-Disposition'] = (disposition,
                                                        {'filename': filename})
        self.parts.append(part)


    def attach_text(self, data, ctype):
        """
        This attaches a simpler text encoded part, which doesn't have a
        filename.
        """
        ctype = ctype.lower()

        part = MailBase()
        part.body = data
        part.content_encoding['Content-Type'] = (ctype, {})
        self.parts.append(part)

    def walk(self):
        for p in self.parts:
            yield p
            for x in p.walk():
                yield x

class MailResponse(object):
    """
    You are given MailResponse objects from the lamson.view methods, and
    whenever you want to generate an email to send to someone.  It has the
    same basic functionality as MailRequest, but it is designed to be written
    to, rather than read from (although you can do both).

    You can easily set a Body or Html during creation or after by passing it
    as __init__ parameters, or by setting those attributes.

    You can initially set the From, To, and Subject, but they are headers so
    use the dict notation to change them: msg['From'] = 'joe@test.com'.

    The message is not fully crafted until right when you convert it with
    MailResponse.to_message.  This lets you change it and work with it, then
    send it out when it's ready.
    """
    def __init__(self, To=None, From=None, Subject=None, Body=None, Html=None):
        self.Body = Body
        self.Html = Html
        self.base = MailBase([('To', To), ('From', From), ('Subject', Subject)])
        self.multipart = self.Body and self.Html
        self.attachments = []

    def __contains__(self, key):
        return self.base.__contains__(key)

    def __getitem__(self, key):
        return self.base.__getitem__(key)

    def __setitem__(self, key, val):
        return self.base.__setitem__(key, val)

    def __delitem__(self, name):
        del self.base[name]

    def attach(self, filename=None, content_type=None, data=None,
               disposition=None):
        """

        Simplifies attaching files from disk or data as files.  To attach
        simple text simple give data and a content_type.  To attach a file,
        give the data/content_type/filename/disposition combination.

        For convenience, if you don't give data and only a filename, then it
        will read that file's contents when you call to_message() later.  If
        you give data and filename then it will assume you've filled data
        with what the file's contents are and filename is just the name to
        use.
        """

        assert filename or data, ("You must give a filename or some data to "
                                  "attach.")
        assert data or os.path.exists(filename), ("File doesn't exist, and no "
                                                  "data given.")

        self.multipart = True

        if filename and not content_type:
            content_type, enc = mimetypes.guess_type(filename)

        assert content_type, ("No content type given, and couldn't guess "
                              "from the filename: %r" % filename)

        self.attachments.append({'filename': filename,
                                 'content_type': content_type,
                                 'data': data,
                                 'disposition': disposition,})
    def attach_part(self, part):
        """
        Attaches a raw MailBase part from a MailRequest (or anywhere)
        so that you can copy it over.
        """
        self.multipart = True

        self.attachments.append({'filename': None,
                                 'content_type': None,
                                 'data': None,
                                 'disposition': None,
                                 'part': part,
                                 })

    def attach_all_parts(self, mail_request):
        """
        Used for copying the attachment parts of a mail.MailRequest
        object for mailing lists that need to maintain attachments.
        """
        for part in mail_request.all_parts():
            self.attach_part(part)

        self.base.content_encoding = mail_request.base.content_encoding.copy()

    def clear(self):
        """
        Clears out the attachments so you can redo them.  Use this to keep the
        headers for a series of different messages with different attachments.
        """
        del self.attachments[:]
        del self.base.parts[:]
        self.multipart = False


    def update(self, message):
        """
        Used to easily set a bunch of heading from another dict
        like object.
        """
        for k in message.keys():
            self.base[k] = message[k]

    def __str__(self):
        """
        Converts to a string.
        """
        return self.to_message().as_string()

    def _encode_attachment(self, filename=None, content_type=None, data=None,
                           disposition=None, part=None):
        """
        Used internally to take the attachments mentioned in self.attachments
        and do the actual encoding in a lazy way when you call to_message.
        """
        if part:
            self.base.parts.append(part)
        elif filename:
            if not data:
                f = open(filename)
                data = f.read()
                f.close()

            self.base.attach_file(filename, data, content_type,
                                  disposition or 'attachment')
        else:
            self.base.attach_text(data, content_type)

        ctype = self.base.content_encoding['Content-Type'][0]

        if ctype and not ctype.startswith('multipart'):
            self.base.content_encoding['Content-Type'] = ('multipart/mixed', {})

    def to_message(self):
        """
        Figures out all the required steps to finally craft the
        message you need and return it.  The resulting message
        is also available as a self.base attribute.

        What is returned is a Python email API message you can
        use with those APIs.  The self.base attribute is the raw
        lamson.encoding.MailBase.
        """
        del self.base.parts[:]

        if self.Body and self.Html:
            self.multipart = True
            self.base.content_encoding['Content-Type'] = (
                'multipart/alternative', {})

        if self.multipart:
            self.base.body = None
            if self.Body:
                self.base.attach_text(self.Body, 'text/plain')

            if self.Html:
                self.base.attach_text(self.Html, 'text/html')

            for args in self.attachments:
                self._encode_attachment(**args)

        elif self.Body:
            self.base.body = self.Body
            self.base.content_encoding['Content-Type'] = ('text/plain', {})

        elif self.Html:
            self.base.body = self.Html
            self.base.content_encoding['Content-Type'] = ('text/html', {})

        return to_message(self.base)

    def all_parts(self):
        """
        Returns all the encoded parts.  Only useful for debugging
        or inspecting after calling to_message().
        """
        return self.base.parts

    def keys(self):
        return self.base.keys()

def to_message(mail):
    """
    Given a MailBase message, this will construct a MIMEPart 
    that is canonicalized for use with the Python email API.
    """
    ctype, params = mail.content_encoding['Content-Type']

    if not ctype:
        if mail.parts:
            ctype = 'multipart/mixed'
        else:
            ctype = 'text/plain'
    else:
        if mail.parts:
            assert ctype.startswith(("multipart", "message")), \
                   "Content type should be multipart or message, not %r" % ctype

    # adjust the content type according to what it should be now
    mail.content_encoding['Content-Type'] = (ctype, params)

    try:
        out = MIMEPart(ctype, **params)
    except TypeError: # pragma: no cover
        exc = sys.exc_info()[1]
        raise EncodingError("Content-Type malformed, not allowed: %r; "
                            "%r (Python ERROR: %s" %
                            (ctype, params, exc.message))

    for k in mail.keys():
        value = mail[k]
        if k.lower() in encoding.ADDR_HEADERS:
            if is_nonstr_iter(value): # not a string
                value = ", ".join(value)
        if value == '':
            continue
        out[k] = value

    out.extract_payload(mail)

    # go through the children
    for part in mail.parts:
        out.attach(to_message(part))

    return out

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
        if mail.body == None: return  # only None, '' is still ok

        ctype, ctype_params = mail.content_encoding['Content-Type']
        cdisp, cdisp_params = mail.content_encoding['Content-Disposition']

        assert ctype, ("Extract payload requires that mail.content_encoding "
                       "have a valid Content-Type.")

        if ctype.startswith("text/"):
            self.set_payload(mail.body)
        else:
            if cdisp:
                # replicate the content-disposition settings
                self.add_header('Content-Disposition', cdisp, **cdisp_params)

            self.set_payload(mail.body)

    def __repr__(self):
        return "<MIMEPart '%s/%s': '%s', %r, multipart=%r>" % (
            self.subtype,
            self.maintype,
            self['Content-Type'],
            self['Content-Disposition'],
            self.is_multipart())


def is_nonstr_iter(v): # pragma: no cover
    if isinstance(v, str): 
        return False
    return hasattr(v, '__iter__')

# BBB Python 2 vs 3 compat
if sys.version < '3':
    def is_nonstr_iter(v):
        return hasattr(v, '__iter__')

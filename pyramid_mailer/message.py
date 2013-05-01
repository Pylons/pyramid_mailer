# BBB Python 2 vs 3 compat
try:
    unicode
except NameError:  # pragma: no cover
    basestring = (bytes, str)
else:
    basestring = (str, unicode)

from pyramid_mailer.response import MailResponse
from pyramid_mailer.response import MailBase

from pyramid_mailer.exceptions import BadHeaders
from pyramid_mailer.exceptions import InvalidMessage


class Attachment(object):
    """
    Encapsulates file attachment information.

    :param filename: filename of attachment
    :param content_type: file mimetype
    :param data: the raw file data, either as string or file obj
    :param disposition: content-disposition (if any)
    :param transfer_encoding: content-transfer-encoding (if any)
    """

    def __init__(self,
                 filename=None,
                 content_type=None,
                 data=None,
                 disposition=None,
                 transfer_encoding=None):

        self.filename = filename
        self.content_type = content_type
        self.disposition = disposition or 'attachment'
        self.transfer_encoding = transfer_encoding or 'base64'
        self._data = data

    @property
    def data(self):
        if isinstance(self._data, basestring):
            return self._data
        self._data = self._data.read()
        return self._data


class Message(object):
    """
    Encapsulates an email message.

    :param subject: email subject header
    :param recipients: list of email addresses
    :param body: plain text message
    :param html: HTML message
    :param sender: email sender address
    :param cc: CC list
    :param bcc: BCC list
    :param extra_headers: dict of extra email headers
    :param attachments: list of Attachment instances
    """

    def __init__(self,
                 subject=None,
                 recipients=None,
                 body=None,
                 html=None,
                 sender=None,
                 cc=None,
                 bcc=None,
                 extra_headers=None,
                 attachments=None):

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
        Returns raw email.Message instance.Validates message first.
        """

        self.validate()

        return self.get_response().to_message()

    def get_response(self):
        """
        Creates a Lamson MailResponse instance
        """
        bodies = [self.body, self.html]
        for idx, part in enumerate(bodies):
            if not isinstance(part, Attachment):
                continue

            base = MailBase()
            base.body = part.data
            base.content_encoding['Content-Type'] = (part.content_type, {})
            base.content_encoding[
                'Content-Disposition'] = (part.disposition, {})
            base.content_encoding[
                'Content-Transfer-Encoding'] = part.transfer_encoding
            bodies[idx] = base

        response = MailResponse(Subject=self.subject,
                                To=self.recipients,
                                From=self.sender,
                                Body=bodies[0],
                                Html=bodies[1])

        if self.cc:
            response.base['Cc'] = self.cc

        for attachment in self.attachments:

            response.attach(attachment.filename,
                            attachment.content_type,
                            attachment.data,
                            attachment.disposition,
                            attachment.transfer_encoding)

        response.update(self.extra_headers)

        return response

    def is_bad_headers(self):
        """
        Checks for bad headers i.e. newlines in subject, sender or recipients.
        """

        headers = [self.subject, self.sender]
        headers += list(self.send_to)
        headers += self.extra_headers.values()

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
            raise InvalidMessage("No body or html has been set;"
                " at least one is required")
            
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

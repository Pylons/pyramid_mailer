from pyramid_mailer.response import (
    MailResponse,
    MailBase,
    )

from pyramid_mailer.exceptions import (
    BadHeaders,
    InvalidMessage,
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

    def to_mailbase(self):
        base = MailBase()
        base.set_body(self.data)
        # self.data above will be *either* text or bytes, that's OK
        base.set_content_type(self.content_type)
        # self.content_type above *may* be None, that's OK
        base.set_content_disposition(self.disposition)
        # self.content_disposition above *may* be None, that's OK
        base.set_transfer_encoding(self.transfer_encoding)
        # self.content_transfer_encoding above *may* be None, that's OK
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
            base = part.to_mailbase()
            bodies[idx] = base

        response = MailResponse(
            Subject=self.subject,
            To=self.recipients,
            From=self.sender,
            Body=bodies[0],
            Html=bodies[1]
            )

        if self.cc:
            response.base['Cc'] = self.cc

        for attachment in self.attachments:

            response.attach(
                attachment.filename,
                attachment.content_type,
                attachment.data,
                attachment.disposition,
                attachment.transfer_encoding
                )

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

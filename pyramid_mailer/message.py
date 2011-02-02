from lamson.mail import MailResponse

from zope.interface import implements

from pyramid_mailer.interfaces import IMessage
from pyramid_mailer.interfaces import IAttachment
from pyramid_mailer.exceptions import BadHeaders
from pyramid_mailer.exceptions import InvalidMessage

class Attachment(object):
    implements(IAttachment)

    """
    Encapsulates file attachment information.

    :param filename: filename of attachment
    :param content_type: file mimetype
    :param data: the raw file data
    :param disposition: content-disposition (if any)
 
    """

    def __init__(self, 
                 filename=None, 
                 content_type=None, 
                 data=None,
                 disposition=None): 

        self.filename = filename
        self.content_type = content_type
        self.data = data
        self.disposition = disposition or 'attachment'


class Message(object):
    implements(IMessage)
    
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

    def __init__(self, subject, 
                 recipients=None, 
                 body=None, 
                 html=None, 
                 sender=None,
                 cc=None,
                 bcc=None,
                 extra_headers=None,
                 attachments=None):


        self.subject = subject
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

        response = MailResponse(Subject=self.subject, 
                                To=self.recipients,
                                From=self.sender,
                                Body=self.body,
                                Html=self.html)

        if self.bcc:
            response.base['Bcc'] = self.bcc

        if self.cc:
            response.base['Cc'] = self.cc

        for attachment in self.attachments:

            response.attach(attachment.filename, 
                            attachment.content_type, 
                            attachment.data, 
                            attachment.disposition)

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

        if not self.recipients:
            raise InvalidMessage, "No recipients have been added"

        if not self.body and not self.html:
            raise InvalidMessage, "No body has been set"

        if not self.sender:
            raise InvalidMessage, "No sender address has been set"

        if self.is_bad_headers():
            raise BadHeaders

    def add_recipient(self, recipient):
        """
        Adds another recipient to the message.
        
        :param recipient: email address of recipient.
        """
        
        self.recipients.append(recipient)

    def add_cc(self, recipient):

        self.cc.append(recipient)

    def add_bcc(self, recipient):

        self.bcc.append(recipient)

    def attach(self, attachment):
        
        """
        Adds an IAttachment instance to the message.
        """

        self.attachments.append(attachment)



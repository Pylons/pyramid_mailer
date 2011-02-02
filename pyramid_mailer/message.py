
from lamson.mail import MailResponse

from pyramid_mailer.exceptions import BadHeaders
from pyramid_mailer.exceptions import InvalidMessage

class Attachment(object):

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
    
    """
    Encapsulates an email message.

    :param subject: email subject header
    :param recipients: list of email addresses
    :param body: plain text message
    :param html: HTML message
    :param sender: email sender address, or **DEFAULT_MAIL_SENDER** by default
    :param cc: CC list
    :param bcc: BCC list
    :param attachments: list of Attachment instances

    
    """

    def __init__(self, subject, 
                 recipients=None, 
                 body=None, 
                 html=None, 
                 sender=None,
                 cc=None,
                 bcc=None,
                 attachments=None):


        self.subject = subject
        self.sender = sender
        self.body = body
        self.html = html

        self.recipients = recipients or []
        self.attachments = attachments or []
        self.cc = cc or []
        self.bcc = bcc or []

    @property
    def send_to(self):
        return set(self.recipients) | set(self.bcc or ()) | set(self.cc or ())

    def to_message(self):
        """
        Returns raw email.Message instance
        """
        
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

        return response
    
    def is_bad_headers(self):
        """
        Checks for bad headers i.e. newlines in subject, sender or recipients.
        """
       
        for val in [self.subject, self.sender] + list(self.send_to):
            for c in '\r\n':
                if c in val:
                    return True
        return False
        
    def send(self, mailer):
        """
        Verifies and sends the message.
        """

        if not self.recipients:
            raise InvalidMessage, "No recipients have been added"

        if not self.body or not self.html:
            raise InvalidMessage, "No body has been set"

        if not self.sender:
            raise InvalidMessage, "No sender address has been set"

        if self.is_bad_headers():
            raise BadHeaders

        mailer.send(self)

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

    def attach(self, 
               filename=None, 
               content_type=None, 
               data=None,
               disposition=None):
        
        """
        Adds an attachment to the message.
        
        :param filename: filename of attachment
        :param content_type: file mimetype
        :param data: the raw file data
        :param disposition: content-disposition (if any)
        """

        attachment = Attachment(filename, content_type, data, disposition)

        self.attachments.append(attachment)



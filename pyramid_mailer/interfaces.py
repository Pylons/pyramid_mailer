from zope.interface import Interface
from zope.interface import Attribute


class IAttachment(Interface):

    filename = Attribute("Name of the file")
    content_type = Attribute("Content type")
    data = Attribute("Raw data")
    disposition = Attribute("Content disposition")

    
class IMessage(Interface):

    sender = Attribute("Email from address")
    recipients = Attribute("Iterable of 'to' addresses")

    def to_message():
        """
        Should return "raw" email.Message instance.
        """


class IMailer(Interface):

    def send(message):
        """
        Sends an IMessage instance directly
        """
        
    def send_to_queue(message):
        """
        Adds an IMessage instance directly to queue
        """




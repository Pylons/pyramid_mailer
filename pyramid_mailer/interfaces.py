from zope.interface import Interface
from zope.interface import Attribute


class IMessage(Interface):

    sender = Attribute("Email from address")
    recipients = Attribute("Iterable of 'to' addresses")

    def to_message(self):
        """
        Should return "raw" email.Message instance.
        """


class IMailer(Interface):

    def send(self, message):
        """
        Sends an IMessage instance directly
        """
        
    def send_to_queue(self, message):
        """
        Adds an IMessage instance directly to queue
        """




from zope.interface import Interface

class IMailer(Interface):

    def send(self, message):
        raise NotImplementedError
        
    def send_to_queue(self, message):
        raise NotImplementedError




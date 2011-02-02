from repoze.sendmail.mailer import SMTPMailer
from repoze.sendmail.delivery import DirectMailDelivery
from repoze.sendmail.delivery import QueuedMailDelivery

from zope.interface import implements

from pyramid_mailer.interfaces import IMailer

class DummyMailer(object):
    implements(IMailer)

    """
    Dummy mailing instance
    Used for example in unit tests.

    Keeps all sent messages internally in list as **outbox** property.
    Queued messages are instead added to **queue** property.

    """

    def __init__(self):
        self.outbox = []
        self.queue = []

    def send(self, message):    
        self.outbox.append(message)

    def send_to_queue(self, message):
        self.queue.append(message)


class Mailer(object):
    implements(IMailer)

    """
    Usage: config.registry['mailer'] = Mailer(settings)

    request.registry['mailer'].send(message)
    request.registry['mailer'].send_to_queue(message)
    """

    def __init__(self, settings=None):

        settings = settings or {}

        hostname = settings.get('mail.hostname', 'localhost')
        port = int(settings.get('mail.port', 25))
        username = settings.get('mail.username')
        password = settings.get('mail.password')
        no_tls = not(settings.get('mail.tls'))
        force_tls = settings.get('mail.force_tls')
        queue_path = settings.get('mail.queue_path')
        debug_smtp = settings.get('debug_smtp')

        self.default_sender = settings.get('mail.default_sender')

        smtp_mailer = SMTPMailer(hostname, port, username, password, 
                                 no_tls, force_tls, debug_smtp)

        self.direct_delivery = DirectMailDelivery(smtp_mailer)

        if queue_path:
            self.queue_delivery = QueuedMailDelivery(queue_path)
        else:
            self.queue_delivery = None

    def prep_message(self, message):

        message.sender = message.sender or self.default_sender

        return (message.sender, 
                message.recipients,
                message.to_message())

    def send(self, message):

        return self.direct_delivery.send(*self.prep_message(message))
        
    def send_to_queue(self, message):

        if not self.queue_delivery:
            raise RuntimeError, "You must set mail:queue_path in your settings"
    
        return self.queue_delivery.send(*self.prep_message(message))


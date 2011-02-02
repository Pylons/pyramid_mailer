import smtplib

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
        """
        Mocks sending a direct message. The message is added to the **outbox**
        list.

        :param message : a **pyramid_mailer.interfaces.IMessage** instance.
        """
        self.outbox.append(message)

    def send_to_queue(self, message):
        """
        Mocks sending to a maildir queue. The message is added to the **queue**
        list.

        :param message : a **pyramid_mailer.interfaces.IMessage** instance.
        """
        self.queue.append(message)


class SMTP_SSLMailer(SMTPMailer):
    """
    Subclass of SMTPMailer enabling SSL.
    """

    smtp = smtplib.SMTP_SSL

    def __init__(self, *args, **kwargs):
        self.keyfile = kwargs.pop('keyfile', None)
        self.certfile = kwargs.pop('certfile', None)

        super(SMTP_SSLMailer, self).__init__(*args, **kwargs)

    def smtp_factory(self):

        connection = self.smtp(self.hostname, str(self.port),
                               keyfile=self.keyfile,
                               certfile=self.certfile)

        connection.set_debuglevel(self.debug_smtp)
        return connection


class Mailer(object):
    """
    Manages sending of email messages.

    :param settings : a settings dict. See documentation on the 
                      individual settings required.
    """

    implements(IMailer)

    def __init__(self, settings=None):

        settings = settings or {}

        host = settings.get('mail.host', 'localhost')
        port = int(settings.get('mail.port', 25))
        username = settings.get('mail.username')
        password = settings.get('mail.password')
        tls = settings.get('mail.tls', False)
        ssl = settings.get('mail.ssl', False)
        keyfile = settings.get('mail.keyfile')
        certfile = settings.get('mail.certfile')
        queue_path = settings.get('mail.queue_path')
        debug_smtp = int(settings.get('mail.debug', 0))

        self.default_sender = settings.get('mail.default_sender')

        if ssl:

            smtp_mailer = SMTP_SSLMailer(hostname=host,
                                         port=port,
                                         username=username,
                                         password=password,
                                         no_tls=not(tls),
                                         force_tls=tls,
                                         debug_smtp=debug_smtp,
                                         keyfile=keyfile,
                                         certfile=certfile)

        else:

            smtp_mailer = SMTPMailer(hostname=host, 
                                     port=port, 
                                     username=username, 
                                     password=password, 
                                     no_tls=not(tls), 
                                     force_tls=tls, 
                                     debug_smtp=debug_smtp)

        self.direct_delivery = DirectMailDelivery(smtp_mailer)

        if queue_path:
            self.queue_delivery = QueuedMailDelivery(queue_path)
        else:
            self.queue_delivery = None

    def send(self, message):
        """
        Sends a message immediately.

        :param message : a **pyramid_mailer.interfaces.IMessage** instance.
        """

        return self.direct_delivery.send(*self._message_args(message))
        
    def send_to_queue(self, message):
        """
        Adds a message to a maildir queue.
        
        In order to handle this, the setting **mail.queue_path** must be 
        provided and must point to a valid maildir.

        :param message : a **pyramid_mailer.interfaces.IMessage** instance.
        """

        if not self.queue_delivery:
            raise RuntimeError, "You must set mail:queue_path in your settings"
    
        return self.queue_delivery.send(*self._message_args(message))

    def _message_args(self, message):

        message.sender = message.sender or self.default_sender

        return (message.sender, 
                message.recipients,
                message.to_message())


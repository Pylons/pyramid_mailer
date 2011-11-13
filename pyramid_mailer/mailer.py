import smtplib

from repoze.sendmail.mailer import SMTPMailer
from repoze.sendmail.delivery import DirectMailDelivery
from repoze.sendmail.delivery import QueuedMailDelivery


class DummyMailer(object):
    """
    Dummy mailing instance, used for example in unit tests.

    Keeps all sent messages internally in list as **outbox** property.
    Queued messages are instead added to **queue** property.
    """

    def __init__(self):
        self.outbox = []
        self.queue = []

    def send(self, message):    
        """
        Mocks sending a transactional message. The message is added to the 
        **outbox** list.

        :param message: a **Message** instance.
        """
        self.outbox.append(message)

    def send_immediately(self, message, fail_silently=False):
        """
        Mocks sending an immediate (non-transactional) message. The message
        is added to the **outbox** list.

        :versionadded: 0.3

        :param message: a **Message** instance.
        :param fail_silently: swallow connection errors (ignored here)
        """
        self.outbox.append(message)

    def send_to_queue(self, message):
        """
        Mocks sending to a maildir queue. The message is added to the **queue**
        list.

        :param message: a **Message** instance.
        """
        self.queue.append(message)


class SMTP_SSLMailer(SMTPMailer):
    """
    Subclass of SMTPMailer enabling SSL.
    """

    try:
        # support disabled if pre-2.6
        smtp = smtplib.SMTP_SSL
        ssl_support = True
    except AttributeError: # pragma: no cover
        smtp = smtplib.SMTP
        ssl_support = False

    def __init__(self, *args, **kwargs):
        self.keyfile = kwargs.pop('keyfile', None)
        self.certfile = kwargs.pop('certfile', None)

        super(SMTP_SSLMailer, self).__init__(*args, **kwargs)

    def smtp_factory(self):

        if self.ssl_support is False: # pragma: no cover
            return super(SMTP_SSLMailer, self).smtp_factory()

        connection = self.smtp(self.hostname, str(self.port),
                               keyfile=self.keyfile,
                               certfile=self.certfile)

        connection.set_debuglevel(self.debug_smtp) # pragma: no cover
        return connection # pragma: no cover


class Mailer(object):
    """
    Manages sending of email messages.

    :param host: SMTP hostname
    :param port: SMTP port
    :param username: SMTP username
    :param password: SMPT password
    :param tls: use TLS
    :param ssl: use SSL
    :param keyfile: SSL key file 
    :param certfile: SSL certificate file
    :param queue_path: path to maildir for queued messages
    :param default_sender: default "from" address
    :param debug: SMTP debug level
    """

    def __init__(self, 
                 host='localhost', 
                 port=25, 
                 username=None,
                 password=None, 
                 tls=False,
                 ssl=False,
                 keyfile=None,
                 certfile=None,
                 queue_path=None,
                 default_sender=None,
                 debug=0):


        if ssl:

            self.smtp_mailer = SMTP_SSLMailer(
                hostname=host,
                port=port,
                username=username,
                password=password,
                no_tls=not(tls),
                force_tls=tls,
                debug_smtp=debug,
                keyfile=keyfile,
                certfile=certfile)

        else:

            self.smtp_mailer = SMTPMailer(
                hostname=host, 
                port=port, 
                username=username, 
                password=password, 
                no_tls=not(tls), 
                force_tls=tls, 
                debug_smtp=debug)

        self.direct_delivery = DirectMailDelivery(self.smtp_mailer)

        if queue_path:
            self.queue_delivery = QueuedMailDelivery(queue_path)
        else:
            self.queue_delivery = None

        self.default_sender = default_sender

    @classmethod
    def from_settings(cls, settings, prefix='mail.'):
        """
        Creates a new instance of **Message** from settings dict.

        :param settings: a settings dict-like
        :param prefix: prefix separating **pyramid_mailer** settings
        """

        settings = settings or {}

        kwarg_names = [prefix + k for k in (
                       'host', 'port', 'username',
                       'password', 'tls', 'ssl', 'keyfile', 
                       'certfile', 'queue_path', 'debug', 'default_sender')]
        
        size = len(prefix)

        kwargs = dict(((k[size:], settings[k]) for k in settings.keys() if
                        k in kwarg_names))

        return cls(**kwargs)

    def send(self, message):
        """
        Sends a message. The message is handled inside a transaction, so 
        in case of failure (or the message fails) the message will not be sent.

        :param message: a **Message** instance.
        """

        return self.direct_delivery.send(*self._message_args(message))

    def send_immediately(self, message, fail_silently=False):
        """
        Sends a message immediately, outside the transaction manager. 

        If there is a connection error to the mail server this will have to 
        be handled manually. However if you pass ``fail_silently`` the error
        will be swallowed.

        :versionadded: 0.3

        :param message: a **Message** instance.

        :param fail_silently: silently handle connection errors.
        """

        try:
            return self.smtp_mailer.send(*self._message_args(message))
        except smtplib.socket.error:
            if not fail_silently:
                raise

    def send_to_queue(self, message):
        """
        Adds a message to a maildir queue.
        
        In order to handle this, the setting **mail.queue_path** must be 
        provided and must point to a valid maildir.

        :param message: a **Message** instance.
        """

        if not self.queue_delivery:
            raise RuntimeError, "No queue_path provided"
    
        return self.queue_delivery.send(*self._message_args(message))

    def _message_args(self, message):

        message.sender = message.sender or self.default_sender

        return (message.sender, 
                message.send_to,
                message.to_message())


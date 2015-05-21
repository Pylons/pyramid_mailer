from datetime import datetime
from os import makedirs
from os.path import exists
from os.path import join
from random import sample
import smtplib

from pyramid.settings import asbool
from pyramid.settings import aslist
from repoze.sendmail.mailer import SMTPMailer
from repoze.sendmail.mailer import SendmailMailer
from repoze.sendmail.delivery import DirectMailDelivery
from repoze.sendmail.delivery import QueuedMailDelivery

from pyramid_mailer._compat import SMTP_SSL


class DebugMailer(object):
    """ Debug mailer for testing

    Stores messages as files in the specified directory.
    """
    def __init__(self, top_level_directory):
        if not exists(top_level_directory):
            makedirs(top_level_directory)
        self.tld = top_level_directory

    @classmethod
    def from_settings(cls, settings, prefix='mail.'):
        """Create a new instance of 'DebugMailer' from settings dict.

        :param settings: a settings dict-like
        :param prefix: prefix separating 'pyramid_mailer' settings
        """
        settings = settings or {}
        top_level_directory = settings.get(prefix+'top_level_directory')
        if top_level_directory is None:
            raise ValueError("DebugMailer:  must specify "
                             "'%stop_level_directory'" % prefix)
        return cls(top_level_directory)

    def _send(self, message, fail_silently=False):
        """Save message to a file for debugging
        """
        seeds = '1234567890qwertyuiopasdfghjklzxcvbnm'
        file_part1 = datetime.now().strftime('%Y%m%d%H%M%S')
        file_part2 = ''.join(sample(seeds, 4))
        filename = join(self.tld, '%s_%s.msg' % (file_part1, file_part2))
        with open(filename, 'w') as fd:
            if not message.sender:
                message.sender = 'nobody'
            fd.write(str(message.to_message()))

    send = _send
    send_immediately = _send
    send_to_queue = _send
    send_sendmail = _send
    send_immediately_sendmail = _send


class DummyMailer(object):
    """Dummy mailer instance, used for example in unit tests.

    Sent messages are appended to 'outbox' list.

    Queued messages are appended to 'queue' list.
    """

    def __init__(self):
        self.outbox = []
        self.queue = []

    def send(self, message):
        """Mock sending a transactional message via SMTP.

        The message is appended to the 'outbox' list.

        :param message: a 'Message' instance.
        """
        self.outbox.append(message)

    def send_immediately(self, message, fail_silently=False):
        """Mock sending an immediate (non-transactional) message.

        The message is appended to the 'outbox' list.

        :versionadded: 0.3

        :param message: a 'Message' instance.
        :param fail_silently: swallow connection errors (ignored here)
        """
        self.outbox.append(message)

    def send_to_queue(self, message):
        """Mock sending to a maildir queue.

        The message is appended to the 'queue' list.

        :param message: a 'Message' instance.
        """
        self.queue.append(message)

    def send_sendmail(self, message ):
        """Mock sending a transactional message via sendmail.

        The message is added to the 'outbox' list.

        :param message: a 'Message' instance.
        """
        self.outbox.append(message)

    def send_immediately_sendmail(self, message, fail_silently=False):
        """Mock sending an immediate (non-transactional) message.

        The message is added to the 'outbox' list.

        :param message: a 'Message' instance.
        :param fail_silently: swallow connection errors (ignored here)
        """
        self.outbox.append(message)


class SMTP_SSLMailer(SMTPMailer):
    """Subclass of SMTPMailer enabling SSL.
    """
    smtp = SMTP_SSL

    def __init__(self, *args, **kwargs):
        self.keyfile = kwargs.pop('keyfile', None)
        self.certfile = kwargs.pop('certfile', None)
        super(SMTP_SSLMailer, self).__init__(*args, **kwargs)

    def smtp_factory(self):
        if self.smtp is None:
            raise RuntimeError(
                    'No SMTP_SSL support in Python usable by mailer')

        connection = self.smtp(
            self.hostname,
            str(self.port),
            keyfile=self.keyfile,
            certfile=self.certfile
            )
        connection.set_debuglevel(self.debug_smtp)
        return connection


class Mailer(object):
    """Manages sending of email messages.

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
    :param sendmail_app: path to "sendmail" binary.
           repoze defaults to "/usr/sbin/sendmail"
    :param sendmail_template: custom commandline template for sendmail binary,
           defaults to'["{sendmail_app}", "-t", "-i", "-f", "{sender}"]'
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
                 sendmail_app=None,
                 sendmail_template=None,
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

        self.sendmail_mailer = SendmailMailer(sendmail_app, sendmail_template)
        self.sendmail_delivery = DirectMailDelivery(self.sendmail_mailer)
        self.default_sender = default_sender

    @classmethod
    def from_settings(cls, settings, prefix='mail.'):
        """Create a new instance of 'Mailer' from settings dict.

        :param settings: a settings dict-like
        :param prefix: prefix separating 'pyramid_mailer' settings
        """
        settings = settings or {}

        kwarg_names = [prefix + k for k in (
                       'host', 'port', 'username',
                       'password', 'tls', 'ssl', 'keyfile',
                       'certfile', 'queue_path', 'debug', 'default_sender',
                       'sendmail_app', 'sendmail_template')]

        size = len(prefix)

        kwargs = dict(((k[size:], settings[k]) for k in settings.keys() if
                        k in kwarg_names))

        for key in ('tls', 'ssl'):
            val = kwargs.get(key)
            if val:
                kwargs[key] = asbool(val)

        for key in ('debug', 'port'):
            val = kwargs.get(key)
            if val:
                kwargs[key] = int(val)

        # list values
        for key in ('sendmail_template', ):
            if key in kwargs:
                kwargs[key] = aslist(kwargs.get(key))

        return cls(**kwargs)

    def send(self, message):
        """Send a message.

        The message is handled inside a transaction, so in case of failure
        (or the message fails) the message will not be sent.

        :param message: a 'Message' instance.
        """
        return self.direct_delivery.send(*self._message_args(message))

    def send_immediately(self, message, fail_silently=False):
        """Send a message immediately, outside the transaction manager.

        If there is a connection error to the mail server this will have to
        be handled manually. However if you pass ``fail_silently`` the error
        will be swallowed.

        :versionadded: 0.3

        :param message: a 'Message' instance.

        :param fail_silently: silently handle connection errors.
        """
        try:
            return self.smtp_mailer.send(*self._message_args(message))
        except smtplib.socket.error:
            if not fail_silently:
                raise

    def send_to_queue(self, message):
        """Add a message to a maildir queue.

        In order to handle this, the setting 'mail.queue_path' must be
        provided and must point to a valid maildir.

        :param message: a 'Message' instance.
        """
        if not self.queue_delivery:
            raise RuntimeError("No queue_path provided")

        return self.queue_delivery.send(*self._message_args(message))

    def _message_args(self, message):

        message.sender = message.sender or self.default_sender
        # convert Lamson message to Python email package msessage
        msg = message.to_message()
        return (message.sender, message.send_to, msg)

    def send_sendmail(self, message ):
        """Send a message within the transaction manager.

        Uses the local sendmail option

        :param message: a 'Message' instance.
        """
        return self.sendmail_delivery.send(*self._message_args(message))

    def send_immediately_sendmail(self, message, fail_silently=False):
        """Send a message immediately, outside the transaction manager.

        Uses the local sendmail option

        If there is a connection error to the mail server this will have to
        be handled manually. However if you pass ``fail_silently`` the error
        will be swallowed.

        :param message: a 'Message' instance.

        :param fail_silently: silently handle connection errors.
        """
        try:
            return self.sendmail_mailer.send(*self._message_args(message))
        except:
            if not fail_silently:
                raise

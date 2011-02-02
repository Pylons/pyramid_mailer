from repoze.sendmail.mailer import SMTPMailer
from repoze.sendmail.delivery import DirectMailDelivery
from repoze.sendmail.delivery import QueuedMailDelivery


class Mailer(object):

    """
    Usage: config.registry['mailer'] = Mailer(config)

    request.registry['mailer'].send(message)
    request.registry['mailer'].send_to_queue(message)
    """

    def __init__(self, settings=None):

        settings = settings or {}

        hostname = settings.get('mail:hostname', 'localhost')
        port = int(settings.get('mail:port', 25))
        username = settings.get('mail:username')
        password = settings.get('mail:password')
        no_tls = not(settings.get('mail:tls'))
        force_tls = settings.get('mail:force_tls')
        queue_path = settings.get('mail:queue_path')
        debug_smtp = settings.get('debug_smtp')

        smtp_mailer = SMTPMailer(hostname, port, username, password, 
                                 no_tls, force_tls, debug_smtp)

        self.direct_delivery = DirectMailDelivery(smtp_mailer)

        if queue_path:
            self.queue_delivery = QueuedMailDelivery(queue_path)

    def send(self, message):

        return self.direct_delivery.send(message.sender,
                                         message.recipients,
                                         message.to_message())
        
    def send_to_queue(self, message):
    
        return self.queue_delivery.send(message.sender,
                                        message.recipients,
                                        message.to_message())


pyramid_mailer
==================

**pyramid_mailer** is a package for the Pyramid framework to take the pain out of sending emails. It has the following features:

1. A wrapper around the low-level email functionality of standard Python. This includes handling multipart emails with both text and
   HTML content, and file attachments.

2. The option of directly sending an email or adding it to the queue in your maildir.

3. Wrapping email sending in the transaction manager. If you have a view that sends a customer an email for example, and there is an
   error in that view (for example, a database error) then this ensures that the email is not sent.

4. A ``DummyMailer`` class to help with writing unit tests, or other situations where you want to avoid emails being sent accidentally
   from a non-production install.

**pyramid_mailer** uses the `repoze_sendmail`_ package for general email sending, queuing and transaction management, and the `Lamson`_
library for low-level multipart message encoding and wrapping. You do not have to install or run a Lamson mail service.

Installation
------------

Install using **pip install pyramid_mailer** or **easy_install pyramid_mailer**.

If installing from source, untar/unzip, cd into the directory and do **python setup.py install**.

The source repository is on `Bitbucket`_. Please report any bugs, issues or queries there. 

Installing on Windows
---------------------

Some Windows users have reported issues installing `Lamson`_ due to some dependencies that do not work on Windows.

The best way to install on Windows is to install the individual packages using the `no dependencies` option::

    easy_install -N lamson chardet repoze.sendmail pyramid_mailer


Getting started
---------------

To get started create an instance of :class:`pyramid_mailer.mailer.Mailer`::

    from pyramid_mailer.mailer import Mailer

    mailer = Mailer()

The ``Mailer`` class can take a number of optional settings, detailed in :ref:`configuration`. It's a good idea to create a single ``Mailer`` instance for your application, and add it to your registry in your configuration setup::

    config = Configurator(settings=settings)
    config.registry['mailer'] = Mailer.from_settings(settings)

You can then access your mailer in a view::

    def my_view(request):
        mailer = request.registry['mailer']

To send a message, you must first create a :class:`pyramid_mailer.message.Message` instance::

    from pyramid_mailer.message import Message

    message = Message(subject="hello world",
                      sender="admin@mysite.com",
                      recipients=["arthur.dent@gmail.com"],
                      body="hello, arthur")

The ``Message`` is then passed to the ``Mailer`` instance. You can either send the message right away::

    mailer.send(message)

or add it to your mail queue (a maildir on disk)::

    mailer.send_to_queue(message)


Usually you provide the ``sender`` to your ``Message`` instance. Often however a site might just use a single from address. If that is the case you can provide the ``default_sender`` to your ``Mailer`` and this will be used in throughout your application as the default if the ``sender`` is not otherwise provided.

.. _configuration:

Configuration
-------------

If you create your ``Mailer`` instance using :meth:`pyramid_mailer.mailer.Mailer.from_settings`, you can pass the settings from your .ini file or other source. By default, the prefix is assumed to be `mail.` although you can use another prefix if you wish.

=========================  ===============    =====================
Setting                    Default            Description              
=========================  ===============    =====================
**mail.host**              ``localhost``      SMTP host                
**mail.port**              ``25``             SMTP port                
**mail.username**          **None**           SMTP username            
**mail.password**          **None**           SMTP password           
**mail.tls**               **False**          Use TLS                  
**mail.ssl**               **False**          Use SSL                  
**mail.keyfile**           **None**           SSL key file             
**mail.certfile**          **None**           SSL certificate file     
**mail.queue_path**        **None**           Location of maildir      
**mail.default_sender**    **None**           Default from address     
**mail.debug**             **False**          SMTP debug level         
=========================  ===============    =====================

**Note:** SSL will only work with **pyramid_mailer** if you are using Python **2.6** or higher, as it uses the SSL additions to the ``smtplib`` package. While it may be possible to work around this if you have to use Python 2.5 or lower, **pyramid_mailer** does not support this out of the box.

Transactions
------------

If you are using transaction management with your Pyramid application then **pyramid_mailer** will only send the emails (or add them to the mail queue) when the transactions are committed. 

For example::

    import transaction

    from pyramid_mailer.mailer import Mailer
    from pyramid_mailer.message import Message

    mailer = Mailer()
    message = Message(subject="hello arthur",
                      sender="ford.prefect@gmail.com",
                      recipients=['arthur.dent@gmail.com'],
                      body="hello from ford")


    mailer.send(message)
    transaction.commit()


The email is not actually sent until the transaction is committed. 

When the `repoze.tm2 <http://pypi.python.org/pypi/repoze.tm2>`_ ``tm``
middleware is in your Pyramid WSGI pipeline, transactions are already managed
for you, so you don't need to explicitly commit or abort within code that
sends mail.  Instead, if an exception is raised, the transaction will
implicitly be aborted and mail will not be sent; otherwise it will be
committed, and mail will be sent.

Attachments
-----------

Attachments are added using the :class:`pyramid_mailer.message.Attachment` class::

    from pyramid_mailer.message import Attachment
    from pyramid_mailer.message import Message

    message = Message()

    photo_data = open("photo.jpg", "rb").read()
    attachment = Attachment("photo.jpg", "image/jpg", photo_data)

    message.attach(attachment)

You can pass the data either as a string or file object, so the above code could be rewritten::

    from pyramid_mailer.message import Attachment
    from pyramid_mailer.message import Message

    message = Message()

    attachment = Attachment("photo.jpg", "image/jpg", 
                            open("photo.jpg", "rb"))

    message.attach(attachment)



Unit tests
----------

When running unit tests you probably don't want to actually send any emails inadvertently. However it's still useful to keep track of what emails would be sent in your tests. 

Another case is if your site is in development and you want to avoid accidental sending of any emails to customers.

In either case, the :class:`pyramid_mailer.mailer.DummyMailer` can be used::

    class TestViews(unittest.TestCase):

        def test_some_view(self):
            
            from pyramid.config import Configurator
            from pyramid.testing import DummyRequest
            from pyramid_mailer.mailer import DummyMailer

            config = Configurator()
            mailer = DummyMailer()
            config.registry['mailer'] = mailer

            request = DummyRequest()
            response = some_view(request)

The ``DummyMailer`` instance keeps track of emails "sent" in two properties: `queue` for emails send via :meth:`pyramid_mailer.mailer.Mailer.send_to_queue` and `outbox` for emails sent via :meth:`pyramid_mailer.mailer.Mailer.send`. Each stores the individual ``Message`` instances::

    self.assertEqual(len(mailer.outbox) == 1)
    self.assertEqual(mailer.outbox[0].subject == "hello world")

    self.assertEqual(len(mailer.queue) == 1)
    self.assertEqual(mailer.queue[0].subject == "hello world")

Queue
-----

When you send mail to a queue via
:meth:`pyramid_mailer.Mailer.send_to_queue`, the mail will be placed into a
``maildir`` directory specified by the ``queue_path`` parameter or setting to :class:`pyramid_mailer.mailer.Mailer`.  A
separate process will need to be launched to monitor this maildir and take
actions based on its state.  Such a program comes as part of
`repoze_sendmail`_ (a dependency of the ``pyramid_mailer`` package).  It is
known as ``qp``.  ``qp`` will be installed into your Python (or virtualenv)
``bin`` or ``Scripts`` directory when you install ``repoze_sendmail``.

You'll need to arrange for ``qp`` to be a long-running process that monitors
the maildir state.::

  $ bin/qp /path/to/mail/queue

This will attempt to use the localhost SMTP server to send any messages in
the queue over time.  ``qp`` has other options that allow you to choose
different settings.  Use it's ``--help`` parameter to see more::

  $ bin/qp --help
        
API
---

.. module:: pyramid_mailer.mailer

.. autoclass:: Mailer
   :members:

.. autoclass:: DummyMailer
   :members:
    
.. module:: pyramid_mailer.message

.. autoclass:: Message
   :members:

.. autoclass:: Attachment
   :members:

.. module:: pyramid_mailer.exceptions

.. autoclass:: InvalidMessage
   :members:

.. autoclass:: BadHeaders
   :members:

.. _Bitbucket: http://bitbucket.org/danjac/pyramid_mailer
.. _Pyramid: http://pypi.python.org/pypi/pyramid/
.. _repoze_sendmail: http://pypi.python.org/pypi/repoze_sendmail/
.. _Lamson: http://pypi.python.org/pypi/lamson/

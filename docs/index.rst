pyramid_mailer
==================

**pyramid_mailer** is a package for the `Pyramid`_ framework to take the pain
  out of sending emails. It has the following features:

1. A wrapper around the low-level email functionality of standard
   Python. This includes handling multipart emails with both text and HTML
   content, and file attachments.

2. The option of directly sending an email or adding it to the queue in your
maildir.

3. Wrapping email sending in the transaction manager. If you have a view that
   sends a customer an email for example, and there is an error in that view
   (for example, a database error) then this ensures that the email is not
   sent.

4. A ``DummyMailer`` class to help with writing unit tests, or other
   situations where you want to avoid emails being sent accidentally from a
   non-production install.

**pyramid_mailer** uses the `repoze_sendmail`_ package for general email
sending, queuing and transaction management, and it borrows code from Zed
Shaw's `Lamson`_ library for low-level multipart message encoding and
wrapping.

Installation
------------

Install using **pip install pyramid_mailer** or **easy_install
pyramid_mailer**.

If installing from source, untar/unzip, cd into the directory and do **python
setup.py install**.

The source repository is on `Github`_. Please report any bugs, issues or
queries there.

Getting Started (The Easier Way)
--------------------------------

In your application's configuration stanza (where you create a Pyramid
"Configurator"), use the ``config.include`` method::

   config.include('pyramid_mailer')

Thereafter in view code, use the ``pyramid_mailer.get_mailer`` API to obtain
the configured mailer::

   from pyramid_mailer import get_mailer
   mailer = get_mailer(request)

To send a message, you must first create a
:class:`pyramid_mailer.message.Message` instance::

    from pyramid_mailer.message import Message

    message = Message(subject="hello world",
                      sender="admin@mysite.com",
                      recipients=["arthur.dent@gmail.com"],
                      body="hello, arthur")

The ``Message`` is then passed to the ``Mailer`` instance. You can either
send the message right away::

    mailer.send(message)

or add it to your mail queue (a maildir on disk)::

    mailer.send_to_queue(message)

Usually you provide the ``sender`` to your ``Message`` instance. Often
however a site might just use a single from address. If that is the case you
can provide the ``default_sender`` to your ``Mailer`` and this will be used
in throughout your application as the default if the ``sender`` is not
otherwise provided.


If you don't want to use transactions, you can side-step them by using
**send_immediately**::

    mailer.send_immediately(message, fail_silently=False)

This will send the email immediately, outwith the transaction, so if it fails
you have to deal with it manually. The ``fail_silently`` flag will swallow
any connection errors silently - if it's not important whether the email gets
sent.

Getting Started (The Harder Way)
--------------------------------

To get started the harder way (without using ``config.include``), create an
instance of :class:`pyramid_mailer.mailer.Mailer`::

    from pyramid_mailer.mailer import Mailer

    mailer = Mailer()

The ``Mailer`` class can take a number of optional settings, detailed in
:ref:`configuration`. It's a good idea to create a single ``Mailer`` instance
for your application, and add it to your registry in your configuration
setup::

    config = Configurator(settings=settings)
    config.registry['mailer'] = Mailer.from_settings(settings)

or alternatively::

    from pyramid_mailer import mailer_factory_from_settings
    config.registry['mailer'] = mailer_factory_from_settings(settings)

You can then access your mailer in a view::

    def my_view(request):
        mailer = request.registry['mailer']

Note that the ``pyramid_mailer.get_mailer()`` API will not work if you
construct and set your own mailer in this way.

.. _configuration:

Configuration
-------------

If you configure a ``Mailer`` using
:meth:`pyramid_mailer.mailer.Mailer.from_settings` or
``config.include('pyramid_mailer')``, you can pass the settings from your
Paste ``.ini`` file.  For example::

  [app:myproject]
  mail.host = localhost
  mail.port = 25

By default, the prefix for is assumed to be `mail.`.  If you use the
``config.include`` mechanism, to set another prefix, use the
``pyramid_mailer.prefix`` key in the config file.  For example::

  [app:myproject]
  foo.host = localhost
  foo.port = 25
  pyramid_mailer.prefix = foo.

If you use the :meth:`pyramid_mailer.Mailer.Mailer.from_settings` or
:func:`pyramid_mailer.mailer_factory_from_settings` API, these accept a
prefix directly; for example::

  mailer_factory_from_settings(settings, prefix='foo.')

If you don't use Paste, just pass the settings directly into your Pyramid
``Configurator``::

   settings = {'mail.host':'localhost', 'mail.port':'25'}
   Configurator(settings=settings)
   config.include('pyramid_mailer')

The available settings are listed below.

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

**Note:** SSL will only work with **pyramid_mailer** if you are using Python
  **2.6** or higher, as it uses the SSL additions to the ``smtplib``
  package. While it may be possible to work around this if you have to use
  Python 2.5 or lower, **pyramid_mailer** does not support this out of the
  box.

Transactions
------------

If you are using transaction management with your Pyramid application then
**pyramid_mailer** will only send the emails (or add them to the mail queue)
when the transactions are committed.

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
middleware is in your Pyramid WSGI pipeline or if you've included the
``pyramid_tm`` package in your Pyramid configuration, transactions are
already managed for you, so you don't need to explicitly commit or abort
within code that sends mail.  Instead, if an exception is raised, the
transaction will implicitly be aborted and mail will not be sent; otherwise
it will be committed, and mail will be sent.

Attachments
-----------

Attachments are added using the :class:`pyramid_mailer.message.Attachment`
class::

    from pyramid_mailer.message import Attachment
    from pyramid_mailer.message import Message

    message = Message()

    photo_data = open("photo.jpg", "rb").read()
    attachment = Attachment("photo.jpg", "image/jpg", photo_data)

    message.attach(attachment)

You can pass the data either as a string or file object, so the above code
could be rewritten::


    from pyramid_mailer.message import Attachment
    from pyramid_mailer.message import Message

    message = Message()

    attachment = Attachment("photo.jpg", "image/jpg", 
                            open("photo.jpg", "rb"))

    message.attach(attachment)



Unit tests
----------

When running unit tests you probably don't want to actually send any emails
inadvertently. However it's still useful to keep track of what emails would
be sent in your tests.

Another case is if your site is in development and you want to avoid
accidental sending of any emails to customers.

In either case, ``config.include('pyramid_mailer.testing')`` can be used to
make the current mailer an instance of the
:class:`pyramid_mailer.mailer.DummyMailer`::

    from pyramid import testing

    class TestViews(unittest.TestCase):
        def setUp(self):
            self.config = testing.setUp()
            self.config.include('pyramid_mailer.testing')

        def tearDown(self):
            testing.tearDown()

        def test_some_view(self):
            from pyramid.testing import DummyRequest
            from pyramid_mailer import get_mailer
            request = DummyRequest()
            mailer = get_mailer(request)
            response = some_view(request)

The ``DummyMailer`` instance keeps track of emails "sent" in two properties:
`queue` for emails send via
:meth:`pyramid_mailer.mailer.Mailer.send_to_queue` and `outbox` for emails
sent via :meth:`pyramid_mailer.mailer.Mailer.send`. Each stores the
individual ``Message`` instances::

    self.assertEqual(len(mailer.outbox) == 1)
    self.assertEqual(mailer.outbox[0].subject == "hello world")

    self.assertEqual(len(mailer.queue) == 1)
    self.assertEqual(mailer.queue[0].subject == "hello world")

Queue
-----

When you send mail to a queue via
:meth:`pyramid_mailer.Mailer.send_to_queue`, the mail will be placed into a
``maildir`` directory specified by the ``queue_path`` parameter or setting to
:class:`pyramid_mailer.mailer.Mailer`.  A separate process will need to be
launched to monitor this maildir and take actions based on its state.  Such a
program comes as part of `repoze_sendmail`_ (a dependency of the
``pyramid_mailer`` package).  It is known as ``qp``.  ``qp`` will be
installed into your Python (or virtualenv) ``bin`` or ``Scripts`` directory
when you install ``repoze_sendmail``.

You'll need to arrange for ``qp`` to be a long-running process that monitors
the maildir state.::

  $ bin/qp /path/to/mail/queue

This will attempt to use the localhost SMTP server to send any messages in
the queue over time.  ``qp`` has other options that allow you to choose
different settings.  Use it's ``--help`` parameter to see more::

  $ bin/qp --help
        
API
---

.. module:: pyramid_mailer
    
.. autofunction:: mailer_factory_from_settings

.. autofunction:: get_mailer

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

.. _Github: https://github.com/Pylons/pyramid_mailer
.. _Pyramid: http://pypi.python.org/pypi/pyramid/
.. _repoze_sendmail: http://pypi.python.org/pypi/repoze.sendmail/
.. _Lamson: http://pypi.python.org/pypi/lamson/

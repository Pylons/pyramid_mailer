pyramid_mailer
==================

**pyramid_mailer** is a package for the `Pyramid`_ framework to take the pain
out of sending emails. It is compatible with Python 2.7, 3.3, and 3.4, as well
as PyPy. It has the following features:

1. A wrapper around the low-level email functionality of standard
   Python. This includes handling multipart emails with both text and HTML
   content, and file attachments.

2. The option of directly sending an email or adding it to the queue in your
   maildir.

3. Wrapping email sending in the transaction manager. If you have a view that
   sends a customer an email for example, and there is an error in that view
   (for example, a database error) then this ensures that the email is not
   sent.

4. A :class:`pyramid_mailer.DummyMailer` class to help with writing unit
   tests, or other situations where you want to avoid emails being sent
   accidentally from a non-production install.

**pyramid_mailer** uses the `repoze_sendmail`_ package for general email
sending, queuing and transaction management, and it borrows code from Zed
Shaw's `Lamson`_ library for low-level multipart message encoding and
wrapping.

Pre-Installation
----------------

For local development, a developer has a few options:

1. Include the :mod:`pyramid_mailer.debug` module in your application's
   configuration (see :ref:`debugging`) so mails save to a local file.

2. Run a fake SMTPD server for developing and debugging your webapp. Python
   provides an SMTP server in its standard library called **smtpd**. We can make
   use of it by simply running the following command in a new terminal (this
   example uses port 2525; feel free to change that)::
   
      python -m smtpd -n -c DebuggingServer localhost:2525

3. Use your ISP's mail relay.

4. Ensure an SMTP server is installed and running. This is usually used
   for a production environment. Follow instructions for the appropriate operating
   system:

   **Linux/OSX**
       For Linux users, a common SMTP server to use is Postfix. Most Linux
       distributions carry Postfix, so ensure it is installed and running.
       Ubuntu/Debian users see `Ubuntu's Postfix guide`_. Other Linux users
       can follow the `ArchLinux Postfix guide`_. OSX users can
       check out the `OSX Postfix instructions`_.
   
   **Windows**
      Windows users can use Windows' built-in Internet Information
      Services to `setup an SMTP with IIS`_.

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

Or, in your application's configuration development.ini add::

   pyramid.includes =
      pyramid_mailer
      ...
      pyramid_debugtoolbar
      pyramid_tm

Or, in your application's configuration stanza use the
:meth:`pyramid.config.Configurator.include` method::

   config.include('pyramid_mailer')

Thereafter, the mailer is available via the ``request.mailer`` attribute::

   mailer = request.mailer

To send a message, you must first create a
:class:`~pyramid_mailer.message.Message` instance::

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
:meth:`~pyramid_mailer.mailer.Mailer.send_immediately`::

    mailer.send_immediately(message, fail_silently=False)

This will send the email immediately, without the transaction, so if it fails
you have to deal with it manually. The ``fail_silently`` flag will swallow
any connection errors silently - if it's not important whether the email gets
sent.

Getting Started (The Harder Way)
--------------------------------

To get started the harder way (without using ``config.include``), create an
instance of :class:`pyramid_mailer.mailer.Mailer`::

    from pyramid_mailer.mailer import Mailer

    mailer = Mailer()

The mailer can take a number of optional settings, detailed in
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

If you configure a :class:`~pyramid_mailer.mailer.Mailer` using
:meth:`~pyramid_mailer.mailer.Mailer.from_settings` or via
``config.include('pyramid_mailer')``, you can pass the settings from your
Paste ``.ini`` file.  For example::

  [app:myproject]
  mail.host = localhost
  mail.port = 25

By default, the prefix is assumed to be `mail.`.  If you use the
``config.include`` mechanism, to set another prefix, use the
``pyramid_mailer.prefix`` key in the config file.  For example::

  [app:myproject]
  foo.host = localhost
  foo.port = 25
  pyramid_mailer.prefix = foo.

If you use the :meth:`pyramid_mailer.mailer.Mailer.from_settings` or
:func:`pyramid_mailer.mailer_factory_from_settings` API, these accept a
prefix directly; for example::

  mailer_factory_from_settings(settings, prefix='foo.')

If you don't use Paste, just pass the settings directly into your Pyramid
``Configurator``::

   settings = {'mail.host':'localhost', 'mail.port':'25'}
   Configurator(settings=settings)
   config.include('pyramid_mailer')

The available settings are listed below.

==========================      ====================================            ===============================
Setting                         Default                                         Description
==========================      ====================================            ===============================
**mail.host**                   ``localhost``                                   SMTP host
**mail.port**                   ``25``                                          SMTP port
**mail.username**               **None**                                        SMTP username
**mail.password**               **None**                                        SMTP password
**mail.tls**                    **False**                                       Use TLS
**mail.ssl**                    **False**                                       Use SSL
**mail.keyfile**                **None**                                        SSL key file
**mail.certfile**               **None**                                        SSL certificate file
**mail.queue_path**             **None**                                        Location of maildir
**mail.default_sender**         **None**                                        Default from address
**mail.debug**                  **0**                                           SMTP debug level
**mail.sendmail_app**           **/usr/sbin/sendmail**                          Sendmail executable
**mail.sendmail_template**      **{sendmail_app} -t -i -f {sender}**            Template for sendmail execution
==========================      ====================================            ===============================

**Note:** SSL will only work with **pyramid_mailer** if you are using Python
  **2.6** or higher, as it uses the SSL additions to the ``smtplib``
  package. While it may be possible to work around this if you have to use
  Python 2.5 or lower, **pyramid_mailer** does not support this out of the
  box.

**Note:** the ``mail.debug`` option will be passed to the underlying
``smtplib`` connection. Any values for this option that Python would consider
``> 0`` will result in debug messages for all messages sent and received from
the server. Thus, specifying ``mail.debug`` with any value will result in debug
messages as ``pyramid_mailer`` will not attempt to coerce this value from its
original string.

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

HTML email
--------------------

Below is a recipe how to send templatized HTML and plain text email. 
The email is assembled from three templates: subject, HTML body and text 
body. It is also recommend to use `premailer <https://pypi.python.org/pypi/premailer>`_
Python package to transform email CSS styles to inline CSS, as 
email clients are pretty restricted  what comes to their ability to understand 
CSS.

.. code-block:: python

    from pyramid.renderers import render

    from pyramid_mailer import get_mailer
    from pyramid_mailer.message import Message

    import premailer



    def send_templated_mail(request, recipients, template, context, sender=None):
        """Send out templatized HTML and plain text emails.

        The email is assembled from three different templates:

        * Read subject from a subject specific template $template.subject.txt

        * Generate HTML email from HTML template, $template.body.html

        * Generate plain text email from HTML template, $template.body.txt

        :param request: HTTP request, passed to the template engine. Request configuration is used to get hold of the configured mailer.

        :param recipients: List of recipient emails

        :param template: Template filename base string for template tripled (subject, HTML body, plain text body). For example ``email/my_message`` would map to templates ``email/my_message.subject.txt``, ``email/my_message.body.txt``, ``email/my_message.body.html``

        :param context: Template context variables as a dict

        :param sender: Override the sender email - if not specific use the default set in the config as ``mail.default_sender``
        """

        assert recipients
        assert len(recipients) > 0

        subject = render(template + ".subject.txt", context, request=request)
        subject = subject.strip()

        html_body = render(template + ".body.html", context, request=request)
        text_body = render(template + ".body.txt", context, request=request)

        if not sender:
            sender = request.registry.settings["mail.default_sender"]

        # Inline CSS styles
        html_body = premailer.transform(html_body)

        message = Message(subject=subject, sender=sender, recipients=recipients, body=text_body, html=html_body)

        mailer = get_mailer(request)
        mailer.send(message)


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

A transfer encoding can be specified via the ``transfer_encoding`` option.
Supported options are currently ``quoted-printable`` (default), ``base64``,
``7bit`` and ``8bit``.

You can also pass an attachment as the ``body`` and/or ``html``
arguments to specify ``Content-Transfer-Encoding`` or other
``Attachment`` attributes::

    from pyramid_mailer.message import Attachment
    from pyramid_mailer.message import Message

    body = Attachment(data="hello, arthur",
                      transfer_encoding="quoted-printable")
    html = Attachment(data="<p>hello, arthur</p>",
                      transfer_encoding="quoted-printable")
    message = Message(body=body, html=html)


.. _debugging:

Debugging
---------

If your site is in development and you want to avoid accidental sending of any
emails to customers, but still see what emails would get sent, you can use
``config.include('pyramid_mailer.debug')`` to make the current mailer an
instance of the :class:`pyramid_mailer.mailer.DebugMailer`, hence writing all
emails to a file instead of sending them out. In other words if you add
``pyramid_mailer.debug`` to your development.ini, all emails that would be sent
out will instead get written to files so you can inspect them::

   pyramid.includes =
      pyramid_mailer.debug
      ...
      pyramid_debugtoolbar
      pyramid_tm


Unit tests
----------

When running unit tests you probably don't want to actually send any emails
inadvertently. However it's still useful to keep track of what emails would
be sent in your tests.

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

One can also use the ``DummyMailer`` to keep track of emails sent from a `WebTest`_ functional test.::

    class FunctionalTests(unittest.TestCase):
        def setUp(self):
            from myapp import main
            settings = {'pyramid.includes' : 'pyramid_mailer.testing'}
            app = main({}, **settings)
            from webtest import TestApp
            self.testapp = TestApp(app)

        def test_some_functionality(self):
            res = self.testapp.get('/post_email', status=200)
            registry = self.testapp.app.registry
            mailer = get_mailer(registry)

The ``DummyMailer`` instance keeps track of emails "sent" in two properties:
`queue` for emails send via
:meth:`pyramid_mailer.mailer.Mailer.send_to_queue` and `outbox` for emails
sent via :meth:`pyramid_mailer.mailer.Mailer.send`. Each stores the
individual ``Message`` instances::

    self.assertEqual(len(mailer.outbox), 1)
    self.assertEqual(mailer.outbox[0].subject, "hello world")

    self.assertEqual(len(mailer.queue), 1)
    self.assertEqual(mailer.queue[0].subject, "hello world")

Queue
-----

When you send mail to a queue via
:meth:`pyramid_mailer.mailer.Mailer.send_to_queue`, the mail will be placed
into a ``maildir`` directory specified by the ``queue_path`` parameter or
setting to
:class:`pyramid_mailer.mailer.Mailer`.  A separate process will need to be
launched to monitor this maildir and take actions based on its state.  Such a
program comes as part of `repoze_sendmail`_ (a dependency of the
``pyramid_mailer`` package).  It is known as ``qp``.  ``qp`` will be
installed into your Python (or virtualenv) ``bin`` or ``Scripts`` directory
when you install ``repoze_sendmail``.

``qp`` is a script that is meant to be run as a cron job because what it does
is that it looks at maildir and sends messages. You'll need to arrange
for ``qp`` to be a long-running process that monitors the maildir state.::

  $ bin/qp /path/to/mail/queue

This will attempt to use the localhost SMTP server to send any messages in
the queue over time.  ``qp`` has other options that allow you to choose
different settings.  Use it's ``--help`` parameter to see more::

  $ bin/qp --help

.. note::

   Sending messages via the queue requires the use of a transaction manager.
   If no manager is enabled, it must be emulated by issuing a manual commit
   via ``transaction.commit()``.

   .. code-block:: python

      import transaction
      tx = transaction.begin()
      mailer.send_to_queue(msg)
      try:
          tx.commit()
      except Exception:
          # handle a failed delivery

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
.. _Ubuntu's Postfix guide: https://help.ubuntu.com/lts/serverguide/postfix.html
.. _ArchLinux Postfix guide: https://wiki.archlinux.org/index.php/postfix
.. _OSX Postfix instructions: http://benjaminrojas.net/configuring-postfix-to-
    send-mail-from-mac-os-x-mountain-lion
.. _setup an SMTP with IIS: http://www.neatcomponents.com/enable-SMTP-in-Windows-8
.. _repoze_sendmail: http://pypi.python.org/pypi/repoze.sendmail/
.. _Lamson: http://pypi.python.org/pypi/lamson/
.. _WebTest: http://pypi.python.org/pypi/WebTest/

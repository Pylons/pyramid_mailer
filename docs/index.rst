pyramid_mailer
==================

**pyramid_mailer** is a package for the Pyramid framework to take the pain out of sending emails. It has the following features:

1. A wrapper around the low-level email functionality of standard Python. This includes handling multipart emails with both text and
   HTML content, and file attachments.

2. The option of directly sending an email or adding it to the queue in your maildir.

3. Wrapping email sending in the transaction manager. If you have a view that sends a customer an email for example, and there is an
   error in that view (for example, a database error) then this ensures that the email is not sent.

4. A **DummyMailer** class to help with writing unit tests, or other situations where you want to avoid emails being sent accidentally
   from a non-production install.

**pyramid_mailer** uses the `repoze_sendmail`_ package for general email sending, queuing and transaction management, and the `Lamson`_
library for low-level multipart message encoding and wrapping. You do not have to install or run a Lamson mail service.

Installation
------------

Install using **pip install pyramid_mailer** or **easy_install pyramid_mailer**.

If installing from source, untar/unzip, cd into the directory and do **python setup.py install**.

The source repository is on `Bitbucket`_. Please report any bugs, issues or queries there. 

Getting started
---------------

To get started create an instance of **Mailer**::

    from pyramid_mailer.mailer import Mailer

    mailer = Mailer()

The **Mailer** class can take a number of optional settings, detailed in :ref:`configuration`.. It's a good idea to create a single **Mailer** instance for your application, and add it to your registry in your configuration setup::

    config = Configurator(settings=settings)
    config.registry['mailer'] = Mailer(settings)

You can then access your mailer in a view::

    def my_view(request):
        mailer = request.registry['mailer']

To send a message, you must first create a **Message** instance::

    from pyramid.mailer.message import Message

    message = Message(subject="hello world",
                      sender="admin@mysite.com",
                      recipients=["arthur.dent@gmail.com"],
                      body="hello, arthur")

The **Message** is then passed to the **Mailer** instance. You can either send the message right away::

    mailer.send(message)

or add it to your mail queue::

    mailer.send_to_queue(message)

.. _configuration:

Configuration
-------------

+--------------------------+-------------------+--------------------------+
| Setting                  | Default           | Description              | 
+=====================================+===================================+
| **mail.host**            | ``localhost``     | SMTP host                |
+--------------------------+-------------------+--------------------------+
| **mail.port**            | ``25``            | SMTP port                |
+--------------------------+-------------------+--------------------------+
| **mail.username**        | **None**          | SMTP username            |
+--------------------------+-------------------+--------------------------+
| **mail.password**        | **None**          | SMTP password            |
+--------------------------+-------------------+--------------------------+
| **mail.tls**             | **False**         | Use TLS                  |
+--------------------------+-------------------+--------------------------+
| **mail.ssl**             | **False**         | Use SSL                  |
+--------------------------+-------------------+--------------------------+
| **mail.keyfile**         | **None**          | SSL key file             |
+--------------------------+-------------------+--------------------------+
| **mail.certfile**        | **None**          | SSL certificate file     |
+--------------------------+-------------------+--------------------------+
| **mail.queue_path**      | **None**          | Location of maildir      |
| **mail.queue_path**      | **None**          | Location of maildir      |
+--------------------------+-------------------+--------------------------+
| **mail.default_sender**  | **None**          | Default from address     |
+--------------------------+-------------------+--------------------------+
| **mail.debug**           | **False**         | SMTP debug level         |
+-------------------------------------------------------------------------+

Transactions
------------

Attachments
-----------


Unit tests
----------

When running unit tests you probably don't want to actually send any emails inadvertently. However it's still useful to keep track of what emails would be sent in your tests. 

Another case is if your site is in development and you want to avoid accidental sending of any emails to customers.

In either case, the **DummyMailer** can be used::

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

The **DummyMailer** instance keeps track of emails "sent" in two properties: `queue` for emails send via **send_to_queue()** and `outbox` for emails sent via **send()**. Each stores the individual **Message** instances::

    self.assertEqual(len(mailer.outbox) == 1)
    self.assertEqual(mailer.outbox[0].subject == "hello world")

    self.assertEqual(len(mailer.queue) == 1)
    self.assertEqual(mailer.queue[0].subject == "hello world")

        
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

.. module:: pyramid_mailer.interfaces

.. autoclass:: IMailer
   :members:

.. autoclass:: IMessage
   :members:

.. autoclass:: IAttachment
   :members:

.. _Bitbucket: http://bitbucket.org/danjac/pyramid_mailer
.. _Pyramid: http://pypi.python.org/pypi/pyramid/
.. _repoze_sendmail: http://pypi.python.org/pypi/repoze_sendmail/
.. _Lamson: http://pypi.python.org/pypi/lamson/

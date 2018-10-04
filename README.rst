``pyramid_mailer``
==================

.. image:: https://travis-ci.org/Pylons/pyramid_mailer.png?branch=master
   :target: https://travis-ci.org/Pylons/pyramid_mailer

.. image:: https://readthedocs.org/projects/pyramid_mailer/badge/?version=latest
   :target: https://docs.pylonsproject.org/projects/pyramid_mailer/en/latest/
   :alt: Documentation Status

pyramid_mailer is a package for sending email from your Pyramid application.
It is compatible with Python 2.7, 3.4, 3.5, 3.6, and 3.7 as well as PyPy.

This package includes:

1. Wrapping the low-level Python ``email`` library with an easy-to-use
   API, which includes attachments and mulipart content.

2. Sending emails immediately or add to a ``maildir`` queue.

3. Managing email sends inside a transaction, to prevent emails being sent
   if your code raises an exception.

4. Features to help with unit testing.

``pyramid_mailer`` uses the ``repoze.sendmail`` library for managing email
sending and transacton management, and borrows code (with permission) from
Zed Shaw's `lamson <https://github.com/zedshaw/lamson>`_  for wrapping email
messages.  See the ``LICENSE.txt`` file for more information.

Links
-----

- `documentation
  <https://docs.pylonsproject.org/projects/pyramid_mailer/en/latest/>`_

- `code repository
  <https://github.com/Pylons/pyramid_mailer>`_

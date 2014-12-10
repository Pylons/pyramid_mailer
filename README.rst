``pyramid_mailer``
==================

pyramid_mailer is a package for sending email from your Pyramid application.
It is compatible with Python 2.6. 2.7, 3.2, 3.3, and 3.4, as well as PyPy
and PyPy3.

This package includes:

1. Wrapping the low-level Python ``email`` library with an easy-to-use
   API, which includes attachments and mulipart content.

2. Send emails immediately or to add to a maildir queue.

3. Managing email sends inside a transaction, to prevent emails being sent
   if your code raises an exception.

4. Features to help with unit testing.

``pyramid_mailer`` uses the ``repoze.sendmail`` library for managing email
sending and transacton management, and borrows code (with permission) from
Zed Shaw's ``lamson`` for wrapping email messages (http://lamsonproject.org/).
See the LICENSE.txt file for more information.

Links
-----

- `documentation
  <http://docs.pylonsproject.org/projects/pyramid_mailer/en/latest/>`_

- `development version
  <https://github.com/Pylons/pyramid_mailer>`_

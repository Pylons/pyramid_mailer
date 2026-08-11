Change History
==============

.. _vunreleased:

unreleased
----------

- Bring repo up to Pylons Project standards.
  See https://github.com/Pylons/pyramid_mailer/pull/89

- Optionally include bcc information on send.
  See https://github.com/Pylons/pyramid_mailer/pull/87
  
- Rename "master" to "main"

.. _v0.15.1:

0.15.1 (2016-12-13)
-------------------

- Add the new ``.bind`` method to the ``DebugMailer`` and the
  ``DummyMailer``. Also ``pyramid_mailer.testing`` and
  ``pyramid_mailer.debug`` now add the ``request.mailer`` request attribute.
  https://github.com/Pylons/pyramid_mailer/pull/83


.. _v0.15:

0.15 (2016-12-06)
-----------------

- Support '7bit' and '8bit' transfer-encoding.
  https://github.com/Pylons/pyramid_mailer/pull/49

- If ``username`` and ``password`` are both set to the empty string,
  ``Mailer.from_settings``, now interprets them as being set to ``None``.
  Previously, setting them to the empty string caused SMTP authentication
  to be force with empty username and password.
  https://github.com/Pylons/pyramid_mailer/pull/70

- Add a ``content_id`` argument to the ``Attachment`` constructor
  which allows you to set the Content-ID header so you can reference it from
  an HTML body.
  https://github.com/Pylons/pyramid_mailer/pull/71

- Change file extension to ``.eml`` for mails saved from
  ``DebugMailer``. ``.eml`` is the standard file format for storing
  plaintext MIME (rfc822) emails.
  https://github.com/Pylons/pyramid_mailer/pull/72

- Drop Python 2.6 and 3.2 support.
  https://github.com/Pylons/pyramid_mailer/pull/77

- Add Python 3.5 support.

- Support per-request transaction managers if available via
  ``request.tm`` set by ``pyramid_tm``.
  https://github.com/Pylons/pyramid_mailer/pull/78


.. _v0.14.1:

0.14.1 (2015-05-21)
-------------------

- Enable compatibility testing with Pyramid all the way back to 1.2. It may
  work earlier but we aren't testing it any longer.

- Fix a bug where the ``mailer.debug`` ini option was not properly being
  cast to an ``int``. This did not show up on Python 2 because string
  to int comparisons are valid there but it was a latent bug.
  See https://github.com/Pylons/pyramid_mailer/pull/68


.. _v0.14:

0.14 (2014-12-10)
-----------------

- Added support for Python3.4, PyPy3.

- Ensure that ``DebugMailer`` emulates ``Mailer`` by generating
  a sender if none is passed.
  https://github.com/Pylons/pyramid_mailer/pull/56

- Add configuration options for ``mail.sendmail_app`` and
  ``mail.sendmail_template`` to allow use with non-default sendmail
  configurations.
  https://github.com/Pylons/pyramid_mailer/pull/52

- Add ``pyramid_mailer.debug`` shorthand:  via one line in
  ``development.ini``, enables writing emails to a file instead of sending
  them.
  https://github.com/Pylons/pyramid_mailer/pull/50


.. _v0.13:

0.13 (2013-07-13)
-----------------

- Default transfer encoding for mail messages is now
  'quoted-printable'.
  https://github.com/Pylons/pyramid_mailer/pull/45


.. _v0.12:

0.12 (2013-06-26)
-----------------

- Added support for sendmail binary via repoze.sendmail >= 4.0b2.
  https://github.com/Pylons/pyramid_mailer/pull/35

- Remove "all_parts" and "attach_all_parts" from MailResponse object (unused by
  pyramid_mailer).

- The Attachment class no longer supports reading data from the a file based on
  the ``filename`` it is passed.  Instead, use the filename argument only as
  something that should go in the Content-Disposition header, and pass a
  filelike object as ``data``.

- Major code overhaul: nonascii attachment sending now actually works, most of
  the code stolen from Lamson was gutted and replaced.

- Requires repoze.sendmail >= 4.1


.. _v0.11:

0.11 (2013-03-28)
-----------------

- Allow setting Content-Transfer-Encoding for body and html
  via Attachments.
  https://github.com/Pylons/pyramid_mailer/issues/29

- Fix handling of messages with both HTML and plain text
  bodies that also have attachments.
  https://github.com/Pylons/pyramid_mailer/issues/32

- ensure that ``pyramid_mailer.response.to_message`` returns
  text under Python 3.x.
  https://github.com/Pylons/pyramid_mailer/issues/24

- Dropped support for Python 2.5.


.. _v0.10:

0.10 (2012-11-22)
-----------------

- Set default transfer encoding for attachments to ``base64`` and allow
  an optional ``transfer_encoding`` argument for attachments. This currently
  supports ``base64`` or ``quoted-printable``.

- Properly handle ``Mailer.from_settings`` boolean options including ``tls``
  and ``ssl``.

- Support ``setup.py dev`` (installs testing dependencies).

- Use ``setup.py dev`` in tox.ini.


.. _v0.9:

0.9 (2012-05-03)
----------------

- Add a test for uncode encoding in multipart messages.

- Depend on ``repoze.sendmail`` >= 3.2 (fixes unicode multipart message
  encoding).


.. _v0.8:

0.8 (2012-03-26)
----------------

- Work around a Python 3.2.0 bug in handling emails with empty headers.  This
  allows cc-only and bcc-only emails to be handled properly on all platforms
  (no recipient= required anymore).  See
  https://github.com/Pylons/pyramid_mailer/issues/14.


.. _v0.7:

0.7 (2012-03-26)
----------------

- Packaging release


.. _v0.7dev:

0.7dev (2012-03-20)
-------------------

- Python 2.5, 2.6, 2.7, 3.2, and pypy compatibility.

- Remove explicit Jython support.  It may work, but we no longer test it
  using automated testing.

- Requires repoze.sendmail 3.0+.

- More descriptive exception raised when attempting to send cc-only or
  bcc-only messages.  See https://github.com/Pylons/pyramid_mailer/issues/14


.. _v0.6:

0.6 (2012-01-22)
----------------

- Use ',' as an email header field separator rather than ';' when multiple
  values are in the same header (as per RFC822).

- Allow lists of recipient emails to be tuples or lists (previously it was
  just lists).

- Don't include ``Bcc`` header in mail messages (breaks secrecy of BCC).
  See https://github.com/Pylons/pyramid_mailer/pull/10


.. _v0.5.1:

0.5.1 (2011-11-13)
------------------

- Fixed a bug where the mailer was only sending email to addresses in
  the "TO" field.


.. _v0.5:

0.5 (2011-10-24)
----------------

- Drop Lamson dependency by copying Lamson's MailResponse and dependent code
  into ``pyramid_mailer.response``.


.. _v0.4.x:

0.4.X
-----

- ``pyramid_mailer.includeme`` function added for
  ``config.include('pyramid_mailer')`` support

- ``pyramid_mailer.testing`` module added for
  ``config.include('pyramid_mailer.testing')`` support.

- ``pyramid_mailer.get_mailer`` API added (see docs).

- ``pyramid_mailer.interfaces`` module readded (with marker IMailer interface
  for ZCA registration).

- ``setup.cfg`` added with coverage parameters to allow for ``setup.py
  nosetests --with-coverage``.

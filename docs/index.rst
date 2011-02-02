pyramid_mailer
==================

Installation
------------

Install using **pip install pyramid_mailer** or **easy_install pyramid_mailer**.

If installing from source, untar/unzip, cd into the directory and do **python setup.py install**.

The source repository is on `Bitbucket`_. Please report any bugs, issues or queries there. 

Getting started
---------------

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
.. _repoze.sendmail: http://pypi.python.org/pypi/repoze_sendmail/
.. _Lamson: http://pypi.python.org/pypi/lamson/

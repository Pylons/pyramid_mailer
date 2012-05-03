"""
pyramid_mailer is a package for taking the pain out of sending emails in your
Pyramid project.  It is compatible with Python 2.5, 2.6, 2.7, and 3.2.

This includes:

1. Wrapping the low-level Python email library with an easy-to-use
   API, which includes attachments and mulipart content.

2. Send emails immediately or to add to a maildir queue.

3. Managing email sends inside a transaction, to prevent emails being sent
   if your code fails.

4. Features to help with unit testing.

pyramid_mailer uses the repoze_sendmail library for managing email sending
and transacton management, and borrows code from Zed Shaw's Lamson for
wrapping email messages.

Links
`````

* `documentation
  <http://docs.pylonsproject.org/projects/pyramid_mailer/en/latest/>`_
* `development version
  <https://github.com/Pylons/pyramid_mailer>`_

"""

from setuptools import setup


setup(
    name='pyramid_mailer',
    version='0.9',
    license='BSD',
    author='Dan Jacob',
    author_email='danjac354@gmail.com',
    description='Sendmail package for Pyramid',
    long_description=__doc__,
    url="http://docs.pylonsproject.org/projects/pyramid_mailer/en/latest/",
    packages=[
        'pyramid_mailer',
    ],
    zip_safe=False,
    platforms='any',
    install_requires=[
        'pyramid',
        'repoze.sendmail>=3.2dev',
    ],
    test_suite='pyramid_mailer',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        "Topic :: Communications :: Email",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.5",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Framework :: Pyramid",
    ]
)

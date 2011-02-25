"""
pyramid_mailer is a package for taking the pain out of sending emails
in your Pyramid project.

This includes:

1. Wrapping the low-level Python email library with an easy-to-use
   API, which includes attachments and mulipart content.

2. Send emails immediately or to add to a maildir queue.

3. Managing email sends inside a transaction, to prevent emails being sent
   if your code fails.

4. Features to help with unit testing.

pyramid_mailer uses the repoze_sendmail library for managing email sending
and transacton management, and Lamson for wrapping email messages. You do
not need to install a Lamson service to use pyramid_mailer.

Links
`````

* `documentation <http://packages.python.org/pyramid_mailer/>`_
* `development version
  <http://bitbucket.org/danjac/pyramid_mailer/get/tip.gz#egg=pyramid_mailer>`_

"""

from setuptools import setup


setup(
    name='pyramid_mailer',
    version='0.2.3',
    license='BSD',
    author='Dan Jacob',
    author_email='danjac354@gmail.com',
    description='Sendmail package for Pyramid',
    long_description=__doc__,
    packages=[
        'pyramid_mailer',
    ],
    test_suite='nose.collector',
    zip_safe=False,
    platforms='any',
    install_requires=[
        'pyramid',
        'Lamson',
        'repoze.sendmail',
    ],
    tests_require=[
        'nose',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)

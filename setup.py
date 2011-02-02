from setuptools import setup


setup(
    name='pyramid_mailer',
    version='0.1',
    url='',
    license='BSD',
    author='Dan Jacob',
    author_email='danjac354@gmail.com',
    description='',
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

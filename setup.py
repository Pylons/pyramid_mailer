from setuptools import setup

docs_extras = [
    'Sphinx',
    'docutils',
    'repoze.sphinx.autointerface',
    ]

tests_require = []

testing_extras = tests_require + [
    'nose',
    'coverage',
    ]

with open('README.rst') as f:
    README = f.read()

with open('CHANGES.rst') as f:
    CHANGES = f.read()

setup(
    name='pyramid_mailer',
    version='0.14',
    license='BSD',
    author='Dan Jacob',
    author_email='danjac354@gmail.com',
    description='Sendmail package for Pyramid',
    long_description='\n\n'.join([README, CHANGES]),
    url="http://docs.pylonsproject.org/projects/pyramid_mailer/en/latest/",
    packages=[
        'pyramid_mailer',
    ],
    zip_safe=False,
    platforms='any',
    install_requires=[
        'pyramid',
        'repoze.sendmail>=4.1',
    ],
    tests_require = tests_require,
    extras_require = {
        'testing':testing_extras,
        'docs':docs_extras,
        },
    test_suite='pyramid_mailer',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        "Topic :: Communications :: Email",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Framework :: Pyramid",
    ]
)

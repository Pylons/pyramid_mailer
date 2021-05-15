from setuptools import setup

docs_extras = [
    'Sphinx >= 1.8.1',
    'docutils',
    'repoze.sphinx.autointerface',
    'pylons-sphinx-themes >= 1.0.10',
    ]

tests_require = []

testing_extras = tests_require + [
    'nose',
    'coverage',
    'WebTest',
    ]

try:
    with open('README.rst') as f:
        README = f.read()

    with open('CHANGES.rst') as f:
        CHANGES = f.read()

except IOError:
    README = ''
    CHANGES = ''

setup(
    name='pyramid_mailer',
    version='0.15.1',
    license='BSD',
    author='Dan Jacob',
    author_email='danjac354@gmail.com',
    description='Sendmail package for Pyramid',
    long_description='\n\n'.join([README, CHANGES]),
    url="https://docs.pylonsproject.org/projects/pyramid-mailer/en/latest/",
    packages=[
        'pyramid_mailer',
    ],
    zip_safe=False,
    platforms='any',
    install_requires=[
        'pyramid',
        'repoze.sendmail>=4.1',
        'transaction',
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
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Framework :: Pyramid",
    ]
)

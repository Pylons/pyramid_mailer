# Contributing

All projects under the Pylons Project, including this one, follow the guidelines established at [How to Contribute](https://pylonsproject.org/community-how-to-contribute.html), [Coding Style and Standards](https://pylonsproject.org/community-coding-style-standards.html), and [Pylons Project Documentation Style Guide](https://docs.pylonsproject.org/projects/pyramid_mailer/).

You can contribute to this project in several ways.

*   [File an Issue on GitHub](https://github.com/Pylons/pyramid_mailer/issues)
*   Fork this project, create a new branch, commit your suggested change, and push to your fork on GitHub.
    When ready, submit a pull request for consideration.
    [GitHub Flow](https://guides.github.com/introduction/flow/index.html) describes the workflow process and why it's a good practice.
    When submitting a pull request, sign [CONTRIBUTORS.txt](https://github.com/Pylons/pyramid_mailer/blob/master/CONTRIBUTORS.txt) if you have not yet done so.
*   Join the [IRC channel #pyramid on irc.freenode.net](https://webchat.freenode.net/?channels=pyramid).

## Git Branches

Git branches and their purpose and status at the time of this writing are listed below.

*   [master](https://github.com/Pylons/pyramid_mailer/) - The branch which should always be *deployable*. The default branch on GitHub.
*   For development, create a new branch. If changes on your new branch are accepted, they will be merged into the master branch and deployed.

## Running tests and building documentation

We use [tox](https://tox.readthedocs.io/en/latest/) to automate test running, coverage, and building documentation across all supported Python versions.

To run everything configured in the `tox.ini` file:

    $ tox

To run tests on Python 2 and 3, and ensure full coverage, but exclude building of docs:

    $ tox -e py2-cover,py3-cover,coverage

To build the docs only:

    $ tox -e docs

See the `tox.ini` file for details.

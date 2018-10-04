import sys

PY2 = sys.version_info[0] < 3

try:
    text_type = unicode
except NameError:
    text_type = str

if PY2:
    from StringIO import StringIO
else:
    from io import StringIO

try:
    from smtplib import SMTP_SSL
except ImportError:  # pragma: no cover
    SMTP_SSL = None

if PY2:
    # this works in Py2
    from email.encoders import _qencode

    def string_to_unicode(text, encoding='utf-8'):
        """
        This will upgrade a Py2 ``string`` to a ``unicode`` object, preferably in `UTF-8`.
        This is necessary for the proper escaping to happen on ``Subject`` and ``Body``.
        """
        if isinstance(text, bytes):
            try:
                # ascii in, ascii out
                return text.decode('ascii')
            except UnicodeDecodeError:
                return text.decode(encoding)
        return text

else:
    # but they are broken in Py3 (_qencode was not ported properly and
    # still wants to use str instead of bytes to do space replacement)
    import quopri
    def _qencode(s):
        enc = quopri.encodestring(s, quotetabs=True)
        # Must encode spaces, which quopri.encodestring() doesn't do
        return enc.replace(b' ', b'=20')

    def string_to_unicode(text, encoding='utf-8'):
        """only necessary for Py2"""
        return text

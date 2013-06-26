import sys

PY2 = sys.version < '3'

try: # pragma: no cover
    text_type = unicode
except NameError: # pragma: no cover
    text_type = str


if sys.version < '3': # pragma: no cover
    def is_nonstr_iter(v): 
        return hasattr(v, '__iter__')
else: # pragma: no cover
    def is_nonstr_iter(v):  # pragma: no cover
        if isinstance(v, str):
            return False
        return hasattr(v, '__iter__')

    
try: # pragma: no cover
    from io import StringIO
except ImportError:  # pragma: no cover
    from StringIO import StringIO

try:
    from smtplib import SMTP_SSL
except ImportError:  # pragma: no cover
    SMTP_SSL = None

if PY2:
    # this works in Py2
    from email.encoders import _qencode

else: # pragma: no cover
    # but they are broken in Py3 (_qencode was not ported properly and
    # still wants to use str instead of bytes to do space replacement)
    import quopri
    def _qencode(s):
        enc = quopri.encodestring(s, quotetabs=True)
        # Must encode spaces, which quopri.encodestring() doesn't do
        return enc.replace(b' ', b'=20')


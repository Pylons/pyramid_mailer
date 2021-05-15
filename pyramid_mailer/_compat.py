import quopri


try:
    from smtplib import SMTP_SSL
except ImportError:  # pragma: no cover
    SMTP_SSL = None


# Patch broken _qencode in Py3 (_qencode was not ported properly and
# still wants to use str instead of bytes to do space replacement)
def _qencode(s):
    enc = quopri.encodestring(s, quotetabs=True)
    # Must encode spaces, which quopri.encodestring() doesn't do
    return enc.replace(b' ', b'=20')

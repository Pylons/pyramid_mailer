import sys

try: # pragma: no cover
    from base64 import encodestring as base64_encodestring
    # pyflakes
    base64_encodestring  # pragma: no cover
except ImportError: # pragma: no cover
    # BBB Python 2 compat
    from base64 import encodestring as base64_encodestring
    base64_encodestring # pyflakes

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


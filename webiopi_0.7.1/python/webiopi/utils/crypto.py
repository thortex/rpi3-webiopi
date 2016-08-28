import base64
import hashlib
from webiopi.utils.version import PYTHON_MAJOR

def encodeCredentials(login, password):
    abcd = "%s:%s" % (login, password)
    if PYTHON_MAJOR >= 3:
        b = base64.b64encode(abcd.encode())
    else:
        b = base64.b64encode(abcd)
    return b

def encrypt(value):
    return hashlib.sha256(value).hexdigest()

def encryptCredentials(login, password):
    return encrypt(encodeCredentials(login, password))

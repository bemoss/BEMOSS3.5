__author__ =  "BEMOSS Team"

from Crypto.Cipher import AES
from Crypto import Random
import base64
from django_web_server import settings_tornado

MASTER_KEY = settings_tornado.SECRET_KEY


def encrypt_value(clear_text):
    enc_secret = AES.new(MASTER_KEY[:32], AES.MODE_ECB)
    tag_string = (str(clear_text) +
                  (AES.block_size -
                   len(str(clear_text)) % AES.block_size) * "\0")
    cipher_text = base64.b64encode(enc_secret.encrypt(tag_string))
    return cipher_text


def decrypt_value(cipher_text):
    dec_secret = AES.new(MASTER_KEY[:32], AES.MODE_ECB)
    raw_decrypted = dec_secret.decrypt(base64.b64decode(cipher_text))
    # After you decrypt, strip the null characters:
    clear_text = raw_decrypted.rstrip("\0")
    return clear_text


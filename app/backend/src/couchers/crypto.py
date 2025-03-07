import functools
import secrets
from base64 import urlsafe_b64decode, urlsafe_b64encode
from typing import Optional

import nacl.pwhash
from nacl.bindings import crypto_aead
from nacl.bindings.crypto_generichash import generichash_blake2b_salt_personal
from nacl.bindings.utils import sodium_memcmp
from nacl.exceptions import InvalidkeyError
from nacl.utils import random as random_bytes

from couchers.config import config


def b64encode(data: bytes) -> str:
    return urlsafe_b64encode(data).decode("ascii")


def b64decode(data: str) -> bytes:
    return urlsafe_b64decode(data)


def urlsafe_random_bytes(length=32) -> str:
    return b64encode(random_bytes(length))


def urlsafe_secure_token():
    """
    A cryptographically secure random token that can be put in a URL
    """
    return urlsafe_random_bytes(32)


def cookiesafe_secure_token():
    return random_hex(32)


def hash_password(password: str):
    return nacl.pwhash.str(password.encode("utf-8"))


def verify_password(hashed: bytes, password: str):
    try:
        correct = nacl.pwhash.verify(hashed, password.encode("utf-8"))
        return correct
    except InvalidkeyError:
        return False


def random_hex(length=32):
    """
    Length in binary
    """
    return random_bytes(length).hex()


def secure_compare(val1, val2):
    return sodium_memcmp(val1, val2)


def generate_hash_signature(message: bytes, key: bytes) -> bytes:
    """
    Computes a blake2b keyed hash for the message.

    This can be used as a fast yet secure symmetric signature: by checking that
    the hashes agree, we can make sure the signature was generated by a party
    with knowledge of the key.
    """
    return generichash_blake2b_salt_personal(message, key=key, digest_size=32)


def verify_hash_signature(message: bytes, key: bytes, sig: bytes) -> bool:
    """
    Verifies a hash signature generated with generate_hash_signature.

    Returns true if the signature matches, otherwise false.
    """
    return secure_compare(sig, generate_hash_signature(message, key))


def generate_random_5digit_string():
    """Return a random 5-digit string"""
    return "%05d" % secrets.randbelow(100000)


def verify_token(a: str, b: str):
    """Return True if strings a and b are equal, in such a way as to
    reduce the risk of timing attacks.
    """
    return secrets.compare_digest(a, b)


@functools.lru_cache
def get_secret(name: str):
    """
    Derives a secret key from the root secret using a key derivation function
    """
    return generate_hash_signature(name.encode("utf8"), config["SECRET"])


UNSUBSCRIBE_KEY_NAME = "unsubscribe"
PAGE_TOKEN_KEY_NAME = "pagination"


# AEAD: Authenticated Encryption with Associated Data

_aead_key_len = crypto_aead.crypto_aead_xchacha20poly1305_ietf_KEYBYTES
_aead_nonce_len = crypto_aead.crypto_aead_xchacha20poly1305_ietf_NPUBBYTES


def aead_generate_nonce():
    return random_bytes(_aead_nonce_len)


def aead_generate_key():
    return random_bytes(_aead_key_len)


def aead_encrypt(key: bytes, secret_data: bytes, plaintext_data: bytes = b"", nonce: Optional[bytes] = None) -> bytes:
    if not nonce:
        nonce = aead_generate_nonce()
    encrypted = crypto_aead.crypto_aead_xchacha20poly1305_ietf_encrypt(secret_data, plaintext_data, nonce, key)
    return nonce, encrypted


def aead_decrypt(key: bytes, nonce: bytes, encrypted_secret_data: bytes, plaintext_data: bytes = b"") -> bytes:
    return crypto_aead.crypto_aead_xchacha20poly1305_ietf_decrypt(encrypted_secret_data, plaintext_data, nonce, key)


def simple_encrypt(key_name: str, data: bytes) -> bytes:
    key = get_secret(key_name)
    nonce, data = aead_encrypt(key, data)
    return nonce + data


def simple_decrypt(key_name: str, data: bytes) -> bytes:
    key = get_secret(key_name)
    nonce, data = data[:_aead_nonce_len], data[_aead_nonce_len:]
    return aead_decrypt(key, nonce, data)


def encrypt_page_token(plaintext_page_token: str):
    return b64encode(simple_encrypt(PAGE_TOKEN_KEY_NAME, plaintext_page_token.encode("utf8")))


def decrypt_page_token(encrypted_page_token: str):
    return simple_decrypt(PAGE_TOKEN_KEY_NAME, b64decode(encrypted_page_token)).decode("utf8")

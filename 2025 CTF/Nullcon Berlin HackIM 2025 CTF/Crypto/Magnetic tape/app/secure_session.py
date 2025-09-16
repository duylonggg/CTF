import base64, binascii
import logging
import os

from flask.sessions import SessionMixin, SessionInterface
from flask import Flask, Response, Request

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from universalCRC import crc
from random import SystemRandom

import json

_logger = logging.getLogger(__name__)

class CustomSession(dict, SessionMixin):
    pass

class CustomSessionInterface(SessionInterface):

    _KEY_LENGTH = 32
    _BLOCK_LENGTH = 16
    _IV_LENGTH = _BLOCK_LENGTH
    _MAC_LENGTH = 8
    _POLY = [  # from the ECMA-182 standard
        62, 57, 55, 54, 53, 52, 47, 46, 45, 40, 39, 38, 37, 35, 33, 32, 31, 29,
        27, 24, 23, 22, 21, 19, 17, 13, 12, 10, 9, 7, 4, 1, 0,
    ]
    _POLY = sum(1 << d for d in _POLY)

    def __init__(self, key=None):
        self._random_generator = SystemRandom()
        if key is None:
            key = os.getenv("SECURE_SESSION_KEY")
        if key is None:
            key = self._random_generator.randbytes(self._KEY_LENGTH)
        else:
            key = base64.b64decode(key)
        self._key = key

    def open_session(self, app: Flask, request: Request):
        cookie = request.cookies.get(app.config["SESSION_COOKIE_NAME"])
        if cookie is None:
            return CustomSession()
        try:
            session_data = base64.b64decode(cookie)
            data = self._decrypt(session_data).decode("utf-8")
            return CustomSession(json.loads(data))
        except Exception as e:
            _logger.warning("failed to load session data: {}".format(e))
            return CustomSession()

    def save_session(
        self, app: Flask, session: SessionMixin, response: Response
    ) -> None:
        session_data = json.dumps(dict(session))
        data = self._encrypt(session_data.encode("utf-8"))
        response.set_cookie(app.config["SESSION_COOKIE_NAME"], base64.b64encode(data).decode("ascii"))

    def _encrypt(self, data: bytes):
        nonce = self._random_generator.randbytes(self._IV_LENGTH)
        cipher = Cipher(algorithms.AES(self._key), modes.CTR(nonce))
        encryptor = cipher.encryptor()
        mac = self._crc64(data)
        return nonce + encryptor.update(data + mac) + encryptor.finalize()

    def _decrypt(self, data: bytes):
        minimum_ciphertext_length = self._IV_LENGTH + self._MAC_LENGTH
        if len(data) < minimum_ciphertext_length:
            raise ValueError("ciphertext too short to decrypt, was {} bytes, at least {} required".format(
                len(data),
                minimum_ciphertext_length
            ))

        iv = data[0:self._IV_LENGTH]
        data = data[self._IV_LENGTH:]

        cipher = Cipher(algorithms.AES(self._key), modes.CTR(iv))
        decryptor = cipher.decryptor()
        data = decryptor.update(data) + decryptor.finalize()

        assert len(data) > self._MAC_LENGTH

        transmitted_mac = data[-self._MAC_LENGTH:]
        data = data[:-self._MAC_LENGTH]
        mac_of_received_data = self._crc64(data)
        if mac_of_received_data != transmitted_mac:
            raise ValueError("decryption failed: invalid MAC. Most likely someone has tampered with the transmitted data.")

        return data

    def _crc64(self, data):
        check_value = crc.compute_CRC(binascii.hexlify(data).decode("ascii"), self._POLY, 0, 0, 64, False, False)
        return check_value.to_bytes(8, "big")
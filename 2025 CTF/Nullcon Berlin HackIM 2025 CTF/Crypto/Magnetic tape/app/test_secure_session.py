import unittest

from secure_session import CustomSessionInterface


class SecureSessionTest(unittest.TestCase):

    def test_encryption_decryption(self):
        interface = CustomSessionInterface()
        data = b"ABC"
        ciphertext = interface._encrypt(data)
        self.assertIsInstance(ciphertext, bytes)
        recovered_plaintext = interface._decrypt(ciphertext)
        self.assertIsInstance(recovered_plaintext, bytes)
        self.assertEqual(data, recovered_plaintext)

    def test_modified_ciphertext_raises_error(self):
        interface = CustomSessionInterface()
        data = b"ASDFASDF"
        ciphertext = interface._encrypt(data)
        self.assertIsInstance(ciphertext, bytes)
        for i in range(len(ciphertext)):
            for j in range(8):
                modified_ciphertext = bytearray(ciphertext)
                modified_ciphertext[i] ^= 1 << j
                with self.assertRaises(ValueError):
                    interface._decrypt(modified_ciphertext)

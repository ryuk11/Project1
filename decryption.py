#!/usr/bin/env python3
"""
This is a script to encrypt a message using AES and then decrypt it
Before running it, you must install pycryptodome
"""

from base64 import b64decode

from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

from app import application


class Decryption:
    """ Decryption class """

    def __init__(self):
        """ Constructor """
        self.key_value = '7061737323313233'.encode('utf-8')
        self.iv_value = '7061737323313233'.encode('utf-8')
        self.cipher = None

    def decrypt(self, data):
        """
        Decrypt the data input value
        :param data: input to be decrypted
        :return: decrypted value - str
        """

        try:
            raw = b64decode(data)
            self.cipher = AES.new(self.key_value, AES.MODE_CBC, self.iv_value)
            return unpad(self.cipher.decrypt(raw), 16)
        except Exception as exp_msg:
            application.logger.error(str(exp_msg))


if __name__ == '__main__':
    CTE = "HDGV/yHTUWFDs/JCz+e84A=="
    PWD = ""
    print('Message...:', Decryption().decrypt(CTE).decode('utf-8'))

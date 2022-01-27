from base64 import b64encode, b64decode
from Crypto.Cipher import AES
from Crypto.Hash import SHA3_512


class Crypto:

    HEADER_LENGTH = 10

    password1 = "2264f508168da64354b7dd7355efab1f6268aac77805f82970fb63e5ca7a25fcf5954d306e13dc5703210f63b7574f67cd7875f20ec39cbbc10a8291c4f0d1b1"
    password2 = "f1e99a3f9de2b96beda7cb409522d713a49d1bcad5d315f31b0672191b5bfbc73bfdce59547dfc31870494a3a281ebfbee12f4832bfb47edaee9c2e90c2cf6dc"
    password3 = "256e3bad83a9a6ab99a3895f84e3723afa9fc4ff60463844f2b6e4ad9bfb37deade8715a61d49bd43c14781b0359f709cc3bad84e680299b7ea92f48a435141c"

    def __init__(self):

        hash = SHA3_512.new()
        hash.update(self.password1.encode('utf-8'))
        self.key1 = hash.digest()[:32]

        hash = SHA3_512.new()
        hash.update(self.password2.encode('utf-8'))
        self.key2 = hash.digest()[:32]

        hash = SHA3_512.new()
        hash.update(self.password3.encode('utf-8'))
        self.key3 = hash.digest()[:32]

    def get_key1(self):
        return self.key1

    def get_key2(self):
        return self.key2

    def get_key3(self):
        return self.key3

    def encrypt(self, message):
        key = self.get_key1()
        cipher = AES.new(key, AES.MODE_CTR)
        ct_bytes = cipher.encrypt(message.encode('utf-8'))

        message = b64encode(cipher.nonce).decode(
            'utf-8') + b64encode(ct_bytes).decode('utf-8')
        key = self.get_key2()
        cipher = AES.new(key, AES.MODE_CTR)
        ct_bytes = cipher.encrypt(message.encode('utf-8'))

        message = b64encode(cipher.nonce).decode(
            'utf-8') + b64encode(ct_bytes).decode('utf-8')
        key = self.get_key3()
        cipher = AES.new(key, AES.MODE_CTR)
        ct_bytes = cipher.encrypt(message.encode('utf-8'))

        ct = b64encode(ct_bytes)
        return b64encode(cipher.nonce).decode('utf-8') + ct.decode('utf-8')

    def decrypt(self, message):

        # try:
        key = self.get_key3()
        nonce = b64decode(message[:12].encode('utf-8'))
        ct = b64decode(message[12:].encode('utf-8'))
        cipher = AES.new(key, AES.MODE_CTR, nonce=nonce)
        pt = cipher.decrypt(ct)

        message = pt.decode('utf-8')
        key = self.get_key2()
        nonce = b64decode(message[:12].encode('utf-8'))
        ct = b64decode(message[12:].encode('utf-8'))
        cipher = AES.new(key, AES.MODE_CTR, nonce=nonce)
        pt = cipher.decrypt(ct)

        message = pt.decode('utf-8')
        key = self.get_key1()
        nonce = b64decode(message[:12].encode('utf-8'))
        ct = b64decode(message[12:].encode('utf-8'))
        cipher = AES.new(key, AES.MODE_CTR, nonce=nonce)
        pt = cipher.decrypt(ct)

        return pt.decode('utf-8')
        # except (ValueError, KeyError):
        #print("Incorrect decryption.")


if __name__ == '__main__':
    m = "secret message"
    print(m)
    c = Crypto()
    e_m = c.encrypt(m)
    print(e_m)
    d_m = c.decrypt(e_m)
    print(d_m)

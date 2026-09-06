import base64

# noinspection PyPackageRequirements
from Crypto.Cipher import AES
# noinspection PyPackageRequirements
from Crypto.Random import get_random_bytes
# noinspection PyPackageRequirements
from Crypto.Util.Padding import pad, unpad


# pip install -i http://mirrors.aliyun.com/pypi/simple/ pycryptodome --trusted-host mirrors.aliyun.com

class AESCipher:
    def __init__(self, key='12345678901234567890123456789012'):
        """
        初始化 AES 加密器
        :param key: 密钥（16/24/32字节）
        """
        self.key = bytes.fromhex(key)

    def encrypt(self, text):
        """加密文本"""
        iv = get_random_bytes(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        cipher_text = cipher.encrypt(pad(text.encode('utf-8'), AES.block_size))
        return base64.b64encode(iv + cipher_text).decode('utf-8')

    def decrypt(self, text):
        """解密文本"""
        encrypted_data = base64.b64decode(text)
        iv = encrypted_data[:AES.block_size]
        cipher_text = encrypted_data[AES.block_size:]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        plain_text = unpad(cipher.decrypt(cipher_text), AES.block_size)
        return plain_text.decode('utf-8')

    def encrypt_file(self, input_file, output_file):
        """加密文件"""
        iv = get_random_bytes(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)

        with open(input_file, 'rb') as fin:
            with open(output_file, 'wb') as f:
                f.write(iv)
                while True:
                    chunk = fin.read(64 * 1024)  # 64KB chunks
                    if len(chunk) == 0:
                        break
                    elif len(chunk) % AES.block_size != 0:
                        chunk = pad(chunk, AES.block_size)
                    f.write(cipher.encrypt(chunk))

    def decrypt_file(self, input_file, output_file):
        """解密文件"""
        with open(input_file, 'rb') as fin:
            iv = fin.read(AES.block_size)
            cipher = AES.new(self.key, AES.MODE_CBC, iv)

            with open(output_file, 'wb') as f:
                while True:
                    chunk = fin.read(64 * 1024)  # 64KB chunks
                    if len(chunk) == 0:
                        break
                    decrypted_chunk = cipher.decrypt(chunk)
                    try:
                        decrypted_chunk = unpad(decrypted_chunk, AES.block_size)
                    except ValueError:
                        pass  # 最后一个块可能不需要 unpadding
                    f.write(decrypted_chunk)


# 文件加密解密 (取消注释以使用)
# cipher.encrypt_file('plain.txt', 'encrypted.bin')
# cipher.decrypt_file('encrypted.bin', 'decrypted.txt')
if __name__ == '__main__':
    test_cipher = AESCipher()
    encrypted_text = test_cipher.encrypt("123456")
    print("加密文本:", encrypted_text)
    decrypted_text = test_cipher.decrypt(encrypted_text)
    print("解密文本:", decrypted_text)

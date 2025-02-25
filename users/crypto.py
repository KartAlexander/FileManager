# crypto.py
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
from django.core.files.base import ContentFile

# Генерация случайного 256-битного ключа
def generate_key():
    return os.urandom(32)

# Шифрование файла
def encrypt_file(file_content):
    iv = os.urandom(16)
    key = generate_key()
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(file_content) + padder.finalize()
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
    
    # Сохраняем зашифрованные данные и ключ
    encrypted_file = ContentFile(iv + encrypted_data)
    return encrypted_file, key

# Расшифровка файла
def decrypt_file(encrypted_file_content, key):
    iv = encrypted_file_content[:16]
    encrypted_data = encrypted_file_content[16:]
    
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()
    
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    return unpadder.update(decrypted_data) + unpadder.finalize()

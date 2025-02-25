from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
import base64
import os

def generate_key_pair():
    """Генерирует новую пару RSA ключей"""
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    
    # Сериализация приватного ключа
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    # Сериализация публичного ключа
    public_key = private_key.public_key()
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    return {
        'private_key': private_pem,
        'public_key': public_pem
    }

def encrypt_file(file_path, public_key_pem):
    """Шифрует файл с использованием публичного ключа RSA"""
    # Загрузка публичного ключа
    public_key = serialization.load_pem_public_key(
        public_key_pem,
        backend=default_backend()
    )
    
    # Подготовка выходного файла
    encrypted_file_path = file_path + '.enc'
    chunk_size = 190  # Максимальный размер блока для RSA-2048
    
    with open(file_path, 'rb') as f_in, open(encrypted_file_path, 'wb') as f_out:
        while True:
            chunk = f_in.read(chunk_size)
            if not chunk:
                break
                
            # Шифрование блока
            encrypted_chunk = public_key.encrypt(
                chunk,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            # Запись размера зашифрованного блока и самого блока
            f_out.write(len(encrypted_chunk).to_bytes(4, byteorder='big'))
            f_out.write(encrypted_chunk)
    
    return encrypted_file_path

def decrypt_file(encrypted_file_path, private_key_pem):
    """Дешифрует файл с использованием приватного ключа RSA"""
    # Загрузка приватного ключа
    private_key = serialization.load_pem_private_key(
        private_key_pem,
        password=None,
        backend=default_backend()
    )
    
    # Подготовка выходного файла
    decrypted_file_path = encrypted_file_path.replace('.enc', '.dec')
    
    with open(encrypted_file_path, 'rb') as f_in, open(decrypted_file_path, 'wb') as f_out:
        while True:
            # Чтение размера блока
            size_bytes = f_in.read(4)
            if not size_bytes:
                break
                
            size = int.from_bytes(size_bytes, byteorder='big')
            encrypted_chunk = f_in.read(size)
            
            # Дешифрование блока
            decrypted_chunk = private_key.decrypt(
                encrypted_chunk,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            f_out.write(decrypted_chunk)
    
    return decrypted_file_path
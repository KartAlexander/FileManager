from django.utils.crypto import get_random_string
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
import os
from django.http import JsonResponse, FileResponse
from django.core.files.storage import FileSystemStorage
from django.shortcuts import get_object_or_404
from django.utils.encoding import smart_str
from django.conf import settings
import mimetypes
import tempfile
from .models import EncryptedFile
from .crypto_utils import generate_key_pair, encrypt_file, decrypt_file
from django.core.files.base import ContentFile
import json

# Функция загрузки файла с шифрованием
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def file_upload(request):
    if 'file' not in request.FILES:
        return JsonResponse({'error': 'No file uploaded'}, status=400)

    file = request.FILES['file']
    user = request.user
    unique_filename = get_random_string(length=32) + '_' + file.name
    encrypt_option = request.POST.get('encrypt', 'false').lower() == 'true'

    try:
        fs = FileSystemStorage()
        filename = fs.save(unique_filename, file)
        file_path = fs.path(filename)
        
        # Информация для создания записи о файле
        file_data = {
            'user': user,
            'file': filename,
            'size': file.size,
            'filename': file.name,
            'is_encrypted': encrypt_option
        }
        
        # Если нужно зашифровать файл
        if encrypt_option:
            # Генерируем пару ключей RSA
            key_pair = generate_key_pair()
            
            # Шифруем файл публичным ключом
            encrypted_file_path = encrypt_file(file_path, key_pair['public_key'])
            encrypted_filename = os.path.basename(encrypted_file_path)
            
            # Сохраняем зашифрованный файл
            with open(encrypted_file_path, 'rb') as f:
                encrypted_file_content = f.read()
            
            # Удаляем исходный файл и временный зашифрованный
            fs.delete(filename)
            os.remove(encrypted_file_path)
            
            # Сохраняем зашифрованный файл в хранилище
            encrypted_storage_path = fs.save(encrypted_filename, ContentFile(encrypted_file_content))
            file_data['file'] = encrypted_storage_path

            # Определяем размер зашифрованного файла
            encrypted_file_size = os.path.getsize(fs.path(encrypted_storage_path))
            file_data['size'] = encrypted_file_size

            
            # Сохраняем приватный ключ
            key_filename = get_random_string(length=32) + '.pem'
            key_storage_path = fs.save('keys/' + key_filename, ContentFile(key_pair['private_key']))
            file_data['key'] = key_storage_path
            
            # Сохраняем публичный ключ в текстовом поле
            file_data['public_key'] = key_pair['public_key'].decode('utf-8')
        
        # Создаем запись о файле
        file_instance = EncryptedFile.objects.create(**file_data)

        return JsonResponse({
            'message': 'File uploaded successfully',
            'file_id': file_instance.id,
            'filename': file.name,
            'size': file.size,
            'is_encrypted': encrypt_option
        })

    except Exception as e:
        return JsonResponse({'error': f'Error saving file: {str(e)}'}, status=500)

# Функция получения списка файлов
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def file_list(request):
    files = EncryptedFile.objects.filter(user=request.user)
    files_data = [{
        'id': f.id, 
        'filename': f.filename,
        'size': f.size,
        'is_encrypted': f.is_encrypted,
        'uploaded_at': f.uploaded_at.strftime('%Y-%m-%d %H:%M:%S') if f.uploaded_at else None
    } for f in files]
    return Response({'files': files_data})

# Функция скачивания файла
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def file_download(request, file_id):
    try:
        file_instance = get_object_or_404(EncryptedFile, id=file_id, user=request.user)
        file_path = file_instance.file.path
        
        # Если файл зашифрован, расшифровываем его
        if file_instance.is_encrypted and file_instance.key:
            # Получаем приватный ключ
            private_key_path = file_instance.key.path
            with open(private_key_path, 'rb') as key_file:
                private_key = key_file.read()
            
            # Расшифровываем во временный файл
            decrypted_file_path = decrypt_file(file_path, private_key)
            
            # Подготовка ответа с расшифрованным файлом
            mime_type, _ = mimetypes.guess_type(file_instance.filename)
            mime_type = mime_type or 'application/octet-stream'
            
            filename = smart_str(file_instance.filename)
            response = FileResponse(open(decrypted_file_path, 'rb'), as_attachment=True)
            response['Content-Type'] = mime_type
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            # Регистрируем временный файл для удаления после отправки
            response._file_to_clean = decrypted_file_path
            return response
        else:
            # Отправляем незашифрованный файл как обычно
            mime_type, _ = mimetypes.guess_type(file_instance.filename)
            mime_type = mime_type or 'application/octet-stream'
            
            filename = smart_str(file_instance.filename)
            response = FileResponse(open(file_path, 'rb'), as_attachment=True)
            response['Content-Type'] = mime_type
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
            
    except Exception as e:
        return JsonResponse({'error': f'Error downloading file: {str(e)}'}, status=500)

# Очистка временных файлов после отправки
def cleanup_temp_file(sender, **kwargs):
    if 'response' in kwargs and hasattr(kwargs['response'], '_file_to_clean'):
        try:
            os.remove(kwargs['response']._file_to_clean)
        except (OSError, AttributeError):
            pass

# Регистрация сигнала
from django.core.signals import request_finished
request_finished.connect(cleanup_temp_file)

# Функция удаления файла
@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def file_delete(request, file_id):
    file_instance = get_object_or_404(EncryptedFile, id=file_id, user=request.user)
    
    try:
        if file_instance.key:
            file_instance.key.delete()  # Удаление ключа
        file_instance.file.delete()  # Удаление файла
        file_instance.delete()  # Удаление записи

        return JsonResponse({'message': 'File deleted successfully'})
    except Exception as e:
        return JsonResponse({'error': f'Error deleting file: {str(e)}'}, status=500)

# Получение публичного ключа для шифрования
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_public_key(request, file_id):
    file_instance = get_object_or_404(EncryptedFile, id=file_id, user=request.user)
    
    if file_instance.public_key:
        return JsonResponse({'public_key': file_instance.public_key})
    else:
        return JsonResponse({'error': 'No public key found'}, status=404)
from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import JsonResponse
from django.contrib.auth import authenticate

import json

# Главная страница
def home(request):
    return render(request, 'home.js')  # Замените 'home.js' на правильный шаблон, например 'home.html'

# Регистрация пользователя
@api_view(['POST'])
def register(request):
    if request.method == 'POST':
        try:
            # Получаем данные пользователя из запроса
            data = json.loads(request.body.decode('utf-8'))
            username = data['username']
            password = data['password']

            # Создаём нового пользователя
            user = User.objects.create(
                username=username,
                password=make_password(password)  # Сохраняем пароль в зашифрованном виде
            )
            user.save()

            return JsonResponse({'message': 'User created successfully'}, status=201)
        except KeyError:
            return JsonResponse({'error': 'Missing username or password'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid method'}, status=405)

# Логин пользователя
@api_view(['POST'])
def login(request):
    if request.method == 'POST':
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            return Response({'access_token': access_token, 'refresh_token': str(refresh)}, status=200)
        else:
            return Response({'error': 'Invalid credentials'}, status=400)
    return Response({'error': 'Invalid method'}, status=405)
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt import views as jwt_views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')),  # URL для пользователей
    path('api/files/', include('files.urls')),  # URL для работы с файлами
    path('api/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),

]


if settings.DEBUG:  # Включаем доступ к медиафайлам в режиме разработки
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



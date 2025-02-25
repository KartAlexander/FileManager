from django.urls import path
from .views import file_upload, file_list, file_download, file_delete, get_public_key

urlpatterns = [
    path('upload/', file_upload, name='file-upload'),
    path('', file_list, name='file-list'),
    path('<int:file_id>/', file_download, name='file-download'),
    path('delete/<int:file_id>/', file_delete, name='file-delete'),
    path('key/<int:file_id>/', get_public_key, name='get-public-key'),
]
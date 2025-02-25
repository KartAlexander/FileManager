from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User

class EncryptedFile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='encrypted_files/')
    filename = models.CharField(max_length=255)
    key = models.FileField(upload_to='keys/', null=True, blank=True)
    public_key = models.TextField(null=True, blank=True)
    is_encrypted = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)  # Оставляем только auto_now_add
    size = models.BigIntegerField(null=True, blank=True)

    def __str__(self):
        return self.filename

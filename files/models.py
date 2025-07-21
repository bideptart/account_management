from django.db import models
from django.contrib.auth.models import User
import os

class Folder(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='folders')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subfolders')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']
        unique_together = ['name', 'user', 'parent']

def user_directory_path(instance, filename):
    # File will be uploaded to MEDIA_ROOT/user_<id>/<folder_name>/<filename>
    folder_path = ''
    if instance.folder:
        folder_path = f"{instance.folder.name}/"
    return f"user_{instance.user.id}/{folder_path}{filename}"

class File(models.Model):
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to=user_directory_path)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='files')
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, null=True, blank=True, related_name='files')
    created_at = models.DateTimeField(auto_now_add=True)
    size = models.PositiveIntegerField(default=0)  # Size in bytes
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if self.file:
            self.size = self.file.size
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        # Delete the file from storage
        if self.file:
            if os.path.isfile(self.file.path):
                os.remove(self.file.path)
        super().delete(*args, **kwargs)
    
    def get_file_type(self):
        filename, extension = os.path.splitext(self.file.name)
        return extension.lower()
    
    def is_image(self):
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
        return self.get_file_type() in image_extensions
    
    class Meta:
        ordering = ['name']

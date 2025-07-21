from django.urls import path
from . import views

app_name = 'files'

urlpatterns = [
    path('', views.file_list, name='file_list'),
    path('folder/<int:folder_id>/', views.file_list, name='folder_detail'),
    path('create-folder/', views.create_folder, name='create_folder'),
    path('create-folder/<int:folder_id>/', views.create_folder, name='create_subfolder'),
    path('upload-file/', views.upload_file, name='upload_file'),
    path('upload-file/<int:folder_id>/', views.upload_file, name='upload_file_to_folder'),
    path('delete-folder/<int:folder_id>/', views.delete_folder, name='delete_folder'),
    path('files/delete/<int:file_id>/', views.delete_file, name='delete_file'),
    path('edit-file/<int:file_id>/', views.edit_file, name='edit_file'),
    path('download-file/<int:file_id>/', views.download_file, name='download_file'),
    path('search/', views.search_files, name='search_files'),
    path('recent/', views.recent_files, name='recent_files'),
    path('shared/', views.shared_files, name='shared_files'),
    path('trash/', views.trash_files, name='trash_files'),
]
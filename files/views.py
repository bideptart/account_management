from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.db.models import Q
import os

from .models import Folder, File
from .forms import FolderForm, FileForm, FileEditForm

@login_required
def file_list(request, folder_id=None):
    # Get current folder if folder_id is provided
    current_folder = None
    if folder_id:
        current_folder = get_object_or_404(Folder, id=folder_id)
        # Check if user has permission to access this folder
        if current_folder.user != request.user and not request.user.is_superuser:
            messages.error(request, 'You do not have permission to access this folder.')
            return redirect('files:file_list')
    
    # Get user for admin view
    user_id = request.GET.get('user_id')
    target_user = request.user
    
    if user_id and request.user.is_superuser:
        target_user = get_object_or_404(User, id=user_id)
    
    # Get folders and files
    folders = Folder.objects.filter(user=target_user, parent=current_folder)
    files = File.objects.filter(user=target_user, folder=current_folder)
    
    # Sort by name or date
    sort_by = request.GET.get('sort', 'name')
    if sort_by == 'date':
        folders = folders.order_by('-created_at')
        files = files.order_by('-created_at')
    else:  # Default to name
        folders = folders.order_by('name')
        files = files.order_by('name')
    
    # Create breadcrumbs
    breadcrumbs = []
    if current_folder:
        temp_folder = current_folder
        while temp_folder:
            breadcrumbs.append(temp_folder)
            temp_folder = temp_folder.parent
        breadcrumbs.reverse()
    
    # Forms
    folder_form = FolderForm()
    file_form = FileForm()
    
    # Check view type
    view_type = request.GET.get('view', 'grid')
    
    # Apply view type specific settings
    if view_type == 'list':
        files = files.order_by('-created_at')
    
    context = {
        'current_folder': current_folder,
        'folders': folders,
        'files': files,
        'breadcrumbs': breadcrumbs,
        'folder_form': folder_form,
        'file_form': file_form,
        'target_user': target_user,
        'sort_by': sort_by,
        'view_type': view_type,
    }
    
    return render(request, 'files/file_list.html', context)

@login_required
def create_folder(request, folder_id=None):
    parent_folder = None
    if folder_id:
        parent_folder = get_object_or_404(Folder, id=folder_id)
        # Check if user has permission to create folder here
        if parent_folder.user != request.user and not request.user.is_superuser:
            messages.error(request, 'You do not have permission to create a folder here.')
            return redirect('files:file_list')
    
    # Get user for admin view
    user_id = request.GET.get('user_id')
    target_user = request.user
    
    if user_id and request.user.is_superuser:
        target_user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        form = FolderForm(request.POST)
        if form.is_valid():
            folder = form.save(commit=False)
            folder.user = target_user
            folder.parent = parent_folder
            folder.save()
            messages.success(request, 'Folder created successfully.')
            
            # Redirect back to the appropriate view
            if parent_folder:
                return redirect('files:folder_detail', folder_id=parent_folder.id)
            else:
                if user_id and request.user.is_superuser:
                    return redirect('files:file_list') + f'?user_id={user_id}'
                return redirect('files:file_list')
    
    return redirect('files:file_list')

@login_required
def upload_file(request, folder_id=None):
    folder = None
    if folder_id:
        folder = get_object_or_404(Folder, id=folder_id)
        # Check if user has permission to upload to this folder
        if folder.user != request.user and not request.user.is_superuser:
            messages.error(request, 'You do not have permission to upload to this folder.')
            return redirect('files:file_list')
    
    # Get user for admin view
    user_id = request.GET.get('user_id')
    target_user = request.user
    
    if user_id and request.user.is_superuser:
        target_user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        form = FileForm(request.POST, request.FILES)
        files = request.FILES.getlist('file')
        
        if form.is_valid():
            for f in files:
                file_instance = File(file=f, name=f.name, user=target_user, folder=folder)
                file_instance.save()
            
            messages.success(request, f'{len(files)} file(s) uploaded successfully.')
            
            # Redirect back to the appropriate view
            if folder:
                return redirect('files:folder_detail', folder_id=folder.id)
            else:
                if user_id and request.user.is_superuser:
                    return redirect('files:file_list') + f'?user_id={user_id}'
                return redirect('files:file_list')
    
    return redirect('files:file_list')

@login_required
def delete_folder(request, folder_id):
    folder = get_object_or_404(Folder, id=folder_id)
    
    # Check if user has permission to delete this folder
    if folder.user != request.user and not request.user.is_superuser:
        messages.error(request, 'You do not have permission to delete this folder.')
        return redirect('files:file_list')
    
    parent_folder = folder.parent
    user_id = request.GET.get('user_id')
    
    folder.delete()
    messages.success(request, 'Folder deleted successfully.')
    
    # Redirect back to the appropriate view
    if parent_folder:
        return redirect('files:folder_detail', folder_id=parent_folder.id)
    else:
        if user_id and request.user.is_superuser:
            return redirect('files:file_list') + f'?user_id={user_id}'
        return redirect('files:file_list')

@login_required
def delete_file(request, file_id):
    file = get_object_or_404(File, id=file_id)
    
    # Check if user has permission to delete this file
    if file.user != request.user and not request.user.is_superuser:
        messages.error(request, 'You do not have permission to delete this file.')
        return redirect('files:file_list')
    
    folder = file.folder
    user_id = request.GET.get('user_id')
    
    file.delete()
    messages.success(request, 'File deleted successfully.')
    
    # Redirect back to the appropriate view
    if folder:
        return redirect('files:folder_detail', folder_id=folder.id)
    else:
        if user_id and request.user.is_superuser:
            return redirect('files:file_list') + f'?user_id={user_id}'
        return redirect('files:file_list')

@login_required
def recent_files(request):
    # Get files sorted by most recent
    files = File.objects.filter(user=request.user).order_by('-created_at')[:50]
    
    context = {
        'files': files,
        'view_type': 'recent',
    }
    return render(request, 'files/file_list.html', context)

@login_required
def shared_files(request):
    # Get files shared with current user
    files = File.objects.filter(
        Q(shared_with=request.user) | Q(user=request.user, is_shared=True)
    ).distinct()
    
    context = {
        'files': files,
        'view_type': 'shared',
    }
    return render(request, 'files/file_list.html', context)

@login_required
def trash_files(request):
    # Get deleted files (soft delete implementation would be needed)
    files = File.objects.filter(user=request.user, is_deleted=True)
    
    context = {
        'files': files,
        'view_type': 'trash',
    }
    return render(request, 'files/file_list.html', context)

@login_required
def edit_file(request, file_id):
    file = get_object_or_404(File, id=file_id)
    
    # Check if user has permission to edit this file
    if file.user != request.user and not request.user.is_superuser:
        messages.error(request, 'You do not have permission to edit this file.')
        return redirect('files:file_list')
    
    if request.method == 'POST':
        form = FileEditForm(request.POST, instance=file)
        if form.is_valid():
            form.save()
            messages.success(request, 'File updated successfully.')
            
            # Redirect back to the appropriate view
            if file.folder:
                return redirect('files:folder_detail', folder_id=file.folder.id)
            else:
                user_id = request.GET.get('user_id')
                if user_id and request.user.is_superuser:
                    return redirect('files:file_list') + f'?user_id={user_id}'
                return redirect('files:file_list')
    else:
        form = FileEditForm(instance=file)
    
    return render(request, 'files/edit_file.html', {'form': form, 'file': file})

@login_required
def download_file(request, file_id):
    file = get_object_or_404(File, id=file_id)
    
    # Check if user has permission to download this file
    if file.user != request.user and not request.user.is_superuser:
        messages.error(request, 'You do not have permission to download this file.')
        return redirect('files:file_list')
    
    file_path = file.file.path
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/octet-stream")
            response['Content-Disposition'] = f'attachment; filename={os.path.basename(file_path)}'
            return response
    
    messages.error(request, 'File not found.')
    return redirect('files:file_list')

@login_required
def search_files(request):
    query = request.GET.get('q', '')
    user_id = request.GET.get('user_id')
    
    if not query:
        return redirect('files:file_list')
    
    target_user = request.user
    if user_id and request.user.is_superuser:
        target_user = get_object_or_404(User, id=user_id)
    
    folders = Folder.objects.filter(user=target_user, name__icontains=query)
    files = File.objects.filter(user=target_user, name__icontains=query)
    
    context = {
        'folders': folders,
        'files': files,
        'query': query,
        'target_user': target_user,
    }
    
    return render(request, 'files/search_results.html', context)

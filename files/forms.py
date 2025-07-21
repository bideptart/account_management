from django import forms
from .models import Folder, File

class FolderForm(forms.ModelForm):
    class Meta:
        model = Folder
        fields = ['name']

class FileForm(forms.ModelForm):
    # Use a regular FileField without the multiple attribute in the widget
    # The multiple attribute will be added via JavaScript/HTML
    file = forms.FileField(required=True)
    
    class Meta:
        model = File
        fields = ['file']

class FileEditForm(forms.ModelForm):
    class Meta:
        model = File
        fields = ['name']
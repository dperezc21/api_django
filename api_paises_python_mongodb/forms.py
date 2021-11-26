from django import forms
from django.forms.widgets import PasswordInput

class File(forms.Form):
    file = forms.FileField()

class Login(forms.Form):
    usuario = forms.CharField(max_length = 30, required=True)
    password = forms.CharField(widget=PasswordInput)

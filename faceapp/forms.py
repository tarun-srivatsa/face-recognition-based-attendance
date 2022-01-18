from django import forms
from django.forms import ModelForm
from django.core.validators import RegexValidator
from .models import Student

class RegisterForm(ModelForm):
    name=forms.CharField(
        max_length=60,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'name'})
    )
    usn = forms.CharField(
        max_length=15,
        validators=[RegexValidator('1RV\d\d[A-Z][A-Z][0-4]\d\d', message='Invalid USN')],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'USN'}),
    )

    class Meta():
        model=Student
        fields=['name','usn']
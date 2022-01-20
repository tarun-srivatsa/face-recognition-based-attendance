from django import forms
from django.forms import ModelForm
from django.core.validators import RegexValidator
from .models import Class, CurrentSession, Section, Student

class StudentForm(ModelForm):
    name=forms.CharField(
        max_length=60,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'})
    )
    usn = forms.CharField(
        max_length=10,
        validators=[RegexValidator('1RV\d\d[A-Z][A-Z][0-4]\d\d', message='Invalid USN')],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'USN'}),
    )

    section = forms.ModelChoiceField(
        queryset=Section.objects.all(),
        widget=forms.Select(attrs={'style': 'max-width:17em'})
    )

    # photo=forms.ImageField()

    class Meta():
        model=Student
        fields=['name','usn','section']

class NewSessionForm(ModelForm):
    class_details=forms.ModelChoiceField(
        queryset=Class.objects.all(),
        widget=forms.Select(attrs={'style': 'max-width:17em'})
    )

    attendance_countage=forms.IntegerField(
        min_value=1,
        max_value=5
    )

    class Meta():
        model=CurrentSession
        fields=['class_details','attendance_countage']
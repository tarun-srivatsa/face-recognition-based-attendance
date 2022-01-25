from django import forms
from django.forms import ModelForm, NumberInput, TextInput, ValidationError
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

    class Meta():
        model=Student
        fields=['name','usn','section']

class NewSessionForm(ModelForm):
    class_details=forms.ModelChoiceField(
        queryset=Class.objects.all().order_by('course_code'),
    )

    attendance_countage=forms.IntegerField(
        min_value=1,
        max_value=5,
        widget=forms.NumberInput(attrs={'value':1})
    )

    class Meta():
        model=CurrentSession
        fields=['class_details','attendance_countage']

    def clean_class_details(self):
        class_details=self.cleaned_data.get('class_details')
        if CurrentSession.objects.filter(classdetails=class_details,is_active=True).exists():
            raise ValidationError('Please close the existing active session to create a new session for this course')
        return class_details
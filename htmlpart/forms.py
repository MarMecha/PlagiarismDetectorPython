from django import forms
from .models import Teacher, Student, File

class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['first_name', 'last_name', 'university', 'uni_Mail', 'password']
        
class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['first_name', 'last_name', 'university', 'uni_Mail', 'password']

class FileForm(forms.ModelForm):
    class Meta: 
        model = File
        fields = ['file']
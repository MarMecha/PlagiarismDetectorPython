from django.db import models
from django.utils.timezone import now
import os

# Create your models here.
class Teacher(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    university = models.CharField(max_length=50)
    uni_Mail = models.EmailField(unique=True, max_length=200)
    password = models.CharField(max_length=50)

    def __str__(self):
        return self.first_name + ' ' + self.last_name + ' ' + self.university
    
class Student(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    university = models.CharField(max_length=50)
    uni_Mail = models.EmailField(max_length=200)
    password = models.CharField(max_length=50)

    def __str__(self):
        return self.first_name + ' ' + self.last_name + ' ' + self.university

class File(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=True, blank=True)
    file = models.FileField(upload_to="files/", unique=True)
    filename = models.CharField(max_length=255, unique=True, null=True, blank=True)  # Temporarily allow null values
    fingerprints = models.JSONField(default=list)
    text_positions = models.JSONField(default=list)
    
    def save(self, *args, **kwargs):
        if not self.filename:  # Ensure filename is stored
            self.filename = self.file.name
        super().save(*args, **kwargs)

    def __str__(self):
        return self.filename

class Results(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=True, blank=True)
    file1_name = models.CharField(max_length=255)
    comparison_files = models.TextField()  # Directly store comma-separated NAMES, not IDs
    created_at = models.DateTimeField(auto_now_add=True)
    percentage = models.FloatField(null=True, blank=True)

    def get_comparison_filenames(self):
        """Simply return comparison filenames (already stored)."""
        return self.comparison_files

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Keep maximum 20 entries per teacher
        teacher_history = Results.objects.filter(teacher=self.teacher).order_by('-created_at')
        if teacher_history.count() > 10:
            to_delete = teacher_history[10:]
            for result in to_delete:
                result.delete()

    def __str__(self):
        return f"{self.file1_name} compared with {self.get_comparison_filenames()} at {self.created_at}"

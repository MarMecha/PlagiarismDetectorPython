from django.contrib import admin
from .models import *
import os
# Register your models here.

admin.site.register(Teacher)

admin.site.register(Student)

admin.site.register(File)

@admin.register(Results)
class ResultsAdmin(admin.ModelAdmin):
    list_display = ('get_primary_filename', 'get_comparison_filenames','percentage' , 'created_at')  # Add 'Percentage'
    search_fields = ('file1_name', 'files_name')

    def get_primary_filename(self, obj):
        return os.path.basename(obj.file1_name)

    def get_comparison_filenames(self, obj):
        return obj.get_comparison_filenames()

    def get_overall_percentage(self, obj):
        return obj.Percentage  # Display the stored percentage

    get_primary_filename.short_description = "Primary File"
    get_comparison_filenames.short_description = "Comparison Files"
    get_overall_percentage.short_description = "Overall Percentage"  # Label the column

    date_hierarchy = 'created_at'  # Optional: Adds date filter
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('signup/', views.signUp, name="signUp"),
    path('signIn/', views.signIn, name="signIn"),
    path('teacherPage/', views.teacherPage, name='TeacherPage'),
    path('add_files/', views.add_files, name='add_files'),
    path('delete_files/', views.delete_files, name='delete_files'),
    path('studentPage/', views.studentPage, name='StudentPage'),
    path('logout/', views.signOut, name='signOut')
]

from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_student, name='register'),
    path('login/', views.custom_login, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('dashboard/', views.student_dashboard, name='student_dashboard'),
    path('wallet/', views.wallet_view, name='wallet'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/assign-credits/', views.assign_credits, name='assign_credits'),
]


from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('access-denied/', views.access_denied, name='access_denied'),

    # Custom admin dashboard: user management
    path('manage/users/', views.manage_users, name='manage_users'),
    path('manage/users/<int:pk>/role/', views.change_user_role, name='change_user_role'),
    path('manage/users/<int:pk>/toggle/', views.toggle_user_status, name='toggle_user_status'),
]

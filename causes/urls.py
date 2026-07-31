from django.urls import path
from . import views

urlpatterns = [
    path('', views.cause_list, name='cause_list'),
    path('<int:pk>/', views.cause_detail, name='cause_detail'),

    # Custom admin dashboard
    path('manage/', views.manage_causes, name='manage_causes'),
    path('manage/add/', views.cause_form, name='add_cause'),
    path('manage/<int:pk>/edit/', views.cause_form, name='edit_cause'),
    path('manage/<int:pk>/delete/', views.delete_cause, name='delete_cause'),
    path('manage/categories/', views.manage_categories, name='manage_categories'),
    path('manage/categories/<int:pk>/delete/', views.delete_category, name='delete_category'),
]

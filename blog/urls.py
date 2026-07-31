from django.urls import path
from . import views

urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('<int:pk>/', views.post_detail, name='post_detail'),

    # Custom admin dashboard
    path('manage/', views.manage_posts, name='manage_posts'),
    path('manage/add/', views.post_form, name='add_post'),
    path('manage/<int:pk>/edit/', views.post_form, name='edit_post'),
    path('manage/<int:pk>/delete/', views.delete_post, name='delete_post'),
    path('manage/categories/', views.manage_blog_categories, name='manage_blog_categories'),
    path('manage/categories/<int:pk>/delete/', views.delete_blog_category, name='delete_blog_category'),
]

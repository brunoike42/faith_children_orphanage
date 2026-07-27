from django.urls import path
from . import views

urlpatterns = [
    path('our-children/', views.child_list, name='child_list'),
    path('', views.volunteer_list, name='opportunity_list'),
    path('<int:pk>/apply/', views.apply_volunteer, name='apply_volunteer'),
    path('<int:pk>/', views.volunteer_detail, name='opportunity_detail'),
    path('create/', views.volunteer_form, name='volunteer_create'),
    path('<int:pk>/edit/', views.volunteer_form, name='volunteer_edit'),
    path('manage/', views.manage_opportunities, name='manage_opportunities'),
    path('applications/', views.manage_applications, name='manage_applications'),
    path('applications/<int:pk>/status/', views.update_application_status, name='update_application_status'),
]
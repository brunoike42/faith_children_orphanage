from django.urls import path
from . import views

urlpatterns = [
    path('our-children/', views.child_list, name='child_list'),
    path('', views.volunteer_list, name='opportunity_list'),
    path('<int:pk>/apply/', views.apply_volunteer, name='apply_volunteer'),
    path('<int:pk>/', views.volunteer_detail, name='opportunity_detail'),

    # Custom admin dashboard: opportunities
    path('manage/', views.manage_opportunities, name='manage_opportunities'),
    path('manage/add/', views.volunteer_form, name='add_opportunity'),
    path('manage/<int:pk>/edit/', views.volunteer_form, name='edit_opportunity'),
    path('manage/<int:pk>/delete/', views.delete_opportunity, name='delete_opportunity'),

    # Custom admin dashboard: applications
    path('applications/', views.manage_applications, name='manage_applications'),
    path('applications/<int:pk>/status/', views.update_application_status, name='update_application_status'),

    # Custom admin dashboard: children profiles
    path('manage/children/', views.manage_children, name='manage_children'),
    path('manage/children/add/', views.child_form, name='add_child'),
    path('manage/children/<int:pk>/edit/', views.child_form, name='edit_child'),
    path('manage/children/<int:pk>/delete/', views.delete_child, name='delete_child'),
]

from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('', views.home, name='home'),  # Add this line for homepage
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboards
    path('dashboard/', views.owner_dashboard, name='owner_dashboard'),
    path('inspector/dashboard/', views.inspector_dashboard, name='inspector_dashboard'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    # Properties
    path('properties/', views.my_properties, name='my_properties'),
    path('properties/add/', views.add_property, name='add_property'),
]
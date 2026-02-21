from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    
    path('apartments/', views.apartment_list, name='apartment_list'),
    path('apartments/<slug:slug>/', views.apartment_detail, name='apartment_detail'),
    path('search/', views.search, name='search'),
    path('agent/<int:id>/', views.agent_profile, name='agent_profile'),

    # Auth and Agent
    path('register/', views.RegisterPage, name='register'),
    path('login/', views.LoginPage, name='login'),
    path('logout/', views.LogoutPage, name='logout'),

    path('dashboard/', views.agent_dashboard, name='agent_dashboard'),
    path('my-listings/', views.my_listings, name='my_listings'),
    path('add-apartment/', views.add_apartment, name='add_apartment'),
    path('edit-apartment/<int:apartment_id>/', views.edit_apartment, name='edit_apartment'),
    path('delete-apartment/<int:apartment_id>/', views.delete_apartment, name='delete_apartment'),
    path('delete-image/<int:image_id>/', views.delete_apartment_image, name='delete_apartment_image'),
    path('profile/', views.profile, name='profile'),

    # Payments
    path('feature-payment/<int:apartment_id>/', views.request_feature_payment, name='request_feature_payment'),
    path('boost-payment/<int:apartment_id>/', views.request_boost_payment, name='request_boost_payment'),
    path('payment-success/<int:payment_id>/', views.payment_success, name='payment_success'),
]
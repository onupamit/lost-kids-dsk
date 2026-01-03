from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('cases/', views.case_list, name='case_list'),
    path('case/<uuid:pk>/', views.case_detail, name='case_detail'),
    path('report/', views.report_missing_child, name='report_missing_child'),
    path('lead/<uuid:child_id>/', views.submit_lead, name='submit_lead'),
    path('subscribe/', views.subscribe_alerts, name='subscribe_alerts'),
    path('emergency-contacts/', views.emergency_contacts, name='emergency_contacts'),
    path('verify-email/<str:token>/', views.verify_email, name='verify_email'),
    path('location-update/<uuid:child_id>/', views.submit_location_update, name='submit_location_update'),
    path('search/', views.search_cases, name='search_cases'),
]
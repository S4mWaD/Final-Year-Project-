from django.urls import path
from . import views

urlpatterns = [
    path ('', views.home, name='home'),
    path('vendor/<int:vendor_id>/', views.vendor_questionnaire, name='vendor_questionnaire'),
    path('vendor/<int:vendor_id>/submit/', views.submit_questionnaire, name='submit_questionnaire'),
    path('vendor/<int:vendor_id>/detail/', views.vendor_detail, name='vendor_detail'),
    path('vendor/<int:vendor_id>/detail', views.vendor_detail, name='vendor_detail'),
    path('vendor-risk/<int:vendor_id>/', views.get_risk_assessment, name='get_risk_assessment'),
]

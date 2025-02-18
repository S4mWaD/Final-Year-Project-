from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path ('login/', views.login_view, name='login'), #auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path ('signup/', views.signup_view, name='signup'),
    path ('home/', views.home, name='home'),
    path ('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('vendor/<int:vendor_id>/', views.vendor_questionnaire, name='vendor_questionnaire'),
    path('vendor/<int:vendor_id>/submit/', views.submit_questionnaire, name='submit_questionnaire'),
    path('vendor/<int:vendor_id>/detail/', views.vendor_detail, name='vendor_detail'),
    path('vendor/<int:vendor_id>/detail', views.vendor_detail, name='vendor_detail'),
    path('vendor-risk/<int:vendor_id>/', views.get_risk_assessment, name='get_risk_assessment'),
]

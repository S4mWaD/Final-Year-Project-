from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('login/', views.login_view, name='login'),
    path('home/', views.home, name='home'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup_view, name='signup'),
    path('onboarding/<int:user_id>/', views.vendor_onboarding, name='onboarding'),
    path('profile/', views.profile, name='profile'),
    path('vendors/', views.vendor_list, name='vendor-list'),
    path('vendors/<int:vendor_id>/risk/', views.risk_assessment, name='vendor-risk'),
    
    # New routes for additional features
    path('alerts/', views.alerts, name='alerts'),
    path('settings/', views.settings, name='settings'),
    path('dashboard/', views.admin_dashboard, name='dashboard'),
    path('risk-list/', views.risk_list, name='risk-list'),
    path('checklist-list/', views.checklist_list, name='checklist-list'),
    path('compliance/', views.compliance, name='compliance'),
    path('audit-log/', views.audit_log, name='audit-log'),
    path('terms/', views.terms, name='terms'),
    path('questionnaire/', views.generate_questionnaire, name='questionnaire'),
    path('risk_assessment/<int:assessment_id>/', views.risk_assessment_detail, name='risk_assessment'),
    
    # PDF Generation Route
    path('generate_pdf/<int:vendor_id>/', views.generate_pdf, name='generate_pdf'),
    
    # Password Reset URLs
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='password_reset.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),
]

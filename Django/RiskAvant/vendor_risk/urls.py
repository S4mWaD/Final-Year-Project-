from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('logout/', views.logout_view, name='logout'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('onboarding/<int:user_id>/', views.onboarding, name='onboarding'),
    path('profile/', views.profile, name='profile'),
    path('vendors/', views.vendor_list, name='vendor-list'),
    path('vendors/<int:vendor_id>/risk/', views.risk_assessment, name='vendor-risk'),
    # New routes for additional features
    path('alerts/', views.alerts, name='alerts'),
    path('settings/', views.settings, name='settings'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('risk-list/', views.risk_list, name='risk-list'),
    path('checklist-list/', views.checklist_list, name='checklist-list'),
    path('compliance/', views.compliance, name='compliance'),
    path('audit-log/', views.audit_log, name='audit-log'),
]

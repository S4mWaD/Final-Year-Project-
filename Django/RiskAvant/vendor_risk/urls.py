from django.urls import path
from .views import LoginView, SignupView, VendorListView, VendorDetailView, RiskAssessmentView, QuestionnaireListView
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('api/login/', LoginView.as_view(), name='api-login'),
    path('api/signup/', SignupView.as_view(), name='api-signup'),
    path('api/token-auth/', obtain_auth_token, name='api-token-auth'),
    path('api/vendors/', VendorListView.as_view(), name='vendor-list'),
    path('api/vendors/<int:vendor_id>/', VendorDetailView.as_view(), name='vendor-detail'),
    path('api/vendors/<int:vendor_id>/risk/', RiskAssessmentView.as_view(), name='vendor-risk'),
    path('api/qustionnaire/', QuestionnaireListView.as_view(), name='questionnaire-list'),
    path('api/risk-assessment/', RiskAssessmentView.as_view(), name='risk-assessment-list'),

]
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Vendor, Questionnaire, VendorResponse, RiskAssessment

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('role',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('role',)}),
    )

@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'vendor_type', 'contact_email', 'contact_phone', 'submitted_at')
    search_fields = ('name', 'vendor_type', 'contact_email', 'user__username')
    list_filter = ('vendor_type', 'submitted_at')

@admin.register(Questionnaire)
class QuestionnaireAdmin(admin.ModelAdmin):
    list_display = ('vendor_type', 'question_text')
    search_fields = ('vendor_type', 'question_text')

@admin.register(VendorResponse)
class VendorResponseAdmin(admin.ModelAdmin):
    list_display = ('vendor', 'question', 'response', 'submitted_at')
    search_fields = ('vendor__name', 'question__question_text')

@admin.register(RiskAssessment)
class RiskAssessmentAdmin(admin.ModelAdmin):
    list_display = ('vendor', 'assessment_date', 'risk_score', 'compliance_status', 'created_at')
    search_fields = ('vendor__name', 'compliance_status')

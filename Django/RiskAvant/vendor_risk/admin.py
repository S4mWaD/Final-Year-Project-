from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    CustomUser, Vendor, RiskAssessment, Certification, SecurityChecklistTemplate,
    QuestionBank, SecurityChecklist, SecurityProfile, OnboardingQuestionnaire,
    QuestionnaireRules, VendorResponse
)

# Custom User Admin
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('role', 'organization_name')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('role', 'organization_name')}),
    )

# Inlines for Vendor Admin
class RiskAssessmentInline(admin.TabularInline):
    model = RiskAssessment
    extra = 0

class SecurityChecklistInline(admin.TabularInline):
    model = SecurityChecklist
    extra = 0

class VendorResponseInline(admin.TabularInline):
    model = VendorResponse
    extra = 0

# Vendor Admin
@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'vendor_type', 'contact_email', 'contact_phone', 'submitted_at')
    search_fields = ('name', 'vendor_type', 'contact_email', 'user__username')
    list_filter = ('vendor_type', 'submitted_at')
    filter_horizontal = ('certifications',)
    inlines = [RiskAssessmentInline, SecurityChecklistInline, VendorResponseInline]

# Risk Assessment Admin
@admin.register(RiskAssessment)
class RiskAssessmentAdmin(admin.ModelAdmin):
    list_display = ('vendor', 'assessment_date', 'total_risk_score', 'compliance_status', 'created_at')
    search_fields = ('vendor__name', 'compliance_status')

# Certification Admin
@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)

# Question Bank Admin
@admin.register(QuestionBank)
class QuestionBankAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'vendor_type')
    search_fields = ('question_text', 'vendor_type')
    ordering = ('question_text',)

# Checklist Template Admin
@admin.register(SecurityChecklistTemplate)
class SecurityChecklistTemplateAdmin(admin.ModelAdmin):
    list_display = ('question', 'category', 'is_critical', 'vendor_type', 'standard_required', 'compliance_standard')
    search_fields = ('question', 'category', 'vendor_type', 'compliance_standard')
    ordering = ('question',)

# Checklist Response Admin
@admin.register(SecurityChecklist)
class SecurityChecklistAdmin(admin.ModelAdmin):
    list_display = ('vendor', 'question', 'response', 'status', 'created_at')
    search_fields = ('vendor__name', 'question', 'response', 'status')
    list_filter = ('status', 'created_at')

# New Adds Below 👇

@admin.register(SecurityProfile)
class SecurityProfileAdmin(admin.ModelAdmin):
    list_display = ('vendor', 'cloud_usage', 'encryption', 'mfa', 'rbac', 'penetration_testing')
    filter_horizontal = ('certifications',)

@admin.register(OnboardingQuestionnaire)
class OnboardingQuestionnaireAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'category', 'is_mandatory')
    list_filter = ('category', 'is_mandatory')
    search_fields = ('question_text',)

@admin.register(QuestionnaireRules)
class QuestionnaireRulesAdmin(admin.ModelAdmin):
    list_display = ('vendor_type', 'category', 'requires_certification', 'min_employees', 'max_employees')

@admin.register(VendorResponse)
class VendorResponseAdmin(admin.ModelAdmin):
    list_display = ('vendor', 'question', 'response', 'submitted_at')
    list_filter = ('response',)
    search_fields = ('vendor__name', 'question__question_text')

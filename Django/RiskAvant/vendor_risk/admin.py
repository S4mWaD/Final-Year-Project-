from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Vendor, RiskAssessment, Certification, SecurityChecklistTemplate, QuestionBank, SecurityChecklist

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

@admin.register(RiskAssessment)
class RiskAssessmentAdmin(admin.ModelAdmin):
    list_display = ('vendor', 'assessment_date', 'total_risk_score', 'compliance_status', 'created_at')
    search_fields = ('vendor__name', 'compliance_status')

@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(QuestionBank)
class QuestionBankAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'vendor_type')
    search_fields = ('question_text', 'vendor_type')
    ordering = ('question_text',)

@admin.register(SecurityChecklistTemplate)
class SecurityChecklistTemplateAdmin(admin.ModelAdmin):
    list_display = ('question', 'category', 'is_critical', 'vendor_type', 'standard_required', 'compliance_standard')
    search_fields = ('question', 'category', 'vendor_type', 'compliance_standard')
    ordering = ('question',)

@admin.register(SecurityChecklist)
class SecurityChecklistAdmin(admin.ModelAdmin):
    list_display = ('vendor', 'question', 'response', 'status', 'created_at')
    search_fields = ('vendor__name', 'question', 'response', 'status')
    list_filter = ('status', 'created_at')
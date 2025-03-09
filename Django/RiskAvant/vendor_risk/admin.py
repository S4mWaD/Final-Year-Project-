from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Vendor, RiskAssessment, Certification, SecurityProfile

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
    list_display = ('vendor', 'assessment_date', 'risk_score', 'compliance_status', 'created_at')
    search_fields = ('vendor__name', 'compliance_status')

@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)

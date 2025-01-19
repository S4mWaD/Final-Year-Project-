from django.contrib import admin
from .models import *


# Register your models here.
admin.site.register(Vendor)
admin.site.register(RiskAssessment)
admin.site.register(Questionnaire)
admin.site.register(VendorResponse)


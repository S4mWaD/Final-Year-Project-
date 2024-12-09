from django.db import models

# Risk-Assessment Results
class risk_scoring(models.Model):
    #creating a sample risk register
    risk_id = models.AutoField(primary_key=True)
    risk_score = models.IntegerField()
    risk_description = models.CharField(max_length=100)
    risk_category = models.CharField(max_length=100)    

    def __str__(self):
        return self.risk_description

class vendor(models.Model):
    #creating a sample vendor register
    vendor_id = models.AutoField(primary_key=True)
    vendor_name = models.CharField(max_length=100)
    vendor_address = models.CharField(max_length=100)
    vendor_email = models.EmailField(max_length=100)
    vendor_phone = models.CharField(max_length=100)
    vendor_compliance_status = models.CharField(max_length=100)

    def __str__(self):
        return self.vendor_name


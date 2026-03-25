from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

# Create your models here.

class Project(models.Model):
    name = models.CharField(max_length=100)
    number = models.CharField(max_length=100)
    type = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    size = models.CharField(max_length=100)

    declaration_date = models.DateField()
    completion_date = models.DateField()
    start_date = models.DateField()
    end_date = models.DateField()

    process_step = models.CharField(max_length=100)
    applicant = models.CharField(max_length=100)


class Volunteer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = PhoneNumberField(blank=True)

    date_of_work = models.DateField()
    total_hours = models.IntegerField()
    location_volunteered = models.CharField(max_length=100)
    work_desc = models.TextField(max_length=500)

    equipment_used = models.BooleanField(default=False)
    equipment_type = models.CharField(max_length=100, blank=True, null=True)
    equipment_make_model = models.CharField(max_length=100, blank=True, null=True)
    equipment_hours = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)

    notes = models.TextField(max_length=500)
    flagged = models.BooleanField(default=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)


class Donations(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = PhoneNumberField()
    
    date_of_donation = models.DateField()
    total_hours = models.IntegerField(max_length=100)
    location_donated = models.CharField(max_length=100)
    
    work_desc = models.TextField(max_length=500)
    notes = models.TextField(max_length=500)
    DONATION_TYPES = [
        ('material', 'Material'),
        ('equipment', 'Equipment'),
        ('other', 'Other'),
    ]
    donation_type = models.CharField(max_length=50, choices=DONATION_TYPES)
    material_type = models.CharField(max_length=100, blank=True, null=True)
    equipment_type = models.CharField(max_length=100, blank=True, null=True)

    flagged = models.BooleanField(default=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

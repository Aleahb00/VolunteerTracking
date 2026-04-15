from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from safedelete.models import SafeDeleteModel, SOFT_DELETE
from  django.core.validators import MaxValueValidator


# Create your models here.

class Disaster(models.Model):
    name = models.CharField(max_length=100)
    number = models.CharField(max_length=100)
    type = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    size = models.CharField(max_length=100)
    hourly_rate = models.DecimalField(max_digits=6, decimal_places=2, default=29.95, help_text="Hourly volunteer rate for this state/county")
    skilled_hourly_rate = models.DecimalField(max_digits=6, decimal_places=2, default=45.00, help_text="Hourly rate for skilled volunteers for this state/county")
    declaration_date = models.DateField()
    completion_date = models.DateField()
    start_date = models.DateField()
    end_date = models.DateField()
    location = models.CharField(max_length=100, blank=True, null=True)
    process_step = models.CharField(max_length=100)
    applicant = models.CharField(max_length=100)
    goal = models.BigIntegerField(default=0)
    active = models.BooleanField(default=True)


class Volunteer(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE

    FLAG_INVALID_LOCATION = 'Invalid Location'
    FLAG_CHECKBOX = 'Checked unsure for skilled worker'

    EQUIPMENT_CHOICES = [
        ('chainsaw', 'Chainsaw'),
        ('pole_saw', 'Pole Saw'),
        ('shovel', 'Shovel'),
        ('rake', 'Rake'),
        ('wheelbarrow', 'Wheelbarrow'),
        ('generator', 'Generator'),
        ('extension_cords', 'Extension Cords'),
        ('shop_vac', 'Shop Vac / Wet-Dry Vacuum'),
        ('pressure_washer', 'Pressure Washer'),
        ('truck', 'Truck'),
        ('trailer', 'Trailer'),
        ('atv', 'ATV / UTV'),
        ('ladder', 'Ladder'),
        ('drill_tools', 'Power Tools'),
        ('hand_tools', 'Hand Tools'),
        ('tarps', 'Tarps'),
        ('safety_gear', 'Safety Gear'),
        ('none', 'None'),
        ('other', 'Other'),
    ]
    
    SKILL_OPTIONS = [
        ('yes', 'Yes'),
        ('no', 'No'),
        ('unsure', 'Unsure'),
    ]
    FLAGGED_OPTIONS = [
        FLAG_INVALID_LOCATION,
        FLAG_CHECKBOX,
    ]
    CONTACT_CHOICES = [
        ('email', 'Email'),
        ('phone', 'Phone')
    ]
    name = models.CharField(max_length=100)
    contact_method = models.CharField(max_length=10, choices=CONTACT_CHOICES)
    email = models.EmailField(blank=True)
    phone_number = PhoneNumberField(blank=True)

    date_of_work = models.DateField()
    total_hours = models.IntegerField(validators=[MaxValueValidator(18)])
    location_volunteered = models.CharField(max_length=100)
    work_desc = models.TextField(max_length=500)

    equipment = models.CharField(max_length=50,choices=EQUIPMENT_CHOICES,blank=True,null=True)

    other_equipment = models.CharField(max_length=100,blank=True,null=True)

    equipment_make_model = models.CharField(max_length=100, blank=True, null=True)
    equipment_hours = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    skilled_worker = models.CharField(max_length=10, choices=SKILL_OPTIONS, null=True)
    confirmed_skilled_worker = models.BooleanField(default=False)

    notes = models.TextField(max_length=500, blank=True)
    flagged = models.BooleanField(default=False)
    flagged_reason = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    disaster = models.ForeignKey(Disaster, on_delete=models.CASCADE, blank=True, null=True)


class Donations(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE    

    FLAG_INVALID_LOCATION = 'Invalid Location'
    FLAG_CHECKBOX = 'Checked unsure for skilled worker'

    CONTACT_CHOICES = [
        ('email', 'Email'),
        ('phone', 'Phone')
        ]
    
    SKILL_OPTIONS = [
        ('yes', 'Yes'),
        ('no', 'No'),
        ('unsure', 'Unsure'),
    ]
    FLAGGED_OPTIONS = [
        FLAG_INVALID_LOCATION,
        FLAG_CHECKBOX,
    ]
    DONATION_TYPES = [
        ('material', 'Material'),
        ('equipment', 'Equipment'),
        ('money', 'Money'),
        ('other', 'Other'),
    ]
    name = models.CharField(max_length=100)
    contact_method = models.CharField(max_length=10, choices=CONTACT_CHOICES)
    email = models.EmailField(blank=True)
    phone_number = PhoneNumberField(blank=True)
    date_of_donation = models.DateField()
    total_hours = models.IntegerField(validators=[MaxValueValidator(18)])
    location_donated = models.CharField(max_length=100)
    work_desc = models.TextField(max_length=500)
    notes = models.TextField(max_length=500, blank=True)
    other_donation_type = models.CharField(max_length=100, blank=True, null=True)
    donation_type = models.CharField(max_length=50, choices=DONATION_TYPES)
    material_type = models.CharField(max_length=100, blank=True, null=True)
    equipment_type = models.CharField(max_length=100, blank=True, null=True)
    money_donated = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, validators=[MaxValueValidator(999999.99)])
    created_at = models.DateTimeField(auto_now_add=True)
    flagged = models.BooleanField(default=False)
    flagged_reason = models.JSONField(blank=True, null=True)
    disaster = models.ForeignKey(Disaster, on_delete=models.CASCADE, blank=True, null=True)

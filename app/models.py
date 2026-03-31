from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from safedelete.models import SafeDeleteModel, SOFT_DELETE


# Create your models here.

class Project(models.Model):
    name = models.CharField(max_length=100)
    number = models.CharField(max_length=100)
    type = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    size = models.CharField(max_length=100)
    hourly_rate = models.DecimalField(max_digits=6, decimal_places=2, default=29.95, help_text="Hourly volunteer rate for this state/county")
    declaration_date = models.DateField()
    completion_date = models.DateField()
    start_date = models.DateField()
    end_date = models.DateField()
    location = models.CharField(max_length=100, blank=True, null=True)
    process_step = models.CharField(max_length=100)
    applicant = models.CharField(max_length=100)


class Volunteer(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE

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
        ('first_aid', 'First Aid Kit'),
        ('none', 'None'),
        ('other', 'Other'),
    ]

    name = models.CharField(max_length=100)
    CONTACT_CHOICES = [
        ('email', 'Email'),
        ('phone', 'Phone')
        ]
    contact_method = models.CharField(max_length=10, choices=CONTACT_CHOICES)
    email = models.EmailField(blank=True)
    phone_number = PhoneNumberField(blank=True)

    date_of_work = models.DateField()
    total_hours = models.IntegerField()
    location_volunteered = models.CharField(max_length=100)
    work_desc = models.TextField(max_length=500)

    equipment = models.CharField(max_length=50,choices=EQUIPMENT_CHOICES,blank=True,null=True)

    other_equipment = models.CharField(max_length=100,blank=True,null=True)

    equipment_make_model = models.CharField(max_length=100, blank=True, null=True)
    equipment_hours = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    # equipment_used = models.BooleanField(default=False)


    notes = models.TextField(max_length=500, blank=True)
    flagged = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, blank=True, null=True)


class Donations(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE
    name = models.CharField(max_length=100)
    
    CONTACT_CHOICES = [
        ('email', 'Email'),
        ('phone', 'Phone')
        ]
    contact_method = models.CharField(max_length=10, choices=CONTACT_CHOICES)
    email = models.EmailField(blank=True)
    phone_number = PhoneNumberField(blank=True)
    
    date_of_donation = models.DateField()
    total_hours = models.IntegerField()
    location_donated = models.CharField(max_length=100)
    
    work_desc = models.TextField(max_length=500)
    notes = models.TextField(max_length=500, blank=True)
    DONATION_TYPES = [
        ('material', 'Material'),
        ('equipment', 'Equipment'),
        ('other', 'Other'),
    ]
    # do we need other as an option for donation type? not against it but if this was intentional we need an if other please specifiy field.
    donation_type = models.CharField(max_length=50, choices=DONATION_TYPES)
    material_type = models.CharField(max_length=100, blank=True, null=True)
    equipment_type = models.CharField(max_length=100, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    flagged = models.BooleanField(default=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, blank=True, null=True)

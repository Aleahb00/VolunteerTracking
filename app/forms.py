from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from rapidfuzz import fuzz
from .models import *


class RegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, label='First Name', required=True)
    last_name = forms.CharField(max_length=30, label='Last Name', required=True)
    username = forms.CharField(max_length=40, label='Username', required=True)
    email = forms.EmailField(required=True)
    
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'username', 'email', 'password1', 'password2')


class DisasterForm(forms.ModelForm):
    class Meta:
        model = Disaster
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'text'}),
            
            'number': forms.NumberInput(attrs={
                'class': 'form-control',
                'type': 'number'}),
            
            'type': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'text'}),
            
            'category': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'text'}),
            
            'size': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'text'}),
            
            'declaration_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'}),
            
            'completion_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'}),
            
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'}),
            
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'}),
            
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'text'}),
            
            'process_step': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'text'}),
            
            'applicant': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'text'}),
        }
            


class VolunteerForm(forms.ModelForm):
    class Meta:
        model = Volunteer
        fields = ['name', 'contact_method', 'email', 'phone_number', 'date_of_work', 'total_hours', 'location_volunteered', 'work_desc', 'equipment', 'other_equipment', 'equipment_make_model', 'equipment_hours', 'skilled_worker', 'notes']
        exclude = ['active']
        labels = {
            'name': 'Full Name',
            'contact_method': 'Contact Method',
            'email': 'Email Address',
            'phone_number': 'Phone Number',
            'date_of_work': 'Date of Work',
            'total_hours': 'Total Hours Volunteered',
            'location_volunteered': 'Location Volunteered',
            'work_desc': 'Description of Work',
            'equipment': 'Equipment Used',
            'other_equipment': 'Other Equipment (if applicable)',
            'equipment_make_model': 'Equipment Make/Model',
            'equipment_hours': 'Hours Equipment Used',
            'skilled_worker': 'Skilled Worker',
            'notes': 'Additional Notes',
            }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'text'}),
            
            'contact_method': forms.Select(attrs={
                'class': 'form-control',
                'type': 'select'}),
            
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'type': 'email'}),
            
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'text'}),
            
            'date_of_work': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'}),
            
            
            'total_hours': forms.NumberInput(attrs={
                'class': 'form-control',
                'type': 'number'}),
            
            'location_volunteered': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'text'}),
            
            'work_desc': forms.Textarea(attrs={
                'class': 'form-control',
                'type': 'text'}),
            
            'equipment': forms.Select(attrs={
                'class': 'form-control',
                'id': 'equipment-select'
            }),

            'other_equipment': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'other-equipment',
                'placeholder': 'Please specify'
            }),
            
            'equipment_make_model': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'text'}),
            
            'equipment_hours': forms.NumberInput(attrs={
                'class': 'form-control',
                'type': 'number'}),
            
            'skilled_worker': forms.RadioSelect(attrs={
                'class': 'radio-input'
            }),
            
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'type': 'text'}),
        }

    def clean_date_of_work(self):
        user_date = self.cleaned_data.get('date_of_work')

        from django.db.models import Min
        from django.core.exceptions import ValidationError

        earliest_date = Disaster.objects.aggregate(Min('start_date'))['start_date__min']

        if earliest_date and user_date and user_date < earliest_date:
            raise ValidationError('Date cannot be before earliest disaster date')

        return user_date
    
    def clean(self):
        cleaned_data = super().clean()
        flags = []

        location = (cleaned_data.get('location_volunteered') or '').strip()
        skilled_worker = (cleaned_data.get('skilled_worker') or '').strip().lower()

        min_similarity = 80
        disaster_locations = Disaster.objects.filter(active=True).exclude(location__isnull=True).exclude(location__exact='').values_list('location', flat=True)

        best_similarity = max(
            (fuzz.ratio(location.lower(), disaster_location.lower()) for disaster_location in disaster_locations),default=0)

        if location and best_similarity < min_similarity:
            flags.append(Volunteer.FLAG_INVALID_LOCATION)
        if skilled_worker == 'unsure':
            flags.append(Volunteer.FLAG_CHECKBOX)

        cleaned_data['flagged_reason'] = flags
        cleaned_data['is_flagged'] = bool(flags)
        cleaned_data['location_similarity'] = best_similarity
        return cleaned_data

class DonationForm(forms.ModelForm):
    class Meta:
        model = Donations
        fields = ['name', 'contact_method', 'email', 'phone_number', 'date_of_donation', 'total_hours', 'location_donated', 'work_desc', 'notes', 'donation_type', 'material_type', 'equipment_type', 'other_donation_type', 'money_donated']
        labels = {
            'name': 'Full Name',
            'contact_method': 'Contact Method',
            'email': 'Email Address',
            'phone_number': 'Phone Number',
            'date_of_donation': 'Date of Donation',
            'total_hours': 'Total Hours Donated',
            'location_donated': 'Location Donated',
            'work_desc': 'Description of Work',
            'notes': 'Additional Notes',
            'donation_type': 'Donation Type',
            'other_donation_type': 'Other Donation Type (if applicable)',
            'material_type': 'Material Type',
            'equipment_type': 'Equipment Type',
            'money_donated': 'Amount Donated'
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'text'}),
            
            'contact_method': forms.Select(attrs={
                'class': 'form-control',
                'type': 'select'}),
            
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'type': 'email',
                'required': False}),
            
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'text',
                'required': False}),
            
            'date_of_donation': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'}),
            
            'total_hours': forms.NumberInput(attrs={
                'class': 'form-control',
                'type': 'number'}),
            
            'location_donated': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'text'}),
            
            'work_desc': forms.Textarea(attrs={
                'class': 'form-control',
                'type': 'text'}),
            
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'type': 'text'}),
            
            'donation_type': forms.Select(attrs={
                'class': 'form-control',
                'type': 'select'}),
            
            'material_type': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'text'}),
            
            'equipment_type': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'text'}),
            
            'money_donated': forms.NumberInput(attrs={
                'class': 'form-control',
                'type': 'number'}),
            
            'other_donation_type': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'text'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        contact_method = cleaned_data.get('contact_method')
        email = cleaned_data.get('email')
        phone_number = cleaned_data.get('phone_number')

        if contact_method == 'email':
            if not email:
                self.add_error('email', 'Email is required when contact method is Email.')
            cleaned_data['phone_number'] = ''
        elif contact_method == 'phone':
            if not phone_number:
                self.add_error('phone_number', 'Phone number is required when contact method is Phone.')
            cleaned_data['email'] = ''

        # Compute flagged_reason for donations
        flags = []
        location = (cleaned_data.get('location_donated') or '').strip()
        
        min_similarity = 80
        disaster_locations = Disaster.objects.filter(active=True).exclude(location__isnull=True).exclude(location__exact='').values_list('location', flat=True)
        
        best_similarity = max(
            (fuzz.ratio(location.lower(), disaster_location.lower()) for disaster_location in disaster_locations),
            default=0)
        
        if location and best_similarity < min_similarity:
            flags.append(Donations.FLAG_INVALID_LOCATION)
        
        cleaned_data['flagged_reason'] = flags
        cleaned_data['is_flagged'] = bool(flags)
        cleaned_data['location_similarity'] = best_similarity

        return cleaned_data

    def clean_date_of_donation(self):
        user_date = self.cleaned_data.get('date_of_donation')

        from django.db.models import Min
        from django.core.exceptions import ValidationError

        earliest_date = Disaster.objects.aggregate(Min('start_date'))['start_date__min']

        if earliest_date and user_date and user_date < earliest_date:
            raise ValidationError('Date cannot be before earliest disaster date')

        return user_date
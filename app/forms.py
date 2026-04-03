from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import *


class RegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, label='First Name', required=True)
    last_name = forms.CharField(max_length=30, label='Last Name', required=True)
    username = forms.CharField(max_length=40, label='Username', required=True)
    email = forms.EmailField(required=True)
    
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'username', 'email', 'password1', 'password2')


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={
                'class' : 'unknown',
                'type': 'text'}),
            
            'number': forms.NumberInput(attrs={
                'class' : 'unknown',
                'type': 'number'}),
            
            'type': forms.TextInput(attrs={
                'class' : 'unknown',
                'type': 'text'}),
            
            'category': forms.TextInput(attrs={
                'class' : 'unknown',
                'type': 'text'}),
            
            'size': forms.TextInput(attrs={
                'class' : 'unknown',
                'type': 'text'}),
            
            'declaration_date': forms.DateInput(attrs={
                'class' : 'unknown',
                'type': 'date'}),
            
            'completion_date': forms.DateInput(attrs={
                'class' : 'unknown',
                'type': 'date'}),
            
            'start_date': forms.DateInput(attrs={
                'class' : 'unknown',
                'type': 'date'}),
            
            'end_date': forms.DateInput(attrs={
                'class' : 'unknown',
                'type': 'date'}),
            
            'location': forms.TextInput(attrs={
                'class' : 'unknown',
                'type': 'text'}),
            
            'process_step': forms.TextInput(attrs={
                'class' : 'unknown',
                'type': 'text'}),
            
            'applicant': forms.TextInput(attrs={
                'class' : 'unknown',
                'type': 'text'}),
        }
            


class VolunteerForm(forms.ModelForm):
    class Meta:
        model = Volunteer
        fields = ['name', 'contact_method', 'email', 'phone_number', 'date_of_work', 'total_hours', 'location_volunteered', 'work_desc', 'equipment', 'other_equipment', 'equipment_make_model', 'equipment_hours', 'skilled_worker', 'notes']
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
                'class' : 'unknown',
                'type': 'text'}),
            
            'contact_method': forms.Select(attrs={
                'class' : 'unknown',
                'type': 'select'}),
            
            'email': forms.EmailInput(attrs={
                'class' : 'unknown',
                'type': 'email'}),
            
            'phone_number': forms.TextInput(attrs={
                'class' : 'unknown',
                'type': 'text'}),
            
            'date_of_work': forms.DateInput(attrs={
                'class' : 'unknown',
                'type': 'date'}),
            
            
            'total_hours': forms.NumberInput(attrs={
                'class' : 'unknown',
                'type': 'number'}),
            
            'location_volunteered': forms.TextInput(attrs={
                'class' : 'unknown',
                'type': 'text'}),
            
            'work_desc': forms.Textarea(attrs={
                'class' : 'unknown',
                'type': 'text'}),
            
            'equipment': forms.Select(attrs={
                'class': 'unknown',
                'id': 'equipment-select'
            }),

            'other_equipment': forms.TextInput(attrs={
                'class': 'unknown',
                'id': 'other-equipment',
                'placeholder': 'Please specify'
            }),
            
            'equipment_make_model': forms.TextInput(attrs={
                'class' : 'unknown',
                'type': 'text'}),
            
            'equipment_hours': forms.NumberInput(attrs={
                'class' : 'unknown',
                'type': 'number'}),
            
            'skilled_worker': forms.RadioSelect(attrs={
                'class': 'radio-input'
            }),
            
            'notes': forms.Textarea(attrs={
                'class' : 'unknown',
                'type': 'text'}),
        }

    def clean_date_of_work(self):
        user_date = self.cleaned_data.get('date_of_work')

        from django.db.models import Min
        from django.core.exceptions import ValidationError

        earliest_date = Project.objects.aggregate(Min('start_date'))['start_date__min']

        if earliest_date and user_date and user_date < earliest_date:
            raise ValidationError('Date cannot be before earliest project date')

        return user_date


class DonationForm(forms.ModelForm):
    class Meta:
        model = Donations
        fields = ['name', 'contact_method', 'email', 'phone_number', 'date_of_donation', 'total_hours', 'location_donated', 'work_desc', 'notes', 'donation_type', 'material_type', 'equipment_type']
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
            'material_type': 'Material Type',
            'equipment_type': 'Equipment Type',
            'skilled_worker': 'Skilled Worker',
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'class' : 'unknown',
                'type': 'text'}),
            
            'contact_method': forms.Select(attrs={
                'class' : 'unknown',
                'type': 'select'}),
            
            'email': forms.EmailInput(attrs={
                'class' : 'unknown',
                'type': 'email',
                'required': False}),
            
            'phone_number': forms.TextInput(attrs={
                'class' : 'unknown',
                'type': 'text',
                'required': False}),
            
            'date_of_donation': forms.DateInput(attrs={
                'class' : 'unknown',
                'type': 'date'}),
            
            'total_hours': forms.NumberInput(attrs={
                'class' : 'unknown',
                'type': 'number'}),
            
            'location_donated': forms.TextInput(attrs={
                'class' : 'unknown',
                'type': 'text'}),
            
            'work_desc': forms.Textarea(attrs={
                'class' : 'unknown',
                'type': 'text'}),
            
            'notes': forms.Textarea(attrs={
                'class' : 'unknown',
                'type': 'text'}),
            
            'donation_type': forms.Select(attrs={
                'class' : 'unknown',
                'type': 'select'}),
            
            'material_type': forms.TextInput(attrs={
                'class' : 'unknown',
                'type': 'text'}),
            
            'equipment_type': forms.TextInput(attrs={
                'class' : 'unknown',
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

        return cleaned_data

    def clean_date_of_donation(self):
        user_date = self.cleaned_data.get('date_of_donation')

        from django.db.models import Min
        from django.core.exceptions import ValidationError

        earliest_date = Project.objects.aggregate(Min('start_date'))['start_date__min']

        if earliest_date and user_date and user_date < earliest_date:
            raise ValidationError('Date cannot be before earliest project date')

        return user_date
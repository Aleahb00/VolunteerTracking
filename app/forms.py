from django import forms
from .models import *




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
        fields = fields = ['name', 'email', 'phone_number', 'date_of_work', 'total_hours', 'location_volunteered', 'work_desc', 'equipment', 'other_equipment', 'equipment_make_model', 'equipment_hours', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={
                'class' : 'unknown',
                'type': 'text'}),
            
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
            
            # 'equipment_used': forms.CheckboxInput(attrs={
            #     'class' : 'unknown',
            #     'type': 'checkbox'}),
            
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
            
            'notes': forms.Textarea(attrs={
                'class' : 'unknown',
                'type': 'text'}),
        }


class DonationForm(forms.ModelForm):
    class Meta:
        model = Donations
        fields = ['name', 'email', 'phone_number', 'date_of_donation', 'total_hours', 'location_donated', 'work_desc', 'notes', 'donation_type', 'material_type', 'equipment_type']
        widgets = {
            'name': forms.TextInput(attrs={
                'class' : 'unknown',
                'type': 'text'}),
            
            'email': forms.EmailInput(attrs={
                'class' : 'unknown',
                'type': 'email'}),
            
            'phone_number': forms.TextInput(attrs={
                'class' : 'unknown',
                'type': 'text'}),
            
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
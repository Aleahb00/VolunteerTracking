from django.shortcuts import render, redirect, get_object_or_404
from django.http.response import HttpResponse
from django.http.request import HttpRequest
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from django.core.exceptions import PermissionDenied
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import *
from django.contrib import messages
from django.db.models import Q
from .models import *
from .forms import *
from .forms import ProjectForm, VolunteerForm, DonationForm
from django.template.loader import get_template
import re

# Create your views here.

# NOTE CLIENT SIDE VIEWS
def landing_view(request:HttpRequest)->HttpResponse:
    return render(request, 'landing.html')

def error_view(request:HttpRequest)->HttpResponse:
    return render(request, '403.html', status=403)

def project_test_view(request:HttpRequest)->HttpResponse:
    projects = Project.objects.all()

    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('landing')
    else:
        form = ProjectForm()

    return render(request, 'temp_admin.html', {'form': form, 'projects': projects})

def form_template_view(request:HttpRequest)->HttpResponse:
    volunteerForm = VolunteerForm()
    donationForm = DonationForm()

    if request.method == 'POST':
        volunteerForm = VolunteerForm(request.POST)
        donationForm = DonationForm(request.POST)

        if volunteerForm.is_valid():
            volunteerForm.save()
            return redirect('forms')

        if donationForm.is_valid():
            donationForm.save()
            return redirect('forms')

    return render(request, 'forms.html', {
        'volunteerForm': volunteerForm,
        'donationForm': donationForm,
    })




# NOTE ADMIN SIDE VIEWS
def admin_dashboard_view(request: HttpRequest, project_id=None) -> HttpResponse:
    project = get_object_or_404(Project, id=project_id) if project_id else None
    # DELETE
    if request.method == 'POST' and request.POST.get('_method') == 'DELETE':
        if project:
            project.delete()
        return redirect('admin_dashboard')

    #  CREATE/UPDATE
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)  
        if form.is_valid():
            form.save()
            return redirect('admin_dashboard')
    else:
        form = ProjectForm(instance=project)  
    
    if project:
        volunteers = Volunteer.objects.filter(project=project)
        donations = Donations.objects.filter(project=project)
    else:
        volunteers = Volunteer.objects.all()
        donations = Donations.objects.all()

    total_submissions = volunteers.count() + donations.count()

    # READ
    return render(request, 'admin_dashboard.html', {
        'projects': Project.objects.all(),
        'volunteers': volunteers,
        'donations': donations,
        'total_submissions': total_submissions,
        'form': form,
        'project': project,  
    })


def checker_view(request:HttpRequest)->HttpResponse:
    volunteers = Volunteer.objects.all()
    projects = Project.objects.all()
    
    if request.method == 'POST':
        for project in projects:
            location = project.location
            for volunteer in volunteers:
                if not re.match(r'volunteer.location_volunteered', location):
                    volunteer.flagged = True
                    volunteer.save()

    return render(request, 'test_checker.html', {'flagged_forms': Volunteer.objects.filter(flagged=True)})

# def print_view(request, v_d_form_id):
#     pet = get_object_or_404(Project, id=v_d_form_id)
#     return render(request, 'pets.html', {'pet': pet})
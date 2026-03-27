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
import csv
from rapidfuzz import fuzz
from .functions import *
from django.db.models import Q



# Create your views here.

# NOTE CLIENT SIDE VIEWS
def landing_view(request:HttpRequest)->HttpResponse:
    return render(request, 'landing.html')


def status_403_view(request:HttpRequest)->HttpResponse:
    return render(request, '403.html', status=403)


def status_404_view(request:HttpRequest)->HttpResponse:
    return render(request, '404.html', status=404)


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
    volunteers = Volunteer.objects.all()
    projects = Project.objects.all()

    if request.method == 'POST':
        volunteerForm = VolunteerForm(request.POST)
        donationForm = DonationForm(request.POST)

        for project in projects:
            location = project.location
            for volunteer in volunteers:
                similarity = fuzz.ratio(volunteer.location_volunteered.lower(), location.lower())
                if similarity < 80:
                    volunteer.flagged = True
                    volunteer.save()

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
    # I think this function works but like its been acting funny or I might just be tripping (might need hondussy to review)




# NOTE ADMIN SIDE VIEWS
# Search query needs to be implemented into this view if this is the one that were searching on
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
    
def generate_csv(request):
    response = HttpResponse(
        content_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="submissions_export.csv"'},
    )
    writer = csv.writer(response)
    writer.writerow([
    'submission_type', 'id', 'name', 'email', 'phone_number', 'date', 'total_hours', 'location', 'work_desc', 'notes',
    # 'flagged', 'project_id', 
    'project_name', 'equipment', 'other_equipment', 'equipment_make_model', 'equipment_hours', 'donation_type', 'material_type', 'equipment_type'])

    volunteers = Volunteer.objects.select_related('project').all()
    for volunteer in volunteers:
        writer.writerow([
    'volunteer',
    volunteer.id,
    volunteer.name,
    volunteer.email,
    volunteer.phone_number,
    volunteer.date_of_work,
    volunteer.total_hours,
    volunteer.location_volunteered,
    volunteer.work_desc,
    volunteer.notes,
    # volunteer.flagged,
    # volunteer.project_id,
    volunteer.project.name if volunteer.project else '',
    volunteer.equipment,
    volunteer.other_equipment,
    volunteer.equipment_make_model,
    volunteer.equipment_hours,])

    donations = Donations.objects.select_related('project').all()
    for donation in donations:
        writer.writerow([
            'donation',
            donation.id,
            donation.name,
            donation.email,
            donation.phone_number,
            donation.date_of_donation,
            donation.total_hours,
            donation.location_donated,
            donation.work_desc,
            donation.notes,
            donation.flagged,
            donation.project_id,
            donation.project.name,
            '',
            '',
            '',
            '',
            donation.donation_type,
            donation.material_type,
            donation.equipment_type,
        ])
    return response
# this view needs to be reconfigured if we need to export donations and volunteers seperately or togeder or both options


# def print_view(request, v_d_form_id):
#     pet = get_object_or_404(Project, id=v_d_form_id)
#     return render(request, 'pets.html', {'pet': pet})
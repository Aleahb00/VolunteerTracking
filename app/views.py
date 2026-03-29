from django.shortcuts import render, redirect, get_object_or_404
from django.http.response import HttpResponse
from django.http.request import HttpRequest
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from django.core.exceptions import PermissionDenied
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import *
from django.contrib import messages
from django.db.models import Q, Min
from .models import *
from .forms import *
from .forms import ProjectForm, VolunteerForm, DonationForm
from honeypot.decorators import check_honeypot
from django_ratelimit.decorators import ratelimit
from django.template.loader import get_template
import csv
from rapidfuzz import fuzz
from .functions import *
import json
from django.http import JsonResponse




# Create your views here.

# NOTE CLIENT SIDE VIEWS
def landing_view(request:HttpRequest)->HttpResponse:
    return render(request, 'landing.html')


def status_403_view(request:HttpRequest, exception=None)->HttpResponse:
    return render(request, '403.html', status=403)


def status_404_view(request:HttpRequest, exception=None)->HttpResponse:
    return render(request, '404.html', status=404)

def ratelimit_error(request, exception=None):
    return render(request, '429.html', status=429)


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
# is this needed? where is this being used?

@check_honeypot
@ratelimit(key='ip', rate='5/m', method='POST', block=False)
def form_template_view(request:HttpRequest)->HttpResponse:
    earliest_date = Project.objects.aggregate(Min('start_date'))['start_date__min']
    volunteerForm = VolunteerForm()
    donationForm = DonationForm()
    projects = Project.objects.exclude(location__isnull=True).exclude(location__exact='')

    if request.method == 'POST' and getattr(request, 'limited', False):
        return render(request, '429.html', status=429)

    def find_best_project(location_text: str):
        best_project = None
        best_similarity = -1

        for project in projects:
            similarity = fuzz.ratio(location_text.lower(), project.location.lower())
            if similarity > best_similarity:
                best_similarity = similarity
                best_project = project

        return best_project, best_similarity

    if request.method == 'POST':
        if 'submit_volunteer' in request.POST:
            volunteerForm = VolunteerForm(request.POST)

            if volunteerForm.is_valid():
                volunteer = volunteerForm.save(commit=False)
                best_project, similarity = find_best_project(volunteer.location_volunteered)
                volunteer.flagged = similarity < 80

                if volunteer.flagged:
                    volunteer.project = None
                elif best_project:
                    volunteer.project = best_project

                volunteer.save()

                if volunteer.flagged:
                    messages.warning(request, 'Volunteer submission saved and flagged (location similarity below 80%). No project was assigned.')
                else:
                    messages.success(request, 'Volunteer form submission saved successfully.')

                return redirect('forms')

            messages.error(request, 'There was an error with the volunteer form. Please check and try again.')

        elif 'submit_donation' in request.POST:
            donationForm = DonationForm(request.POST)

            if donationForm.is_valid():
                donation = donationForm.save(commit=False)
                best_project, similarity = find_best_project(donation.location_donated)
                donation.flagged = similarity < 80

                if donation.flagged:
                    donation.project = None
                elif best_project:
                    donation.project = best_project

                donation.save()

                if donation.flagged:
                    messages.warning(request, 'Donation submission saved and flagged (location similarity below 80%). No project was assigned.')
                    flagged_reason = 'Location unrecognized.'
                    # this is broken and needs to be repiared. still trying to come up with a solution. moving on.
                else:
                    messages.success(request, 'Donation submission saved and matched to project location.')

                return redirect('forms')

            else:
                messages.error(request, 'There was an error with the donation form. Please check and try again.')

    return render(request, 'forms.html', {
        'volunteerForm': volunteerForm,
        'donationForm': donationForm,
        'earliest_date': earliest_date,
    })
    # I think this function works but like its been acting funny
    #  or I might just be tripping (might need hondussy to review)
    
    # these messages need to change currently theyre confirmation for testing but will need to be changed for users




# NOTE ADMIN SIDE VIEWS
# Search query needs to be implemented into this view if this is the one that were searching on
def register_view(request:HttpRequest)->HttpResponse:
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('admin_dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'register.html', {'form': form})


def login_view(request:HttpRequest)->HttpResponse:
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('admin_dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


def logout_view(request:HttpRequest)->HttpResponse:
    logout(request)
    return redirect('landing')
# may need to redirect to somewhere else considering it's admin

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
    
    query = request.GET.get('q')
    
    if project:
        volunteers = Volunteer.objects.filter(project=project).order_by('created_at')
        donations = Donations.objects.filter(project=project).order_by('created_at')
    else:
        volunteers = Volunteer.objects.all().order_by('created_at')
        donations = Donations.objects.all().order_by('created_at')
    
    if query:
        volunteers = volunteers.filter(
            Q(name__icontains=query) |
            Q(email__icontains=query) |
            Q(phone_number__icontains=query) |
            Q(location_volunteered__icontains=query) |
            Q(work_desc__icontains=query) |
            Q(notes__icontains=query)
        )
        donations = donations.filter(
            Q(name__icontains=query) |
            Q(email__icontains=query) |
            Q(phone_number__icontains=query) |
            Q(location_donated__icontains=query) |
            Q(work_desc__icontains=query) |
            Q(notes__icontains=query)
        )

    total_submissions = volunteers.count() + donations.count()
    create_form = ProjectForm()
    
    edit_form = ProjectForm(instance=project) if project else None
    # READ
    return render(request, 'admin_dashboard.html', {
        'projects': Project.objects.all(),
        'volunteers': volunteers,
        'donations': donations,
        'total_submissions': total_submissions,
        'create_form': create_form,
        'edit_form': edit_form,
        'project': project,  
        'query': query
    })


def toggle_flagged_status(request, volunteer_id):
    volunteer = get_object_or_404(Volunteer, id=volunteer_id)
    volunteer.flagged = not volunteer.flagged
    volunteer.save()
    return JsonResponse({'flagged': volunteer.flagged, 'status': 'success'})

def generate_volunteer_csv(request):
    response = HttpResponse(
        content_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="submissions_export.csv"'},
    )
    writer = csv.writer(response)
    writer.writerow([
    'submission_type', 'id', 'name', 'email', 'phone_number', 'date', 'total_hours', 'location', 'work_desc', 'notes',
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
    volunteer.project.name if volunteer.project else '',
    volunteer.equipment,
    volunteer.other_equipment,
    volunteer.equipment_make_model,
    volunteer.equipment_hours])
    return response


def generate_donation_csv(request):
    response = HttpResponse(
        content_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="submissions_export.csv"'},
    )
    writer = csv.writer(response)
    writer.writerow([
    'submission_type' ,'project_name', 'id', 'name', 'email', 'phone_number', 'date', 'total_hours', 'location', 'work_desc', 'notes',
    'donation_type', 'material_type', 'equipment_type'])

    donations = Donations.objects.select_related('project').all()
    for donation in donations:
        writer.writerow([
    'donation',
    donation.project.name if donation.project else '',
    donation.id,
    donation.name,
    donation.email,
    donation.phone_number,
    donation.date_of_donation,
    donation.total_hours,
    donation.location_donated,
    donation.work_desc,
    donation.notes,
    donation.donation_type,
    donation.material_type if donation.donation_type == 'material' else '',
    donation.equipment_type if donation.donation_type == 'equipment' else ''])
    return response


# def print_view(request, v_d_form_id):
#     pet = get_object_or_404(Project, id=v_d_form_id)
#     return render(request, 'pets.html', {'pet': pet})
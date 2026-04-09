from decimal import Decimal
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
from django.db.models import Sum
import json
from django.http import JsonResponse
from .filters import VolunteerFilter, DonationFilter




# Create your views here.

# NOTE CLIENT SIDE VIEWS
def landing_view(request:HttpRequest)->HttpResponse:
    return render(request, 'landing.html')

def faq_view(request:HttpRequest)->HttpResponse:
    return render(request, 'faq.html')

def status_403_view(request:HttpRequest, exception=None)->HttpResponse:
    return render(request, '403.html', status=403)

def status_404_view(request:HttpRequest, exception=None)->HttpResponse:
    return render(request, '404.html', status=404)

def status_429_view(request:HttpRequest, exception=None)->HttpResponse:
    return render(request, '429.html', status=429)

def status_500_view(request:HttpRequest)->HttpResponse:
    return render(request, '500.html', status=500)

def ratelimit_error(request, exception=None):
    return render(request, '429.html', status=429)


# def project_test_view(request:HttpRequest)->HttpResponse:
#     projects = Project.objects.all()

#     if request.method == 'POST':
#         form = ProjectForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('landing')
#     else:
#         form = ProjectForm()

#     return render(request, 'temp_admin.html', {'form': form, 'projects': projects})
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
            if project.active:
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
                flag_reasons = volunteerForm.cleaned_data.get('flagged_reason', [])
                volunteer.flagged_reason = flag_reasons
                volunteer.flagged = bool(flag_reasons)
                if volunteer.skilled_worker == 'yes':
                    volunteer.confirmed_skilled_worker = True

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
                flag_reasons = donationForm.cleaned_data.get('flagged_reason', [])
                donation.flagged_reason = flag_reasons
                donation.flagged = bool(flag_reasons)

                if donation.flagged:
                    donation.project = None
                elif best_project:
                    donation.project = best_project

                donation.save()

                if donation.flagged:
                    messages.warning(request, 'Donation submission saved and flagged (location similarity below 80%). No project was assigned.')
                else:
                    messages.success(request, 'Donation form submission saved successfully.')

                return redirect('forms')

            else:
                messages.error(request, 'There was an error with the donation form. Please check and try again.')

    return render(request, 'forms.html', {
        'volunteerForm': volunteerForm,
        'donationForm': donationForm,
        'earliest_date': earliest_date,
    })

    
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
    active_tab = request.GET.get('active_tab', 'volunteers-panel')
    

    # DELETE
    if request.method == 'POST' and request.POST.get('_method') == 'DELETE':
        if project:
            project.delete()
        return redirect('admin_dashboard', )
    # think this needs to be deleted because you cant delete projects just close them but maybe it should still be an option? //COW//

    # CREATE/UPDATE
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect('admin_dashboard', )
    else:
        form = ProjectForm(instance=project)

        form = ProjectForm(instance=project)  
    
    query = request.GET.get('q')

    if project:
        volunteers = Volunteer.objects.filter(project=project).order_by('-created_at')
        donations = Donations.objects.filter(project=project).order_by('-created_at')
    else:
        volunteers = Volunteer.objects.all().order_by('-created_at')
        donations = Donations.objects.all().order_by('-created_at')

    # Keep dedicated flagged querysets so filters/sorts from other tabs do not leak into flagged tab.
    flagged_volunteers = volunteers.filter(flagged=True)
    flagged_donations = donations.filter(flagged=True)

    if query and active_tab == 'volunteers-panel':
        volunteers = volunteers.filter(
            Q(name__icontains=query) |
            Q(email__icontains=query) |
            Q(phone_number__icontains=query) |
            Q(location_volunteered__icontains=query) |
            Q(work_desc__icontains=query) |
            Q(notes__icontains=query)
        )
    elif query and active_tab == 'donations-panel':
        donations = donations.filter(
            Q(name__icontains=query) |
            Q(email__icontains=query) |
            Q(phone_number__icontains=query) |
            Q(location_donated__icontains=query) |
            Q(work_desc__icontains=query) |
            Q(notes__icontains=query)
        )

    volunteer_filter = VolunteerFilter(request.GET, queryset=volunteers, prefix='volunteer')
    donation_filter = DonationFilter(request.GET, queryset=donations, prefix='donation')

    if active_tab == 'volunteers-panel':
        volunteers = volunteer_filter.qs
    if active_tab == 'donations-panel':
        donations = donation_filter.qs

    volunteer_count = volunteers.count()
    donation_count = donations.count()
    total_submissions = volunteer_count + donation_count

    hourly_rate = project.hourly_rate if project else Decimal('29.95')
    skilled_hourly_rate = project.skilled_hourly_rate if project else Decimal('45.00')

    # Price volunteer labor using confirmed skilled status only.
    confirmed_skilled_hours = volunteers.filter(confirmed_skilled_worker=True).aggregate(total=Sum('total_hours'))['total'] or 0
    non_skilled_hours = volunteers.filter(confirmed_skilled_worker=False).aggregate(total=Sum('total_hours'))['total'] or 0

    total_hours = volunteers.aggregate(total=Sum('total_hours'))['total'] or 0
    volunteer_value = (
        Decimal(str(non_skilled_hours)) * hourly_rate
        + Decimal(str(confirmed_skilled_hours)) * skilled_hourly_rate
    )
    flagged_count = volunteers.filter(flagged=True).count()
    donation_flagged_count = donations.filter(flagged=True).count()

    # Compute donation value from donated hours using project's hourly_rate
    donation_hours_total = donations.aggregate(total=Sum('total_hours'))['total'] or 0
    donation_value = Decimal(str(donation_hours_total)) * hourly_rate
    total_value = volunteer_value + donation_value

    create_form = ProjectForm()
    edit_form = ProjectForm(instance=project) if project else None
    deleted_volunteers = Volunteer.all_objects.filter(deleted__isnull=False).order_by('-created_at')
    deleted_donations = Donations.all_objects.filter(deleted__isnull=False).order_by('-created_at')

    # READ
    return render(request, 'admin_dashboard.html', {
        'projects': Project.objects.all(),
        'volunteers': volunteers,
        'donations': donations,
        'volunteer_count': volunteer_count,
        'donation_count': donation_count,
        'total_submissions': total_submissions,
        'create_form': create_form,
        'edit_form': edit_form,
        'project': project,
        'total_hours': total_hours,
        'volunteer_value': volunteer_value,
        'donation_value': donation_value,
        'total_value': total_value,
        'query': query,
        'hourly_rate': hourly_rate,
        'flagged_count': flagged_count,
        'donation_flagged_count': donation_flagged_count,
        'flagged_volunteers': flagged_volunteers,
        'flagged_donations': flagged_donations,
        'deleted_volunteers': deleted_volunteers,
        'deleted_donations': deleted_donations,
        'volunteer_filter': volunteer_filter,
        'donation_filter': donation_filter,
        'active_tab': active_tab,
    })
    
def submissions_full_view(request: HttpRequest, project_id=None) -> HttpResponse:
    project = get_object_or_404(Project, id=project_id) if project_id else None
    active_tab = request.GET.get('active_tab', 'volunteer-panel')
    query = request.GET.get('q')

    if project:
        volunteers = Volunteer.objects.filter(project=project).select_related('project').order_by('-created_at')
        donations = Donations.objects.filter(project=project).select_related('project').order_by('-created_at')
    else:
        volunteers = Volunteer.objects.select_related('project').order_by('-created_at')
        donations = Donations.objects.select_related('project').order_by('-created_at')

    if query and active_tab == 'volunteer-panel':
        volunteers = volunteers.filter(
            Q(name__icontains=query) |
            Q(email__icontains=query) |
            Q(phone_number__icontains=query) |
            Q(location_volunteered__icontains=query) |
            Q(work_desc__icontains=query) |
            Q(notes__icontains=query)
        )
    elif query and active_tab == 'donation-panel':
        donations = donations.filter(
            Q(name__icontains=query) |
            Q(email__icontains=query) |
            Q(phone_number__icontains=query) |
            Q(location_donated__icontains=query) |
            Q(work_desc__icontains=query) |
            Q(notes__icontains=query)
        )

    volunteer_filter = VolunteerFilter(request.GET, queryset=volunteers, prefix='volunteer')
    donation_filter = DonationFilter(request.GET, queryset=donations, prefix='donation')

    if active_tab == 'volunteer-panel':
        volunteers = volunteer_filter.qs
    elif active_tab == 'donation-panel':
        donations = donation_filter.qs


    return render(request, 'submissions_full.html', {
        'project': project,
        'active_tab': active_tab,
        'query': query,
        'volunteers': volunteers,
        'donations': donations,
        'volunteer_filter': volunteer_filter,
        'donation_filter': donation_filter,
    })

def general_dashboard_view(request:HttpRequest)->HttpResponse:
    active_tab = request.GET.get('active_tab', 'volunteer-panel')
    search_query = (request.GET.get('q') or '').strip()
    projects = Project.objects.filter(active=True).select_related()
    base_flagged_volunteers = Volunteer.objects.filter(flagged=True).select_related('project').order_by('-created_at')
    base_flagged_donations = Donations.objects.filter(flagged=True).select_related('project').order_by('-created_at')
    flagged_volunteers = base_flagged_volunteers
    flagged_donations = base_flagged_donations
    deleted_volunteers = Volunteer.all_objects.filter(deleted__isnull=False, project__isnull=True).order_by('-created_at')
    deleted_donations = Donations.all_objects.filter(deleted__isnull=False, project__isnull=True).order_by('-created_at')

    # Keep tab badge counts stable and independent from current filter/search state.
    flagged_volunteers_count = base_flagged_volunteers.count()
    flagged_donations_count = base_flagged_donations.count()

    volunteer_filter = VolunteerFilter(request.GET, queryset=flagged_volunteers, prefix='volunteer')
    donation_filter = DonationFilter(request.GET, queryset=flagged_donations, prefix='donation')

    if active_tab == 'volunteer-panel':
        flagged_volunteers = volunteer_filter.qs.filter(flagged=True)
        if search_query:
            flagged_volunteers = flagged_volunteers.filter(
                Q(name__icontains=search_query)
                | Q(email__icontains=search_query)
                | Q(phone_number__icontains=search_query)
                | Q(location_volunteered__icontains=search_query)
                | Q(work_desc__icontains=search_query)
                | Q(notes__icontains=search_query)
                | Q(project__name__icontains=search_query)
            )
    elif active_tab == 'donation-panel':
        flagged_donations = donation_filter.qs.filter(flagged=True)
        if search_query:
            flagged_donations = flagged_donations.filter(
                Q(name__icontains=search_query)
                | Q(email__icontains=search_query)
                | Q(phone_number__icontains=search_query)
                | Q(location_donated__icontains=search_query)
                | Q(work_desc__icontains=search_query)
                | Q(notes__icontains=search_query)
                | Q(material_type__icontains=search_query)
                | Q(equipment_type__icontains=search_query)
                | Q(other_donation_type__icontains=search_query)
                | Q(project__name__icontains=search_query)
            )
    
    # Ensure flagged_reason is always a list, never None
    for volunteer in flagged_volunteers:
        if volunteer.flagged_reason is None:
            volunteer.flagged_reason = []
    
    for donation in flagged_donations:
        if donation.flagged_reason is None:
            donation.flagged_reason = []
    
    return render(request, 'general_dashboard.html', {
        'projects': projects,
        'total_projects': projects.count(),
        'flagged_volunteers': flagged_volunteers,
        'flagged_volunteers_count': flagged_volunteers_count,
        'flagged_donations': flagged_donations,
        'flagged_donations_count': flagged_donations_count,
        'volunteer_filter': volunteer_filter,
        'donation_filter': donation_filter,
        'active_tab': active_tab,
        'search_query': search_query,
        'deleted_volunteers': deleted_volunteers,
        'deleted_donations': deleted_donations,
    })

def general_delete_volunteer_view(request, volunteer_id):
    volunteer = get_object_or_404(Volunteer, id=volunteer_id)
    volunteer.delete()
    return redirect('general_dashboard')

def general_permanent_delete_volunteer_view(request, id):
    volunteer = get_object_or_404(Volunteer.all_objects, id=id)
    volunteer.delete()
    return redirect('general_dashboard')


def general_delete_donation_view(request, donation_id):
    donation = get_object_or_404(Donations, id=donation_id)
    donation.delete()
    return redirect('general_dashboard')

def general_permanent_delete_donation_view(request, id):
    donation = get_object_or_404(Donations.all_objects, id=id)
    donation.delete()
    return redirect('general_dashboard')
    
def general_restore_volunteer_view(request, id):
    volunteer = get_object_or_404(Volunteer.all_objects, id=id)
    volunteer.undelete()
    return redirect('general_dashboard')

def general_restore_donation_view(request, id):
    donation = get_object_or_404(Donations.all_objects, id=id)
    donation.undelete()
    return redirect('general_dashboard')




# DISASTER DASHBOARD
def delete_volunteer_view(request, volunteer_id):
    volunteer = get_object_or_404(Volunteer, id=volunteer_id)
    volunteer_project_id = volunteer.project_id
    volunteer.delete()
    if volunteer_project_id:
        return redirect('edit_project', project_id=volunteer_project_id)
    return redirect('admin_dashboard')

def permanent_delete_volunteer_view(request, id):
    volunteer = get_object_or_404(Volunteer.all_objects, id=id)
    volunteer.delete()
    return redirect('admin_dashboard')


def delete_donation_view(request, donation_id):
    donation = get_object_or_404(Donations, id=donation_id)
    donation_project_id = donation.project_id
    donation.delete()
    if donation_project_id:
        return redirect('edit_project', project_id=donation_project_id)
    return redirect('admin_dashboard')

def permanent_delete_donation_view(request, id):
    donation = get_object_or_404(Donations.all_objects, id=id)
    donation.delete()
    return redirect('admin_dashboard')
    
def restore_volunteer_view(request, id):
    volunteer = get_object_or_404(Volunteer.all_objects, id=id)
    volunteer_project_id = volunteer.project_id
    volunteer.undelete()
    if volunteer_project_id:
        return redirect('edit_project', project_id=volunteer_project_id)
    return redirect('admin_dashboard')

def restore_donation_view(request, id):
    donation = get_object_or_404(Donations.all_objects, id=id)
    donation_project_id = donation.project_id
    donation.undelete()
    if donation_project_id:
        return redirect('edit_project', project_id=donation_project_id)
    return redirect('admin_dashboard')


def close_project_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    project.active = False
    project.save()
    return redirect('admin_dashboard')

# def project_detail_view(request: HttpRequest, project_id: int) -> HttpResponse:
#     project = get_object_or_404(Project, id=project_id)
#     volunteers = Volunteer.objects.filter(project=project)
#     donations = Donations.objects.filter(project=project)

#     total_submissions = volunteers.count() + donations.count()

#     hourly_rate = project.hourly_rate
#     total_hours = volunteers.aggregate(total=Sum('total_hours'))['total'] or 0
#     volunteer_value = Decimal(str(total_hours)) * hourly_rate
#     flagged_count = volunteers.filter(flagged=True).count()

    return render(request, 'project_details.html', {
        'project': project,
        'volunteers': volunteers,
        'donations': donations,
        'total_submissions': total_submissions,
        'total_hours': total_hours,
        'volunteer_value': volunteer_value,
        'hourly_rate': hourly_rate,
        'flagged_count': flagged_count,
    })


def volunteer_pdf_view(request: HttpRequest, volunteer_id: int) -> HttpResponse:
    """Render a PDF-like page for a single volunteer submission (wrapped div for print)."""
    volunteer = get_object_or_404(Volunteer, id=volunteer_id)
    # reuse volunteers_pdf.html by passing a single-item list
    return render(request, 'volunteers_pdf.html', {'volunteers': [volunteer]})


def donation_pdf_view(request: HttpRequest, donation_id: int) -> HttpResponse:
    """Render a PDF-like page for a single donation submission (wrapped div for print)."""
    donation = get_object_or_404(Donations, id=donation_id)
    return render(request, 'donations_pdf.html', {'donations': [donation]})
    


def toggle_flagged_status(request, volunteer_id):
    volunteer = get_object_or_404(Volunteer, id=volunteer_id)
    volunteer.flagged = not volunteer.flagged
    volunteer.save()
    return JsonResponse({'flagged': volunteer.flagged, 'status': 'success'})


def toggle_donation_flagged_status(request, donation_id):
    donation = get_object_or_404(Donations, id=donation_id)
    donation.flagged = not donation.flagged
    donation.save()
    return JsonResponse({'flagged': donation.flagged, 'status': 'success'})


def toggle_skilled_worker_status(request, volunteer_id):
    volunteer = get_object_or_404(Volunteer, id=volunteer_id)
    volunteer.confirmed_skilled_worker = not volunteer.confirmed_skilled_worker
    volunteer.save(update_fields=['confirmed_skilled_worker'])
    return JsonResponse({'confirmed_skilled_worker': volunteer.confirmed_skilled_worker, 'status': 'success'})

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
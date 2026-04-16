from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.http.response import HttpResponse
from django.http.request import HttpRequest
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.utils import timezone
from django.core.exceptions import PermissionDenied
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import *
from django.contrib import messages
from django.db.models import Q, Min
from .models import *
from .forms import *
from .forms import DisasterForm, VolunteerForm, DonationForm
from honeypot.decorators import check_honeypot
from django_ratelimit.decorators import ratelimit
from django.template.loader import get_template
import csv
from rapidfuzz import fuzz
from .functions import *
from django.db.models import Sum
from django.http import JsonResponse
from .filters import VolunteerFilter, DonationFilter
from safedelete.models import HARD_DELETE




# Create your views here.

# NOTE PUBLIC USER VIEWS
def landing_view(request:HttpRequest)->HttpResponse:
    latest_disaster = Disaster.objects.filter(active=True).order_by('-start_date').first()
    if not latest_disaster:
        return render(request, 'landing.html', {
            'latest_disaster': None,
            'progress_total': Decimal('0.00'),
            'progress_goal': Decimal('0.00'),
            'progress_percent': Decimal('0.00'),
        })

    revenue_data = get_disaster_revenue(latest_disaster)
    progress_goal = latest_disaster.goal or Decimal('0.00')
    progress_total = revenue_data['total_value']
    progress_percent = (progress_total / progress_goal * Decimal('100')) if progress_goal else Decimal('0.00')

    return render(request, 'landing.html', {
        'latest_disaster': latest_disaster,
        'progress_goal': progress_goal,
        'progress_total': progress_total,
        'progress_percent': progress_percent,
    })

def faq_view(request:HttpRequest)->HttpResponse:
    return render(request, 'faq.html')

@check_honeypot
@ratelimit(key='ip', rate='5/m', method='POST', block=False)
def form_template_view(request:HttpRequest)->HttpResponse:
    earliest_date = Disaster.objects.filter(active=True).aggregate(Min('start_date'))['start_date__min']
    volunteerForm = VolunteerForm()
    donationForm = DonationForm()
    disasters = Disaster.objects.exclude(location__isnull=True).exclude(location__exact='')

    if request.method == 'POST' and getattr(request, 'limited', False):
        return render(request, '429.html', status=429)


    if request.method == 'POST':
        if 'submit_volunteer' in request.POST:
            volunteerForm = VolunteerForm(request.POST)

            if volunteerForm.is_valid():
                volunteer = volunteerForm.save(commit=False)
                best_disaster, _ = find_best_disaster(volunteer.location_volunteered, disasters)
                flag_reasons = volunteerForm.cleaned_data.get('flagged_reason', [])
                volunteer.flagged_reason = flag_reasons
                volunteer.flagged = bool(flag_reasons)
                has_invalid_location = has_invalid_location_flag(flag_reasons)
                if volunteer.skilled_worker == 'yes':
                    volunteer.confirmed_skilled_worker = True

                if has_invalid_location:
                    volunteer.disaster = None
                elif best_disaster:
                    volunteer.disaster = best_disaster

                volunteer.save()

                messages.success(request, 'Volunteer form submission saved successfully.')

                return redirect('forms')
            

            add_form_error_messages(request, volunteerForm, 'Volunteer')

        elif 'submit_donation' in request.POST:
            donationForm = DonationForm(request.POST)

            if donationForm.is_valid():
                donation = donationForm.save(commit=False)
                best_disaster, _ = find_best_disaster(donation.location_donated, disasters)
                flag_reasons = donationForm.cleaned_data.get('flagged_reason', [])
                donation.flagged_reason = flag_reasons
                donation.flagged = bool(flag_reasons)
                has_invalid_location = has_invalid_location_flag(flag_reasons)

                if has_invalid_location:
                    donation.disaster = None
                elif best_disaster:
                    donation.disaster = best_disaster

                donation.save()


                messages.success(request, 'Donation form submission saved successfully.')

                return redirect('forms')

            else:
                add_form_error_messages(request, donationForm, 'Donation')

    return render(request, 'forms.html', {
        'volunteerForm': volunteerForm,
        'donationForm': donationForm,
        'earliest_date': earliest_date,
    })

    
    # these messages need to change currently they're confirmation for testing but will need to be changed for users




# NOTE ADMIN ACCOUNT VIEWS
def login_view(request:HttpRequest)->HttpResponse:
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('general_dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request:HttpRequest)->HttpResponse:
    logout(request)
    return redirect('landing')
# may need to redirect to somewhere else considering it's admin


def _json_message_response(message, status='success', http_status=200):
    return JsonResponse({
        'status': status,
        'message': message,
        'message_type': 'success' if status == 'success' else 'error',
    }, status=http_status)



# NOTE GENERAL DASHBOARD VIEWS
def general_dashboard_view(request:HttpRequest)->HttpResponse:
    if request.method == 'POST':
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        current_password = (request.POST.get('current_password') or '').strip()
        first_name = (request.POST.get('first_name') or '').strip()
        last_name = (request.POST.get('last_name') or '').strip()
        new_password = request.POST.get('new_password') or ''
        confirm_password = request.POST.get('confirm_password') or ''
        wants_password_change = bool(new_password or confirm_password)

        if not current_password:
            message = 'Enter your current password to update your settings.'
            if is_ajax:
                return _json_message_response(message, status='error', http_status=400)
            messages.error(request, message)
            return redirect('general_dashboard')

        if not request.user.check_password(current_password):
            message = 'The current password is incorrect.'
            if is_ajax:
                return _json_message_response(message, status='error', http_status=400)
            messages.error(request, message)
            return redirect('general_dashboard')

        if wants_password_change and new_password != confirm_password:
            message = 'The new passwords do not match.'
            if is_ajax:
                return _json_message_response(message, status='error', http_status=400)
            messages.error(request, message)
            return redirect('general_dashboard')

        changes = []
        if first_name != request.user.first_name:
            request.user.first_name = first_name
            changes.append('first name')
        if last_name != request.user.last_name:
            request.user.last_name = last_name
            changes.append('last name')

        password_changed = False
        if wants_password_change:
            request.user.set_password(new_password)
            password_changed = True
            changes.append('password')

        if changes:
            request.user.save()
            if password_changed:
                update_session_auth_hash(request, request.user)
            message = 'Settings updated successfully.'
        else:
            message = 'No settings changes were made.'

        if is_ajax:
            return _json_message_response(message)

        messages.success(request, message)
        return redirect('general_dashboard')

    active_tab = request.GET.get('active_tab', 'volunteer-panel')
    search_query = (request.GET.get('q') or '').strip()
    create_form = DisasterForm()
    disasters = Disaster.objects.all().order_by('-active', 'name')
    active_disasters_count = Disaster.objects.filter(active=True).count()
    base_flagged_volunteers = Volunteer.objects.filter(flagged=True).select_related('disaster').order_by('-created_at')
    base_flagged_donations = Donations.objects.filter(flagged=True).select_related('disaster').order_by('-created_at')
    flagged_volunteers = base_flagged_volunteers
    flagged_donations = base_flagged_donations
    deleted_volunteers = Volunteer.all_objects.filter(deleted__isnull=False, disaster__isnull=True).order_by('-created_at')
    deleted_donations = Donations.all_objects.filter(deleted__isnull=False, disaster__isnull=True).order_by('-created_at')
    trash_count = deleted_volunteers.count() + deleted_donations.count()

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
                | Q(disaster__name__icontains=search_query)
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
                | Q(disaster__name__icontains=search_query)
            )
    elif active_tab == 'trash-panel':
        if search_query:
            deleted_volunteers = deleted_volunteers.filter(
                Q(name__icontains=search_query)
                | Q(email__icontains=search_query)
                | Q(phone_number__icontains=search_query)
                | Q(location_volunteered__icontains=search_query)
                | Q(work_desc__icontains=search_query)
                | Q(notes__icontains=search_query)
            )
            deleted_donations = deleted_donations.filter(
                Q(name__icontains=search_query)
                | Q(email__icontains=search_query)
                | Q(phone_number__icontains=search_query)
                | Q(location_donated__icontains=search_query)
                | Q(work_desc__icontains=search_query)
                | Q(notes__icontains=search_query)
                | Q(material_type__icontains=search_query)
                | Q(equipment_type__icontains=search_query)
                | Q(other_donation_type__icontains=search_query)
            )
    
    # Ensure flagged_reason is always a list, never None
    for volunteer in flagged_volunteers:
        if volunteer.flagged_reason is None:
            volunteer.flagged_reason = []
    
    for donation in flagged_donations:
        if donation.flagged_reason is None:
            donation.flagged_reason = []
    
    return render(request, 'general_dashboard.html', {
        'disasters': disasters,
        'total_disasters': active_disasters_count,
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
        'trash_count': trash_count,
        'create_form': create_form,
    })


def general_delete_volunteer_view(request, volunteer_id):
    volunteer = get_object_or_404(Volunteer, id=volunteer_id)
    volunteer.delete()
    return JsonResponse({'status': 'success', 'message': 'Volunteer moved to trash.', 'message_type': 'danger'})

def general_permanent_delete_volunteer_view(request, id):
    volunteer = get_object_or_404(Volunteer.all_objects, id=id)
    volunteer.delete(force_policy=HARD_DELETE)
    return JsonResponse({'status': 'success', 'message': 'Volunteer permanently deleted.', 'message_type': 'danger'})

def general_restore_volunteer_view(request, id):
    volunteer = get_object_or_404(Volunteer.all_objects, id=id)
    volunteer.undelete()
    return JsonResponse({'status': 'success', 'message': 'Volunteer restored successfully.'})


def general_delete_donation_view(request, donation_id):
    donation = get_object_or_404(Donations, id=donation_id)
    donation.delete()
    return JsonResponse({'status': 'success', 'message': 'Donation moved to trash.', 'message_type': 'danger'})

def general_permanent_delete_donation_view(request, id):
    donation = get_object_or_404(Donations.all_objects, id=id)
    donation.delete(force_policy=HARD_DELETE)
    return JsonResponse({'status': 'success', 'message': 'Donation permanently deleted.', 'message_type': 'danger'})

def general_restore_donation_view(request, id):
    donation = get_object_or_404(Donations.all_objects, id=id)
    donation.undelete()
    return JsonResponse({'status': 'success', 'message': 'Donation restored successfully.'})


def assign_submission_view(request, submission_type, submission_id):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'error': 'Invalid request method'}, status=405)

    disaster_id = request.POST.get('disaster_id')
    if not disaster_id:
        return JsonResponse({'status': 'error', 'error': 'Please select a disaster.'}, status=400)

    disaster = get_object_or_404(Disaster, id=disaster_id)

    if submission_type == 'volunteer':
        submission = get_object_or_404(Volunteer, id=submission_id)
    elif submission_type == 'donation':
        submission = get_object_or_404(Donations, id=submission_id)
    else:
        return JsonResponse({'status': 'error', 'error': 'Invalid submission type.'}, status=400)

    submission.disaster = disaster
    if should_clear_flag_on_assignment(submission.flagged_reason):
        submission.flagged = False
        submission.flagged_reason = []
    submission.save(update_fields=['disaster', 'flagged', 'flagged_reason'])

    return JsonResponse({'status': 'success'})




# NOTE ADMIN DASHBOARD VIEWS
def admin_dashboard_view(request: HttpRequest, disaster_id=None) -> HttpResponse:
    disaster = get_object_or_404(Disaster, id=disaster_id) if disaster_id else None
    active_tab = request.GET.get('active_tab', 'volunteers-panel')

    # DELETE
    if request.method == 'POST' and request.POST.get('_method') == 'DELETE':
        if disaster:
            disaster.delete()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return _json_message_response('Disaster deleted successfully.')
        messages.success(request, 'Disaster deleted successfully.')
        return redirect('admin_dashboard', )
    # think this needs to be deleted because you cant delete disasters just close them but maybe it should still be an option? //COW//

    # CREATE/UPDATE
    if request.method == 'POST':
        form = DisasterForm(request.POST, instance=disaster)
        if form.is_valid():
            saved_disaster = form.save()
            message = 'Disaster created successfully.' if disaster is None else 'Disaster updated successfully.'
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return _json_message_response(message)
            messages.success(request, message)
            if disaster is None:
                return redirect('general_dashboard')
            return redirect('edit_disaster', disaster_id=saved_disaster.id)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return _json_message_response('Please fix the disaster form and try again.', status='error', http_status=400)
    else:
        form = DisasterForm(instance=disaster)
    
    query = request.GET.get('q')

    if disaster:
        base_volunteers = Volunteer.objects.filter(disaster=disaster).order_by('-created_at')
        base_donations = Donations.objects.filter(disaster=disaster).order_by('-created_at')
    else:
        base_volunteers = Volunteer.objects.all().order_by('-created_at')
        base_donations = Donations.objects.all().order_by('-created_at')

    volunteers = base_volunteers
    donations = base_donations

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

    hourly_rate = disaster.hourly_rate if disaster else Decimal('29.95')
    skilled_hourly_rate = disaster.skilled_hourly_rate if disaster else Decimal('45.00')

    total_hours = volunteers.aggregate(total=Sum('total_hours'))['total'] or 0
    if disaster:
        revenue_data = get_disaster_revenue(disaster)
    else:
        revenue_data = get_aggregate_revenue(base_volunteers, base_donations)
    volunteer_value = revenue_data['volunteer_value']
    flagged_count = volunteers.filter(flagged=True).count()
    donation_flagged_count = donations.filter(flagged=True).count()

    donation_value = revenue_data['donation_value']
    total_value = volunteer_value + donation_value

    edit_form = DisasterForm(instance=disaster) if disaster else None
    if disaster:
        deleted_volunteers = Volunteer.all_objects.filter(deleted__isnull=False, disaster=disaster).order_by('-created_at')
        deleted_donations = Donations.all_objects.filter(deleted__isnull=False, disaster=disaster).order_by('-created_at')
    else:
        deleted_volunteers = Volunteer.all_objects.filter(deleted__isnull=False, disaster__isnull=False).order_by('-created_at')
        deleted_donations = Donations.all_objects.filter(deleted__isnull=False, disaster__isnull=False).order_by('-created_at')
    volunteer_tab_count = base_volunteers.count()
    donation_tab_count = base_donations.count()
    flagged_tab_count = flagged_volunteers.count() + flagged_donations.count()
    trash_count = deleted_volunteers.count() + deleted_donations.count()

    # READ
    return render(request, 'admin_dashboard.html', {
        'disasters': Disaster.objects.all(),
        'volunteers': volunteers,
        'donations': donations,
        'volunteer_count': volunteer_count,
        'donation_count': donation_count,
        'total_submissions': total_submissions,
        'edit_form': edit_form,
        'disaster': disaster,
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
        'volunteer_tab_count': volunteer_tab_count,
        'donation_tab_count': donation_tab_count,
        'flagged_tab_count': flagged_tab_count,
        'trash_count': trash_count,
    })


def delete_volunteer_view(request, volunteer_id):
    volunteer = get_object_or_404(Volunteer, id=volunteer_id)
    volunteer_disaster_id = volunteer.disaster_id
    volunteer.delete()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'message': 'Volunteer moved to trash.', 'message_type': 'danger'})
    if volunteer_disaster_id:
        return redirect('edit_disaster', disaster_id=volunteer_disaster_id)
    return redirect('admin_dashboard')

def permanent_delete_volunteer_view(request, id):
    volunteer = get_object_or_404(Volunteer.all_objects, id=id)
    volunteer.delete(force_policy=HARD_DELETE)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'message': 'Volunteer permanently deleted.', 'message_type': 'danger'})
    return redirect('admin_dashboard')

def restore_volunteer_view(request, id):
    volunteer = get_object_or_404(Volunteer.all_objects, id=id)
    volunteer_disaster_id = volunteer.disaster_id
    volunteer.undelete()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return _json_message_response('Volunteer restored successfully.')
    if volunteer_disaster_id:
        return redirect('edit_disaster', disaster_id=volunteer_disaster_id)
    return redirect('admin_dashboard')

def generate_volunteer_csv(request):
    response = HttpResponse(
        content_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="submissions_export.csv"'},
    )
    writer = csv.writer(response)
    writer.writerow([
    'submission_type', 'id', 'name', 'email', 'phone_number', 'date', 'total_hours', 'location', 'work_desc', 'notes',
    'disaster_name', 'equipment', 'other_equipment', 'equipment_make_model', 'equipment_hours', 'donation_type', 'material_type', 'equipment_type'])

    raw_ids = request.GET.get('ids', '')
    raw_disaster_id = request.GET.get('disaster_id', '')
    selected_ids = [int(value) for value in raw_ids.split(',') if value.strip().isdigit()]

    volunteers = Volunteer.objects.select_related('disaster')
    if raw_disaster_id.strip().isdigit():
        volunteers = volunteers.filter(disaster_id=int(raw_disaster_id))

    if selected_ids:
        volunteers = volunteers.filter(id__in=selected_ids)
    else:
        volunteers = volunteers.none()

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
    volunteer.disaster.name if volunteer.disaster else '',
    volunteer.equipment,
    volunteer.other_equipment,
    volunteer.equipment_make_model,
    volunteer.equipment_hours])
    return response


def delete_donation_view(request, donation_id):
    donation = get_object_or_404(Donations, id=donation_id)
    donation_disaster_id = donation.disaster_id
    donation.delete()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'message': 'Donation moved to trash.', 'message_type': 'danger'})
    if donation_disaster_id:
        return redirect('edit_disaster', disaster_id=donation_disaster_id)
    return redirect('admin_dashboard')

def permanent_delete_donation_view(request, id):
    donation = get_object_or_404(Donations.all_objects, id=id)
    donation.delete(force_policy=HARD_DELETE)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'message': 'Donation permanently deleted.', 'message_type': 'danger'})
    return redirect('admin_dashboard')

def restore_donation_view(request, id):
    donation = get_object_or_404(Donations.all_objects, id=id)
    donation_disaster_id = donation.disaster_id
    donation.undelete()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return _json_message_response('Donation restored successfully.')
    if donation_disaster_id:
        return redirect('edit_disaster', disaster_id=donation_disaster_id)
    return redirect('admin_dashboard')

def generate_donation_csv(request):
    response = HttpResponse(
        content_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="submissions_export.csv"'},
    )
    writer = csv.writer(response)
    writer.writerow([
    'submission_type' ,'disaster_name', 'id', 'name', 'email', 'phone_number', 'date', 'total_hours', 'location', 'work_desc', 'notes',
    'donation_type', 'material_type', 'equipment_type'])

    raw_ids = request.GET.get('ids', '')
    raw_disaster_id = request.GET.get('disaster_id', '')
    selected_ids = [int(value) for value in raw_ids.split(',') if value.strip().isdigit()]

    donations = Donations.objects.select_related('disaster')
    if raw_disaster_id.strip().isdigit():
        donations = donations.filter(disaster_id=int(raw_disaster_id))

    if selected_ids:
        donations = donations.filter(id__in=selected_ids)
    else:
        donations = donations.none()

    for donation in donations:
        writer.writerow([
    'donation',
    donation.disaster.name if donation.disaster else '',
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


def close_disaster_view(request, disaster_id):
    disaster = get_object_or_404(Disaster, id=disaster_id)
    disaster.active = False
    disaster.save()
    return redirect('admin_dashboard')


def update_hourly_rate_view(request, disaster_id):
    disaster = get_object_or_404(Disaster, id=disaster_id)
    
    if not disaster.active:
        return JsonResponse({'status': 'error', 'message': 'Cannot update rates for closed disasters'}, status=400)
    
    if 'hourly_rate' in request.POST:
        disaster.hourly_rate = Decimal(request.POST.get('hourly_rate'))
    
    if 'skilled_hourly_rate' in request.POST:
        disaster.skilled_hourly_rate = Decimal(request.POST.get('skilled_hourly_rate'))
    
    disaster.save()
    
    return JsonResponse({
        'status': 'success',
        'hourly_rate': str(disaster.hourly_rate),
        'skilled_hourly_rate': str(disaster.skilled_hourly_rate)
    })


def toggle_flagged_status(request, volunteer_id):
    volunteer = get_object_or_404(Volunteer, id=volunteer_id)
    volunteer.flagged = not volunteer.flagged
    if volunteer.flagged:
        volunteer.flagged_reason = ['manually flagged']
    else:
        volunteer.flagged_reason = []
    volunteer.save(update_fields=['flagged', 'flagged_reason'])
    return JsonResponse({
        'flagged': volunteer.flagged,
        'status': 'success',
        'message': 'Submission flagged as manually flagged.' if volunteer.flagged else 'Submission unflagged successfully.',
        'message_type': 'success',
    })

def toggle_donation_flagged_status(request, donation_id):
    donation = get_object_or_404(Donations, id=donation_id)
    donation.flagged = not donation.flagged
    if donation.flagged:
        donation.flagged_reason = ['manually flagged']
    else:
        donation.flagged_reason = []
    donation.save(update_fields=['flagged', 'flagged_reason'])
    return JsonResponse({
        'flagged': donation.flagged,
        'status': 'success',
        'message': 'Submission flagged as manually flagged.' if donation.flagged else 'Submission unflagged successfully.',
        'message_type': 'success',
    })


def toggle_skilled_worker_status(request, volunteer_id):
    volunteer = get_object_or_404(Volunteer, id=volunteer_id)
    volunteer.confirmed_skilled_worker = not volunteer.confirmed_skilled_worker
    volunteer.save(update_fields=['confirmed_skilled_worker'])
    return JsonResponse({
        'confirmed_skilled_worker': volunteer.confirmed_skilled_worker,
        'status': 'success',
        'message': 'Submission marked as skilled worker.' if volunteer.confirmed_skilled_worker else 'Submission unmarked as skilled worker.',
        'message_type': 'success',
    })


def submissions_full_view(request: HttpRequest, disaster_id=None) -> HttpResponse:
    disaster = get_object_or_404(Disaster, id=disaster_id) if disaster_id else None
    active_tab = request.GET.get('active_tab', 'volunteer-panel')
    query = request.GET.get('q')

    if disaster:
        volunteers = Volunteer.objects.filter(disaster=disaster).select_related('disaster').order_by('-created_at')
        donations = Donations.objects.filter(disaster=disaster).select_related('disaster').order_by('-created_at')
    else:
        volunteers = Volunteer.objects.select_related('disaster').order_by('-created_at')
        donations = Donations.objects.select_related('disaster').order_by('-created_at')

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
        'disaster': disaster,
        'active_tab': active_tab,
        'query': query,
        'volunteers': volunteers,
        'donations': donations,
        'volunteer_filter': volunteer_filter,
        'donation_filter': donation_filter,
    })




# NOTE STATUS CODE ERROR VIEWS
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


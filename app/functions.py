from decimal import Decimal
from rapidfuzz import fuzz
from django.contrib import messages
from django.db.models import Sum

from .models import Donations, Volunteer

def is_similar(a, b, threshold=75):
    return fuzz.ratio(a.lower(), b.lower()) >= threshold

def add_form_error_messages(request, form, form_name: str):
    messages.error(request, f'{form_name} form has errors. Please review the fields below.')
    for field_name, field_errors in form.errors.items():
        if field_name == '__all__':
            label = 'Form'
        else:
            label = form.fields[field_name].label or field_name.replace('_', ' ').title()

        for error in field_errors:
            messages.error(request, f'{label}: {error}')


def find_best_disaster(location_text: str, disasters):
    normalized_location = (location_text or '').strip().lower()
    if not normalized_location:
        return None, -1

    best_disaster = None
    best_similarity = -1
    best_matches = []

    for disaster in disasters:
        if not disaster.active:
            continue

        disaster_location = (disaster.location or '').strip().lower()
        if not disaster_location:
            continue

        similarity = fuzz.ratio(normalized_location, disaster_location)
        if similarity > best_similarity:
            best_similarity = similarity
            best_disaster = disaster
            best_matches = [disaster]
        elif similarity == best_similarity:
            best_matches.append(disaster)

    # If the best match is ambiguous across multiple active disasters
    # that share the same location, do not auto-assign.
    if best_similarity >= 80 and len(best_matches) > 1:
        match_locations = {(match.location or '').strip().lower() for match in best_matches}
        if len(match_locations) == 1:
            return None, best_similarity

    return best_disaster, best_similarity


def get_disaster_revenue(disaster):
    if not disaster:
        return {
            'hourly_rate': Decimal('0.00'),
            'skilled_hourly_rate': Decimal('0.00'),
            'volunteer_value': Decimal('0.00'),
            'donation_value': Decimal('0.00'),
            'total_value': Decimal('0.00'),
            'volunteer_hours': 0,
            'donation_hours': 0,
        }

    hourly_rate = disaster.hourly_rate
    skilled_hourly_rate = disaster.skilled_hourly_rate

    volunteers = Volunteer.objects.filter(disaster=disaster)
    donations = Donations.objects.filter(disaster=disaster)

    volunteer_hours = Decimal('0')
    donation_hours = Decimal('0')
    volunteer_value = Decimal('0.00')
    donation_value = Decimal('0.00')

    for volunteer in volunteers:
        if has_invalid_location_flag(volunteer.flagged_reason):
            continue

        hours = Decimal(str(volunteer.total_hours or 0))
        volunteer_hours += hours
        rate = skilled_hourly_rate if volunteer.confirmed_skilled_worker else hourly_rate
        volunteer_value += hours * rate

    for donation in donations:
        if has_invalid_location_flag(donation.flagged_reason):
            continue

        hours = Decimal(str(donation.total_hours or 0))
        donation_hours += hours
        donation_value += hours * hourly_rate

    return {
        'hourly_rate': hourly_rate,
        'skilled_hourly_rate': skilled_hourly_rate,
        'volunteer_value': volunteer_value,
        'donation_value': donation_value,
        'total_value': volunteer_value + donation_value,
        'volunteer_hours': float(volunteer_hours),
        'donation_hours': donation_hours,
    }


def get_aggregate_revenue(volunteers, donations):
    volunteer_value = Decimal('0.00')
    donation_value = Decimal('0.00')

    for volunteer in volunteers.select_related('disaster'):
        if not volunteer.disaster:
            continue
        if has_invalid_location_flag(volunteer.flagged_reason):
            continue

        hours = Decimal(str(volunteer.total_hours or 0))
        rate = volunteer.disaster.skilled_hourly_rate if volunteer.confirmed_skilled_worker else volunteer.disaster.hourly_rate
        volunteer_value += hours * rate

    for donation in donations.select_related('disaster'):
        if not donation.disaster:
            continue
        if has_invalid_location_flag(donation.flagged_reason):
            continue

        hours = Decimal(str(donation.total_hours or 0))
        donation_value += hours * donation.disaster.hourly_rate

    return {
        'volunteer_value': volunteer_value,
        'donation_value': donation_value,
        'total_value': volunteer_value + donation_value,
    }


def should_clear_flag_on_assignment(flagged_reason):
    reasons = flagged_reason or []
    return len(reasons) == 1 and reasons[0] == Volunteer.FLAG_INVALID_LOCATION


def has_invalid_location_flag(flagged_reason):
    reasons = flagged_reason or []
    return Volunteer.FLAG_INVALID_LOCATION in reasons or Donations.FLAG_INVALID_LOCATION in reasons
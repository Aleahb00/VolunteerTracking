from rapidfuzz import fuzz
from django.contrib import messages

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
    best_disaster = None
    best_similarity = -1

    for disaster in disasters:
        if disaster.active:
            similarity = fuzz.ratio(location_text.lower(), disaster.location.lower())
            if similarity > best_similarity:
                best_similarity = similarity
                best_disaster = disaster

    return best_disaster, best_similarity
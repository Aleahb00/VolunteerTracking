from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from .views import *


urlpatterns = [
    # ANCHOR PUBLIC USER URLS
    path('', landing_view, name="landing"),
    path('faq/', faq_view, name="faq"),
    path('forms/', form_template_view, name="forms"),




    # ANCHOR ADMIN ACCOUNT URLS
    path('admin-register/', register_view, name='register'),
    path('admin-login/', login_view, name='login'),
    path('admin-logout/', logout_view, name='logout'),




    # ANCHOR GENERAL DASHBOARD URLS
    # General Dashboard
    path('general-dashboard/', general_dashboard_view, name='general_dashboard'),

    # General Dashboard - Volunteer Management
    path('general-dashboard/delete-volunteer/<int:volunteer_id>/', general_delete_volunteer_view, name='delete_volunteer_general'),
    path('general-dashboard/restore-volunteer/<int:id>/', general_restore_volunteer_view, name='restore_volunteer_general'),
    path('general-dashboard/permanent-delete-volunteer/<int:id>/', general_permanent_delete_volunteer_view, name='permanent_delete_volunteer_general'),

    # General Dashboard - Donation Management
    path('general-dashboard/delete-donation/<int:donation_id>/', general_delete_donation_view, name='delete_donation_general'),
    path('general-dashboard/restore-donation/<int:id>/', general_restore_donation_view, name='restore_donation_general'),
    path('general-dashboard/permanent-delete-donation/<int:id>/', general_permanent_delete_donation_view, name='permanent_delete_donation_general'),




    # ANCHOR DISASTER DASHBOARD URLS
    # Disaster Dashboard
    path('admin-dashboard/', admin_dashboard_view, name='admin_dashboard'),

    # Disaster Controls
    path('admin-dashboard/<int:disaster_id>/', admin_dashboard_view, name='edit_disaster'),
    path('admin-dashboard/<int:disaster_id>/delete/', admin_dashboard_view, name='delete_disaster'),
    path('admin-dashboard/close-disaster/<int:disaster_id>/', close_disaster_view, name='close_disaster'),

    # Disaster Dashboard - Volunteer Management
    path('admin-dashboard/delete-volunteer/<int:volunteer_id>/', delete_volunteer_view, name='delete_volunteer'),
    path('admin-dashboard/restore-volunteer/<int:id>/', restore_volunteer_view, name='restore_volunteer'),
    path('admin-dashboard/permanent-delete-volunteer/<int:id>/', permanent_delete_volunteer_view, name='permanent_delete_volunteer'),
    path('admin-dashboard/export/volunteer_csv/', generate_volunteer_csv, name='export_csv'),

    # Disaster Dashboard - Donation Management
    path('admin-dashboard/delete-donation/<int:donation_id>/', delete_donation_view, name='delete_donation'),
    path('admin-dashboard/restore-donation/<int:id>/', restore_donation_view, name='restore_donation'),
    path('admin-dashboard/permanent-delete-donation/<int:id>/', permanent_delete_donation_view, name='permanent_delete_donation'),
    path('admin-dashboard/export/donations_csv/', generate_donation_csv, name='export_donations_csv'),

    # Disaster Dashboard - Submissions View
    path('submissions-full/', submissions_full_view, name='submissions_full'),
    path('submissions-full/<int:disaster_id>/', submissions_full_view, name='submissions_full_disaster'),




    # ANCHOR UNBASED FUNCTIONS URLS
    path('toggle_flagged_status/<int:volunteer_id>/', toggle_flagged_status, name='toggle_flagged_status'),
    path('toggle_donation_flagged_status/<int:donation_id>/', toggle_donation_flagged_status, name='toggle_donation_flagged_status'),
    path('toggle_skilled_worker_status/<int:volunteer_id>/', toggle_skilled_worker_status, name='toggle_skilled_worker_status'),




    # ANCHOR STATUS CODE ERROR URLS
    path('error403/', status_403_view, name='403'), #unauthorized access page
    path('error404/', status_404_view, name='404'), #page not found   
    path('error429/', status_429_view, name='429'), #too many requests page
    path('error500/', status_500_view, name='500'), #server error page


    # TBD
    
    # path('disaster/<int:disaster_id>/', disaster_detail_view, name='disaster_detail'),
    # path('admin-dashboard/volunteer/<int:volunteer_id>/pdf/', volunteer_pdf_view, name='volunteer_pdf'),
    # path('admin-dashboard/donation/<int:donation_id>/pdf/', donation_pdf_view, name='donation_pdf'),

]


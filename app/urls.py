from django.urls import path
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from .views import *


urlpatterns = [
    path('', landing_view, name="landing"),
    path('faq/', faq_view, name="faq"),
    # path('admin/test/', project_test_view, name="project_test"),
    path('forms/', form_template_view, name="forms"),

    path('admin-register/', register_view, name='register'),
    path('admin-login/', login_view, name='login'),
    path('admin-logout/', logout_view, name='logout'),

    path('admin-dashboard/', admin_dashboard_view, name='admin_dashboard'),           # list + create
    path('admin-dashboard/<int:project_id>/', admin_dashboard_view, name='edit_project'),  # edit
    path('admin-dashboard/<int:project_id>/delete/', admin_dashboard_view, name='delete_project'),  # delete
    
    path('admin-dashboard/close-project/<int:project_id>/', close_project_view, name='close_project'),
    
    path('admin-dashboard/delete-volunteer/<int:volunteer_id>/', delete_volunteer_view, name='delete_volunteer'),
    path('admin-dashboard/delete-donation/<int:donation_id>/', delete_donation_view, name='delete_donation'),
    path('admin-dashboard/export/volunteer_csv/', generate_volunteer_csv, name='export_csv'),
    path('admin-dashboard/export/donations_csv/', generate_donation_csv, name='export_donations_csv'),

    path('general-dashboard/', general_dashboard_view, name='general_dashboard'),
    path('submissions-full/', submissions_full_view, name='submissions_full'),
    path('submissions-full/<int:project_id>/', submissions_full_view, name='submissions_full_project'),

    path('project/<int:project_id>/', project_detail_view, name='project_detail'),
    # Project detail page
    path('admin-dashboard/volunteer/<int:volunteer_id>/pdf/', volunteer_pdf_view, name='volunteer_pdf'),
    path('admin-dashboard/donation/<int:donation_id>/pdf/', donation_pdf_view, name='donation_pdf'),
    # PDF-like views for individual submissions

    path('admin-dashboard/restore-volunteer/<int:id>/', restore_volunteer_view, name='restore_volunteer'),
    path('admin-dashboard/restore-donation/<int:id>/', restore_donation_view, name='restore_donation'),
    
    path('admin-dashboard/permanent-delete-volunteer/<int:id>/', permanent_delete_volunteer_view, name='permanent_delete_volunteer'),
    path('admin-dashboard/permanent-delete-donation/<int:id>/', permanent_delete_donation_view, name='permanent_delete_donation'),



    path('toggle_flagged_status/<int:volunteer_id>/', toggle_flagged_status, name='toggle_flagged_status'),
    path('toggle_donation_flagged_status/<int:donation_id>/', toggle_donation_flagged_status, name='toggle_donation_flagged_status'),
    path('toggle_skilled_worker_status/<int:volunteer_id>/', toggle_skilled_worker_status, name='toggle_skilled_worker_status'),

    path('error403/', status_403_view, name='403'), #unauthorized access page
    path('error404/', status_404_view, name='404'), #page not found   
    path('error429/', status_429_view, name='429'), #too many requests page
    path('error500/', status_500_view, name='500'), #server error page
]


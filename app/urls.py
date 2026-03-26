from django.urls import path
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from .views import *


urlpatterns = [
    path('', landing_view, name="landing"),
    # path('admin/test/', project_test_view, name="project_test"),
    path('forms/', form_template_view, name="forms"),
    path('admin-dashboard/', admin_dashboard_view, name='admin_dashboard'),           # list + create
    path('admin-dashboard/<int:project_id>/', admin_dashboard_view, name='edit_project'),  # edit
    path('admin-dashboard/<int:project_id>/delete/', admin_dashboard_view, name='delete_project'),  # delete
]
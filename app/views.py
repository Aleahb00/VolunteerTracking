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
# from .models import *
# from .forms import *
from django.template.loader import get_template

# Create your views here.
def landing_view(request:HttpRequest)->HttpResponse:
    return render(request, 'landing.html')

def error_view(request:HttpRequest)->HttpResponse:
    pass
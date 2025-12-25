from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from .models import User, Property, Inspection

# Authentication Views
def signup_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        nid = request.POST.get('nid')
        phone = request.POST.get('phone')
        user_type = request.POST.get('user_type')
        password = request.POST.get('password')
        
        # Validation
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return render(request, 'signup.html')
        
        if User.objects.filter(nid=nid).exists():
            messages.error(request, 'NID already registered')
            return render(request, 'signup.html')
        
        # Create user
        user = User.objects.create(
            name=name,
            email=email,
            nid=nid,
            phone=phone,
            user_type=user_type,
            password=make_password(password)
        )
        
        messages.success(request, 'Account created successfully! Please login.')
        return redirect('login')
    
    return render(request, 'signup.html')

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')
        
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            login(request, user)
            
            # Handle remember me
            if not remember_me:
                request.session.set_expiry(0)
            
            # Redirect based on user type
            if user.user_type == 'owner':
                return redirect('owner_dashboard')
            elif user.user_type == 'inspector':
                return redirect('inspector_dashboard')
            elif user.user_type == 'admin':
                return redirect('admin_dashboard')
        else:
            return render(request, 'login.html', {
                'error': 'Invalid email or password',
                'email': email
            })
    
    return render(request, 'login.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

# Dashboard Views
@login_required
def owner_dashboard(request):
    if request.user.user_type != 'owner':
        return redirect('login')
    
    properties = Property.objects.filter(owner=request.user)
    inspections = Inspection.objects.filter(property__owner=request.user)
    
    context = {
        'user': request.user,
        'total_properties': properties.count(),
        'active_inspections': inspections.filter(status='in_progress').count(),
        'pending_actions': inspections.filter(status='pending').count(),
    }
    return render(request, 'owner_dashboard.html', context)

@login_required
def inspector_dashboard(request):
    if request.user.user_type != 'inspector':
        return redirect('login')
    
    inspections = Inspection.objects.filter(inspector=request.user)
    
    context = {
        'user': request.user,
        'total_inspections': inspections.count(),
        'pending_inspections': inspections.filter(status='pending').count(),
        'in_progress': inspections.filter(status='in_progress').count(),
        'completed': inspections.filter(status='completed').count(),
    }
    return render(request, 'inspector_dashboard.html', context)

@login_required
def admin_dashboard(request):
    if request.user.user_type != 'admin':
        return redirect('login')
    
    context = {
        'user': request.user,
        'total_users': User.objects.count(),
        'total_properties': Property.objects.count(),
        'total_inspections': Inspection.objects.count(),
        'inspectors': User.objects.filter(user_type='inspector').count(),
    }
    return render(request, 'admin_dashboard.html', context)

# Property Views
@login_required
def my_properties(request):
    if request.user.user_type != 'owner':
        return redirect('login')
    
    properties = Property.objects.filter(owner=request.user).order_by('-created_at')
    
    context = {
        'user': request.user,
        'properties': properties,
    }
    return render(request, 'my_properties.html', context)

@login_required
def add_property(request):
    if request.user.user_type != 'owner':
        return redirect('login')
    
    if request.method == 'POST':
        property_type = request.POST.get('property_type')
        location = request.POST.get('location')
        
        Property.objects.create(
            property_type=property_type,
            location=location,
            owner=request.user
        )
        
        messages.success(request, 'Property added successfully!')
        return redirect('my_properties')
    
    return render(request, 'add_property.html')
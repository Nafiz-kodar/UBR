from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.db.models import Count, Q
from .models import CustomUser, Property, Inspection


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
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return render(request, 'signup.html', {'email': email})
        
        if CustomUser.objects.filter(nid=nid).exists():
            messages.error(request, 'NID already registered')
            return render(request, 'signup.html', {'email': email})
        
        # Create user
        user = CustomUser.objects.create(
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
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')


# Dashboard Views
@login_required
def owner_dashboard(request):
    if request.user.user_type != 'owner':
        messages.error(request, 'Access denied. Owners only.')
        return redirect('login')
    
    properties = Property.objects.filter(owner=request.user)
    inspections = Inspection.objects.filter(property__owner=request.user)
    
    context = {
        'user': request.user,
        'total_properties': properties.count(),
        'active_inspections': inspections.filter(status='in_progress').count(),
        'pending_actions': inspections.filter(status='pending').count(),
        'documents': 0,  # Add document model later
    }
    return render(request, 'owner_dashboard.html', context)


@login_required
def inspector_dashboard(request):
    if request.user.user_type != 'inspector':
        messages.error(request, 'Access denied. Inspectors only.')
        return redirect('login')
    
    inspections = Inspection.objects.filter(inspector=request.user)
    
    context = {
        'user': request.user,
        'total_inspections': inspections.count(),
        'pending_inspections': inspections.filter(status='pending').count(),
        'in_progress': inspections.filter(status='in_progress').count(),
        'completed': inspections.filter(status='completed').count(),
        'inspections': inspections.order_by('-scheduled_date')[:10],
    }
    return render(request, 'inspector_dashboard.html', context)


@login_required
def admin_dashboard(request):
    if request.user.user_type != 'admin':
        messages.error(request, 'Access denied. Admins only.')
        return redirect('login')
    
    context = {
        'user': request.user,
        'total_users': CustomUser.objects.count(),
        'total_properties': Property.objects.count(),
        'total_inspections': Inspection.objects.count(),
        'inspectors': CustomUser.objects.filter(user_type='inspector').count(),
        'owners': CustomUser.objects.filter(user_type='owner').count(),
        'recent_users': CustomUser.objects.order_by('-u_id')[:5],
        'recent_properties': Property.objects.order_by('-created_at')[:5],
    }
    return render(request, 'admin_dashboard.html', context)


# Property Views
@login_required
def my_properties(request):
    if request.user.user_type != 'owner':
        messages.error(request, 'Access denied. Owners only.')
        return redirect('login')
    
    properties = Property.objects.filter(owner=request.user).order_by('-created_at')
    
    # Add inspection counts for each property
    for prop in properties:
        prop.inspection_count = prop.inspections.count()
        prop.document_count = 0  # Add when document model exists
    
    context = {
        'user': request.user,
        'properties': properties,
    }
    return render(request, 'my_properties.html', context)


@login_required
def add_property(request):
    if request.user.user_type != 'owner':
        messages.error(request, 'Access denied. Owners only.')
        return redirect('login')
    
    if request.method == 'POST':
        property_type = request.POST.get('property_type')
        location = request.POST.get('location')
        
        if not property_type or not location:
            messages.error(request, 'All fields are required.')
            return render(request, 'add_property.html')
        
        Property.objects.create(
            property_type=property_type,
            location=location,
            owner=request.user
        )
        
        messages.success(request, 'Property added successfully!')
        return redirect('my_properties')
    
    return render(request, 'add_property.html')


@login_required
def property_detail(request, p_id):
    try:
        property_obj = Property.objects.get(p_id=p_id)
        
        # Check permissions
        if request.user.user_type == 'owner' and property_obj.owner != request.user:
            messages.error(request, 'You do not have permission to view this property.')
            return redirect('my_properties')
        
        inspections = property_obj.inspections.all().order_by('-scheduled_date')
        
        context = {
            'user': request.user,
            'property': property_obj,
            'inspections': inspections,
        }
        return render(request, 'property_detail.html', context)
    
    except Property.DoesNotExist:
        messages.error(request, 'Property not found.')
        return redirect('my_properties')


@login_required
def delete_property(request, p_id):
    if request.user.user_type != 'owner':
        messages.error(request, 'Access denied.')
        return redirect('login')
    
    try:
        property_obj = Property.objects.get(p_id=p_id, owner=request.user)
        property_obj.delete()
        messages.success(request, 'Property deleted successfully.')
    except Property.DoesNotExist:
        messages.error(request, 'Property not found or you do not have permission.')
    
    return redirect('my_properties')


# Home/Landing Page
def home(request):
    if request.user.is_authenticated:
        # Redirect to appropriate dashboard based on user type
        if request.user.user_type == 'owner':
            return redirect('owner_dashboard')
        elif request.user.user_type == 'inspector':
            return redirect('inspector_dashboard')
        elif request.user.user_type == 'admin':
            return redirect('admin_dashboard')
    
    return redirect('login')
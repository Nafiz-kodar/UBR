from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import SignUpForm
from .models import Profile, InspectionRequest, Message  # import your models
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404


def signup(request):
    """
    Handle user registration with user_type selection.
    After signup, redirect to the proper dashboard.
    """
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            # If the user selected `Admin` during signup, grant Django admin privileges.
            # WARNING: this makes any signup selecting Admin a true superuser.
            if form.cleaned_data.get('user_type') == 'Admin':
                user.is_staff = True
                user.is_superuser = True
                user.save()
            # Create or update Profile with selected user_type
            Profile.objects.update_or_create(
                user=user,
                defaults={'user_type': form.cleaned_data['user_type']}
            )
            login(request, user)
            messages.success(
                request,
                f'Account created successfully! Welcome, {user.username}!'
            )
            return redirect('dashboard_redirect')
    else:
        form = SignUpForm()

    return render(request, 'registration/signup.html', {'form': form})


def home(request):
    """
    Simple home page view.
    """
    return render(request, 'home.html')


@login_required
def dashboard_redirect(request):
    """
    Redirect users to the correct dashboard based on user_type.
    """
    profile = request.user.profile
    if profile.user_type == 'Owner':
        return redirect('owner_dashboard')
    elif profile.user_type == 'Inspector':
        return redirect('inspector_dashboard')
    elif profile.user_type == 'Admin':
        return redirect('admin_dashboard')
    else:
        return redirect('home')


@login_required
def owner_dashboard(request):
    """
    Show inspection requests for the logged-in building owner.
    """
    requests = InspectionRequest.objects.filter(owner=request.user)
    return render(request, 'owner/dashboard.html', {'data': requests})


@login_required
def inspector_dashboard(request):
    """
    Show inspection requests assigned to the logged-in inspector.
    """
    requests = InspectionRequest.objects.filter(inspector=request.user)
    return render(request, 'inspector/dashboard.html', {'data': requests})


@login_required
def admin_dashboard(request):
    """
    Show all inspection requests to admin with optional balance info.
    """
    requests = InspectionRequest.objects.all()
    # get or create single AdminBalance row
    from .models import AdminBalance, Profile
    admin_balance_obj, _ = AdminBalance.objects.get_or_create(pk=1)
    # pending inspector approvals
    pending_inspectors = Profile.objects.filter(user_type='Inspector', is_approved=False)
    return render(request, 'admin/dashboard.html', {'data': requests, 'admin_balance': admin_balance_obj, 'pending_inspectors': pending_inspectors})


# views.py
from django.contrib.auth import logout
from django.shortcuts import redirect

def custom_logout(request):
    logout(request)
    return redirect('home')


@login_required
def request_inspection(request):
    """Owner: request an inspection (simple handler)."""
    if request.method == 'POST':
        location = request.POST.get('location') or request.POST.get('building_location')
        # Create InspectionRequest with minimal required fields
        InspectionRequest.objects.create(owner=request.user, building_location=location)
        messages.success(request, 'Inspection request submitted.')
        return redirect('owner_dashboard')
    return render(request, 'owner/request_inspection.html')


@login_required
def owner_complaint(request):
    """Submit a complaint to an inspector. Template expects `inspectors` context."""
    inspectors = User.objects.filter(profile__user_type='Inspector')
    if request.method == 'POST':
        # No Complaint model in repo — just flash a message for now
        messages.success(request, 'Complaint submitted to the inspector.')
        return redirect('owner_dashboard')
    return render(request, 'owner/complaints.html', {'inspectors': inspectors})


@login_required
def inbox(request):
    """Show messages received by the current user."""
    received = Message.objects.filter(recipient=request.user).order_by('-sent_at')
    return render(request, 'messages/inbox.html', {'messages': received})


@login_required
def payment(request, pk):
    """Handle a simple payment flow for an InspectionRequest."""
    req = get_object_or_404(InspectionRequest, pk=pk)
    # prefer request-specific fee if set
    amount = req.fee if getattr(req, 'fee', None) else 500
    success = False
    if request.method == 'POST':
        # get chosen method (demo only)
        method = request.POST.get('method', 'Demo')
        # simulate payment success: create Payment and update admin balance
        success = True
        from .models import Payment, AdminBalance
        Payment.objects.create(payer=request.user, inspection_request=req, amount=amount)
        # mark request as Paid
        req.status = 'Paid'
        req.save()
        admin_balance_obj, _ = AdminBalance.objects.get_or_create(pk=1)
        admin_balance_obj.balance = (admin_balance_obj.balance or 0) + amount
        admin_balance_obj.save()
    return render(request, 'owner/payment.html', {'amount': amount, 'success': success})


@login_required
def owner_payments(request):
    """List owner's inspection requests to pick one for payment."""
    requests = InspectionRequest.objects.filter(owner=request.user).order_by('-created_at')
    return render(request, 'owner/payments_list.html', {'requests': requests})


@login_required
def admin_approve_inspectors(request):
    from .models import Profile
    if request.method == 'POST':
        uid = request.POST.get('profile_id')
        action = request.POST.get('action')
        profile = Profile.objects.get(pk=uid)
        if action == 'approve':
            profile.is_approved = True
            profile.save()
            messages.success(request, f'Inspector {profile.user.username} approved.')
        elif action == 'reject':
            profile.user.delete()
            messages.success(request, f'Inspector {profile.user.username} rejected and user removed.')
        return redirect('admin_dashboard')
    pending = Profile.objects.filter(user_type='Inspector', is_approved=False)
    return render(request, 'admin/approve_inspectors.html', {'pending': pending})


@login_required
def admin_assign_inspector(request, pk=None):
    from .models import Profile
    req = None
    if pk:
        req = get_object_or_404(InspectionRequest, pk=pk)
    inspectors = User.objects.filter(profile__user_type='Inspector', profile__is_approved=True, profile__is_banned=False)
    if request.method == 'POST':
        inspector_id = request.POST.get('inspector')
        inspector = User.objects.get(pk=inspector_id)
        req.inspector = inspector
        req.status = 'Assigned'
        req.save()
        messages.success(request, 'Inspector assigned.')
        return redirect('admin_dashboard')
    return render(request, 'admin/assign_inspector.html', {'inspectors': inspectors, 'request_obj': req})


@login_required
def inspector_inspection_view(request, pk):
    # Inspector view for a specific inspection request
    req = get_object_or_404(InspectionRequest, pk=pk)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'approve':
            # create report
            structural = request.POST.get('structural')
            checklist = request.POST.get('checklist')
            decision = 'Approved'
            report = InspectionReport.objects.create(inspection_request=req, inspector=request.user, structural_evaluation=structural, compliance_checklist=checklist, decision=decision, remarks=request.POST.get('remarks',''))
            req.status = 'Approved'
            req.save()
            messages.success(request, 'Inspection approved and report generated.')
            return redirect('inspector_dashboard')
        elif action == 'reject':
            reason = request.POST.get('reason')
            InspectionReport.objects.create(inspection_request=req, inspector=request.user, decision='Rejected', remarks=reason)
            req.status = 'Rejected'
            req.save()
            messages.success(request, 'Inspection rejected.')
            return redirect('inspector_dashboard')
    return render(request, 'inspector/inspect_request.html', {'req': req})


@login_required
def send_message(request):
    """Send a new internal message to another user."""
    users = User.objects.exclude(pk=request.user.pk)
    if request.method == 'POST':
        recipient_id = request.POST.get('recipient')
        subject = request.POST.get('subject', '')
        body = request.POST.get('body', '')
        recipient = get_object_or_404(User, pk=recipient_id)
        Message.objects.create(sender=request.user, recipient=recipient, subject=subject, body=body)
        messages.success(request, 'Message sent.')
        return redirect('inbox')
    return render(request, 'messages/send.html', {'users': users})


@login_required
def view_message(request, pk):
    """View a received message and optionally reply."""
    msg = get_object_or_404(Message, pk=pk)
    # Only allow recipient or sender to view (recipient can reply)
    if request.user != msg.recipient and request.user != msg.sender:
        messages.error(request, 'Permission denied.')
        return redirect('inbox')
    if request.user == msg.recipient and not msg.is_read:
        msg.is_read = True
        msg.save()
    if request.method == 'POST':
        # reply
        reply_body = request.POST.get('body', '')
        Message.objects.create(sender=request.user, recipient=msg.sender, subject=f'Re: {msg.subject}', body=reply_body)
        messages.success(request, 'Reply sent.')
        return redirect('inbox')
    return render(request, 'messages/view.html', {'msg': msg})

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.db.models import Sum
from .models import UserProfile, CharityActivity, Event, EventRegistration, Donation, Post, Comment, Like
from .forms import UserUpdateForm, ProfileUpdateForm
from .mpesa import stk_push
import json
import requests

@ensure_csrf_cookie
def home(request):
    """Home page showing recent activities and events"""
    recent_activities = CharityActivity.objects.all().order_by('-date_posted')[:10]
    upcoming_events = Event.objects.filter(event_date__gte=timezone.now()).order_by('event_date')[:5]
    recent_posts = Post.objects.all().order_by('-created_at')[:10]
    total_users = UserProfile.objects.count()
    total_activities = CharityActivity.objects.count()
    total_donations = Donation.objects.aggregate(total=Sum('amount_kes'))['total'] or 0
    total_events = Event.objects.count()
    
    context = {
        'recent_activities': recent_activities,
        'upcoming_events': upcoming_events,
        'recent_posts': recent_posts,
        'total_users': total_users,
        'total_activities': total_activities,
        'total_donations': total_donations,
        'total_events': total_events,
    }
    return render(request, 'home.html', context)

def register(request):
    """User registration"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    """User login"""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                UserProfile.objects.get_or_create(user=user)
                messages.info(request, f'You are now logged in as {username}.')
                return redirect('home')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    """User logout"""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')

@login_required
def profile(request):
    """User profile page"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    user_activities = CharityActivity.objects.filter(user=request.user).order_by('-date_posted')
    user_donations = Donation.objects.filter(user=request.user).order_by('-date_donated')
    user_events = EventRegistration.objects.filter(user=request.user).select_related('event')
    
    context = {
        'profile': profile,
        'user_activities': user_activities,
        'user_donations': user_donations,
        'user_events': user_events,
    }
    return render(request, 'profile.html', context)

@login_required
def user_profile(request, username):
    """Public profile page for viewing another user's posts."""
    profile_user = get_object_or_404(User, username=username)
    profile, _ = UserProfile.objects.get_or_create(user=profile_user)
    user_posts = Post.objects.filter(user=profile_user).order_by('-created_at')

    context = {
        'profile_user': profile_user,
        'profile': profile,
        'user_posts': user_posts,
    }
    return render(request, 'user_profile.html', context)

@login_required
def post_charity_activity(request):
    """Post a new charity activity"""
    if request.method == 'POST':
        description = request.POST.get('description')
        if description:
            activity = CharityActivity.objects.create(
                user=request.user,
                description=description,
                points_earned=50  # Fixed points for charity activity
            )
            # Update user points
            profile, created = UserProfile.objects.get_or_create(user=request.user)
            profile.points += activity.points_earned
            profile.save()
            
            messages.success(request, f'Charity activity posted! You earned {activity.points_earned} points.')
            return redirect('home')
        else:
            messages.error(request, 'Please describe your charity activity.')
    return render(request, 'post_activity.html')

@login_required
def donate(request):
    """Handle donations in Kenyan Shillings via MPesa Daraja/STK Push."""
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        amount = request.POST.get('amount')
        phone_number = request.POST.get('phone_number') or profile.phone_number
        message = request.POST.get('message', '')

        if not phone_number:
            messages.error(request, 'Please provide a valid phone number to complete the MPesa payment.')
        elif not amount or float(amount) <= 0:
            messages.error(request, 'Please enter a valid donation amount.')
        else:
            try:
                response = stk_push(
                    phone_number=phone_number,
                    amount=amount,
                    account_ref='SparkHubDonation',
                    description=message or 'SparkHub donation',
                )
                if response.get('ResponseCode') in ('0', 0):
                    Donation.objects.create(
                        user=request.user,
                        amount_kes=amount,
                        message=message,
                    )
                    messages.success(request, 'Donation request sent to MPesa. Please complete the payment on your phone.')
                    return redirect('home')
                else:
                    error_msg = response.get('ResponseDescription', response.get('errorMessage', 'MPesa request failed.'))
                    messages.error(request, f'MPesa error: {error_msg}')
            except Exception as exc:
                import logging
                logging.error(f'Donation error: {exc}', exc_info=True)
                messages.error(request, f'Payment request failed: {str(exc)}. Please check your phone number and try again.')

    return render(request, 'donate.html', {'profile': profile})

@login_required
def events(request):
    """List all events"""
    upcoming_events = Event.objects.filter(event_date__gte=timezone.now()).order_by('event_date')
    past_events = Event.objects.filter(event_date__lt=timezone.now()).order_by('-event_date')
    
    context = {
        'upcoming_events': upcoming_events,
        'past_events': past_events,
    }
    return render(request, 'events.html', context)

@login_required
def event_detail(request, event_id):
    """Event detail page"""
    event = get_object_or_404(Event, id=event_id)
    user_registered = EventRegistration.objects.filter(user=request.user, event=event).exists()
    
    context = {
        'event': event,
        'user_registered': user_registered,
    }
    return render(request, 'event_detail.html', context)

@login_required
def register_for_event(request, event_id):
    """Register for an event"""
    if request.method == 'POST':
        event = get_object_or_404(Event, id=event_id)
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        
        # Check if user has enough points
        if profile.points >= event.required_points:
            # Check if already registered
            if not EventRegistration.objects.filter(user=request.user, event=event).exists():
                EventRegistration.objects.create(user=request.user, event=event)
                messages.success(request, f'Successfully registered for {event.title}!')
            else:
                messages.info(request, 'You are already registered for this event.')
        else:
            needed_points = event.required_points - profile.points
            messages.error(request, f'You need {needed_points} more points to register for this event. Earn points by posting charity activities!')
    
    return redirect('event_detail', event_id=event_id)

@login_required
@ensure_csrf_cookie
def social_feed(request):
    """Social media feed"""
    posts = Post.objects.all().order_by('-created_at')
    
    context = {
        'posts': posts,
    }
    return render(request, 'social_feed.html', context)

@login_required
def create_post(request):
    """Create a social media post"""
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        video = request.FILES.get('video')

        if content or video:
            post = Post.objects.create(
                user=request.user,
                content=content,
                video=video,
            )
            messages.success(request, 'Post created!')
            return redirect('social_feed')
        else:
            messages.error(request, 'Post cannot be empty. Add text or a video.')
    return render(request, 'create_post.html')

@login_required
def settings(request):
    """User settings dashboard."""
    return render(request, 'settings.html')

@login_required
def edit_profile(request):
    """Edit user account and profile information."""
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=profile)

    return render(request, 'edit_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })

@login_required
def change_password(request):
    """Change the current user's password."""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password has been changed.')
            return redirect('settings')
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'change_password.html', {'form': form})

@login_required
def two_factor(request):
    """Two-factor authentication settings placeholder."""
    if request.method == 'POST':
        messages.success(request, 'Two-factor settings saved.')
        return redirect('settings')
    return render(request, 'two_factor.html')

@login_required
def email_preferences(request):
    """Email notification preferences."""
    if request.method == 'POST':
        messages.success(request, 'Email preferences saved.')
        return redirect('settings')
    return render(request, 'email_preferences.html')

@login_required
def notification_settings(request):
    """In-app notification preferences."""
    if request.method == 'POST':
        messages.success(request, 'Notification settings saved.')
        return redirect('settings')
    return render(request, 'notification_settings.html')

@login_required
def privacy_settings(request):
    """Privacy controls."""
    if request.method == 'POST':
        messages.success(request, 'Privacy settings saved.')
        return redirect('settings')
    return render(request, 'privacy_settings.html')

def terms_of_service(request):
    """Static terms of service page."""
    return render(request, 'terms_of_service.html')

@login_required
@require_http_methods(["POST"])
def like_post(request):
    """Like a post via AJAX"""
    try:
        data = json.loads(request.body)
        post_id = data.get('post_id')
        post = get_object_or_404(Post, id=post_id)
        
        like, created = Like.objects.get_or_create(post=post, user=request.user)
        
        if not created:
            # Unlike if already liked
            like.delete()
            liked = False
        else:
            liked = True
        
        like_count = post.likes.count()
        return JsonResponse({'liked': liked, 'like_count': like_count})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
@require_http_methods(["POST"])
def comment_post(request):
    """Comment on a post via AJAX"""
    try:
        data = json.loads(request.body)
        post_id = data.get('post_id')
        content = data.get('content')
        post = get_object_or_404(Post, id=post_id)
        
        if content:
            comment = Comment.objects.create(
                post=post,
                user=request.user,
                content=content
            )
            return JsonResponse({
                'success': True,
                'comment': {
                    'id': comment.id,
                    'content': comment.content,
                    'user': comment.user.username,
                    'created_at': comment.created_at.strftime('%b %d, %Y %H:%M')
                }
            })
        else:
            return JsonResponse({'error': 'Comment cannot be empty'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
def process_donation(request):
    """Handle donation processing via MPesa Daraja/STK Push."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=405)

    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    try:
        data = json.loads(request.body)
        amount = data.get('amount')
        phone_number = data.get('phone_number') or profile.phone_number
        message = data.get('message', '')

        if not phone_number:
            return JsonResponse({'success': False, 'error': 'Phone number is required.'}, status=400)
        if not amount or float(amount) <= 0:
            return JsonResponse({'success': False, 'error': 'Amount must be greater than zero.'}, status=400)

        response = stk_push(
            phone_number=phone_number,
            amount=amount,
            account_ref='SparkHubDonation',
            description=message or 'SparkHub donation',
        )

        if response.get('ResponseCode') in ('0', 0):
            Donation.objects.create(
                user=request.user,
                amount_kes=amount,
                message=message,
            )
            return JsonResponse({'success': True, 'data': response})

        error_msg = response.get('ResponseDescription', response.get('errorMessage', 'MPesa request failed.'))
        return JsonResponse({'success': False, 'error': error_msg, 'data': response})
    except Exception as exc:
        import logging
        logging.error(f'process_donation error: {exc}', exc_info=True)
        return JsonResponse({'success': False, 'error': str(exc)})


@csrf_exempt
def mpesa_callback(request):
    """Accept MPesa payment callback notifications from Safaricom."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=405)

    try:
        callback_data = json.loads(request.body)
        print('MPesa callback received:', callback_data)
        return JsonResponse({'success': True})
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON.'}, status=400)

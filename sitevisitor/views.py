from django.shortcuts import render, redirect
from .models import MentorProfile, Review, UserProfile, Course  # Import UserProfile model
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth import authenticate, login as auth_login
from .forms import ContactForm, LoginForm,UserRegistrationForm 
from django.contrib.auth import login as auth_login 


def landing(request):
    featured_courses = Course.objects.filter(status='published')[:6]
    mentors = MentorProfile.objects.select_related('user').all()[:4]
    reviews = Review.objects.select_related('user', 'course').all()[:3]
    
    context = {
        'featured_courses': featured_courses,
        'mentors': mentors,
        'reviews': reviews,
    }
    return render(request, 'sitevisitor/home.html', context)


def mentors(request):
    mentors = MentorProfile.objects.select_related('user').all()
    return render(request, 'sitevisitor/mentors.html', {'mentors': mentors})

def course_overview(request):
    courses = Course.objects.filter(status='published').select_related('mentor')
    return render(request, 'sitevisitor/courses.html', {'courses': courses})

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save() 
            messages.success(request, "Your message has been sent! We'll get back to you soon.")
            return redirect('contact')  
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ContactForm()

    return render(request, 'sitevisitor/contact.html', {'form': form})


def sign_up(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.get_or_create(user=user)
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            if user is not None:
                login(request, user)
                role = user.userprofile.role  # Assumes profile creation successful
                messages.success(request, f"Account created successfully! Welcome, {user.first_name}!")
                if role == 'student':
                    return redirect('student_home')
                else:
                    return redirect('landing')
            else:
                messages.error(request, "Authentication failed.")
                return redirect('sign_in')
        else:
            messages.error(request, "There was an error creating your account. Please check the form for specific errors.")
    else:
        form = UserRegistrationForm()
    return render(request, 'sitevisitor/sign_up.html', {'form': form})


def sign_in(request):
    """Handle the sign-in process for site visitors."""
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                try:
                    user_profile = user.userprofile
                    role = user_profile.role
                    status = user_profile.status
                    if status != 'active':
                        messages.error(request, "Your account is currently inactive. Please contact support.")
                        return redirect('sign_in')

                except UserProfile.DoesNotExist:
                    messages.error(request, "User profile not found.")
                    return redirect('sign_in')

                # Log the user in and redirect based on role if the account is active
                auth_login(request, user)
                messages.success(request, f"Welcome back, {user.first_name}!")

                if role == 'student':
                    return redirect('student_home')
                elif role == 'mentor':
                    if status == 'active':
                        return redirect('landing')
                    else:
                        messages.info(request, "Your mentor application is pending approval.")
                        return redirect('landing')
                elif role == 'admin':  # Explicitly check for admin role
                    return redirect('admin_home')
                else:
                    return redirect('landing')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()

    return render(request, 'sitevisitor/sign_in.html', {'form': form})


def error_page(request):
    """Render the custom 404 error page."""
    return render(request, 'sitevisitor/404.html')

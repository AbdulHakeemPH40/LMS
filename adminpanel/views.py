
from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.forms import inlineformset_factory
from django.contrib.auth import logout as auth_logout
import logging
import random
import string
from django.utils import timezone
from .forms import UserProfileForm
from django.db.models import Count, Sum, F, DecimalField, Avg

from sitevisitor.forms import (CourseForm,
CourseCategoryForm, ModuleForm, LessonForm,MentorProfileForm,
VideoForm,PromotionForm,ResetPasswordForm
)
from sitevisitor.models import (
    Coupon, Course, User, CourseCategory, Module, Lesson,
    UserProfile,Enrollment,MentorProfile,Video,Contact,Promotion,Review
)


logger = logging.getLogger(__name__)

# Formset for managing videos within a lesson
VideoFormSet = inlineformset_factory(
    Lesson,
    Video,
    form=VideoForm,
    fields=['title', 'video_file', 'video_url', 'video_type', 'order', 'is_locked'],
    extra=1,
    can_delete=True
)

# Helper function to check if the user is an admin
def is_admin(user):
    return user.is_staff and hasattr(user, 'userprofile') and user.userprofile.role == 'admin'


@login_required(login_url='/404/')
@user_passes_test(is_admin)
def admin_home(request):
    # Get the total number of users
    total_users = UserProfile.objects.filter(role='student').count()

    # Get the total number of courses
    total_courses = Course.objects.count()

    # Get total lessons count
    total_lessons = Lesson.objects.count()
    
    total_revenue = Enrollment.objects.filter(status='active').aggregate(
    total_revenue=Sum(F('course__price'), output_field=DecimalField())
    )['total_revenue'] or 0


    # Calculate Growth Rate: Here we calculate the growth in courses over the past month
    one_month_ago = timezone.now() - timedelta(days=30)
    new_courses = Course.objects.filter(created_at__gte=one_month_ago).count()
    old_courses = Course.objects.filter(created_at__lt=one_month_ago).count()
    growth_rate = (new_courses - old_courses) / old_courses * 100 if old_courses > 0 else 0

    # Calculate Average Ratings for all courses
    average_ratings = Review.objects.aggregate(average_rating=Avg('rating'))['average_rating'] or 0

    # Fetch all courses (no need to filter for modules here)
    courses = Course.objects.all()

    # Pass the data to the template
    context = {
        'total_users': total_users,
        'total_courses': total_courses,
        'total_lessons': total_lessons,
        'total_revenue': total_revenue,
        'growth_rate': growth_rate,
        'average_ratings': average_ratings,
        'courses': courses,  # Pass all courses to the template
    }
    
    return render(request, 'adminpanel/admin_home.html', context)


@login_required(login_url='/404/')
@user_passes_test(is_admin)
def admin_view_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    # Fetch the modules related to this course
    modules = Module.objects.filter(course=course)

    context = {
        'course': course,
        'modules': modules  # Pass the modules to the template
    }
    return render(request, 'adminpanel/view_course.html', context)

def manage_courses(request):
    courses = Course.objects.all().prefetch_related('modules__lessons__lesson_videos')  
    # rest of the view...
    return render(request, 'adminpanel/manage_courses.html', {'courses': courses})


@login_required(login_url='/404/')
@user_passes_test(is_admin)
def create_course(request):
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Course created successfully!")
            return redirect('manage_courses')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CourseForm()
    return render(request, 'adminpanel/create_course.html', {'form': form})

@login_required(login_url='/404/')
@user_passes_test(is_admin)
def edit_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, "Course updated successfully!")
            return redirect('manage_courses')
        messages.error(request, "Please correct the errors below.")
    else:
        form = CourseForm(instance=course)
    return render(request, 'adminpanel/edit_course.html', {'form': form, 'course': course})

# View to display all contact form submissions
@login_required(login_url='/404/')
@user_passes_test(is_admin)
def manage_contact_submissions(request):
    # Fetch all contact form submissions from the database
    contact_submissions = Contact.objects.all().order_by('-submitted_at')  # Order by submission date (latest first)

    context = {
        'contact_submissions': contact_submissions,
    }

    return render(request, 'adminpanel/manage_contact.html', context)

# View to see full details of a specific contact submission
@login_required(login_url='/404/')
@user_passes_test(is_admin)
def view_contact(request, contact_id):
    # Fetch the specific contact submission by its ID
    contact_submission = get_object_or_404(Contact, id=contact_id)

    context = {
        'contact_submission': contact_submission
    }

    return render(request, 'adminpanel/view_contact.html', context)

@login_required(login_url='/404/')
@user_passes_test(is_admin)
def delete_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == 'POST':
        course.delete()
        messages.success(request, 'Course deleted successfully.')
        return redirect('manage_courses')
    return render(request, 'adminpanel/delete_course.html', {'course': course})

@login_required(login_url='/404/')
@user_passes_test(is_admin)
def manage_modules(request, course_id):
    """
    Manage Modules: Displays all modules associated with a specific course.
    """
    course = get_object_or_404(Course, id=course_id)
    modules = course.modules.all()  # Fetch modules for the selected course
    all_courses = Course.objects.all()  # Fetch all courses for the course selection

    context = {
        'course': course,
        'modules': modules,
        'courses': all_courses,  # Pass all courses to the template
    }
    return render(request, 'adminpanel/manage_modules.html', context)

@login_required(login_url='/404/')
@user_passes_test(is_admin)
def add_module(request, course_id):
    """
    Add Module: Handles the addition of a new module for a specific course.
    """
    course = get_object_or_404(Course, id=course_id)  # Fetch the course object

    if request.method == 'POST':
        form = ModuleForm(request.POST)
        if form.is_valid():
            module = form.save(commit=False)  # Do not save to the database yet
            module.course = course  # Associate the module with the course
            module.save()  # Now save it
            messages.success(request, 'Module added successfully!')
            return redirect('manage_modules', course_id=course.id)  # Redirect to manage modules
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ModuleForm()

    context = {
        'form': form,
        'course': course,  # Pass the course to the template
    }
    return render(request, 'adminpanel/add_module.html', context)

@login_required(login_url='/404/')
@user_passes_test(is_admin)
def edit_module(request, module_id):
    """
    Edit Module: Allows editing of an existing module within a course.
    """
    module = get_object_or_404(Module, id=module_id)
    if request.method == 'POST':
        form = ModuleForm(request.POST, instance=module)
        if form.is_valid():
            form.save()
            messages.success(request, 'Module updated successfully!')
            return redirect('admin_view_course', course_id=module.course.id)
        else:
            messages.error(request, "Please correct the errors below.")
            logger.error("ModuleForm errors: %s", form.errors)
    else:
        form = ModuleForm(instance=module)
    context = {
        'form': form,
        'module': module
    }
    return render(request, 'adminpanel/edit_module.html', context)


@login_required(login_url='/404/')
@user_passes_test(is_admin)
def delete_module(request, module_id):
    """
    Delete Module: Handles the deletion of a specific module from a course.
    """
    module = get_object_or_404(Module, id=module_id)
    course_id = module.course.id
    if request.method == 'POST':
        module.delete()
        messages.success(request, 'Module deleted successfully!')
        return redirect('admin_view_course', course_id=course_id)
    context = {
        'module': module
    }
    return render(request, 'adminpanel/delete_module.html', context)

@login_required(login_url='/404/')
@user_passes_test(is_admin)
def manage_lessons(request):
    courses = Course.objects.prefetch_related('modules__lessons').all()
    context = {
        'courses': courses,
    }
    return render(request, 'adminpanel/manage_lessons.html', context)

@login_required(login_url='/404/')
@user_passes_test(is_admin)
def add_lesson(request, module_id):
    module = get_object_or_404(Module, id=module_id)
    course = module.course

    if request.method == 'POST':
        lesson_form = LessonForm(request.POST)
        if lesson_form.is_valid():
            lesson = lesson_form.save(commit=False)
            lesson.module = module
            lesson.save()

            messages.success(request, "Lesson added successfully!")
            return redirect('admin_view_course', course_id=course.id)  # Redirect with course_id
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        lesson_form = LessonForm()

    context = {
        'module': module,
        'course': course,
        'lesson_form': lesson_form,
    }

    return render(request, 'adminpanel/add_lesson.html', context)


@login_required(login_url='/404/')
@user_passes_test(is_admin)
def edit_lesson(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    if request.method == 'POST':
        form = LessonForm(request.POST, instance=lesson)
        if form.is_valid():
            form.save()
            messages.success(request, 'Lesson updated successfully!')
            return redirect('manage_lessons')
        messages.error(request, "Please correct the errors below.")
    else:
        form = LessonForm(instance=lesson)
    return render(request, 'adminpanel/edit_lesson.html', {'form': form, 'lesson': lesson})

@login_required(login_url='/404/')
@user_passes_test(is_admin)
def delete_lesson(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    if request.method == 'POST':
        lesson.delete()
        messages.success(request, 'Lesson deleted successfully!')
        return redirect('manage_lessons')
    return render(request, 'adminpanel/delete_lesson.html', {'lesson': lesson})


# views.py (adminpanel)
@login_required(login_url='/404/')
@user_passes_test(is_admin)
def manage_videos(request, course_id=None):
    # Prefetch the lesson videos correctly using the 'lesson_videos' related name
    courses = Course.objects.prefetch_related(
        'modules__lessons__lesson_videos'  # Correct related_name for lesson videos
    ).all()

    selected_course = get_object_or_404(Course, id=course_id) if course_id else None
    
    return render(request, 'adminpanel/manage_videos.html', {'courses': courses, 'selected_course': selected_course})




@login_required(login_url='/404/')
@user_passes_test(is_admin)
def add_video(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    if request.method == 'POST':
        form = VideoForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.save(commit=False)
            video.lesson = lesson
            video.save()
            messages.success(request, 'Video added successfully!')
            return redirect('manage_videos_course', course_id=lesson.module.course.id)  # Update to match URL names
        messages.error(request, "Please correct the errors below.")
    else:
        form = VideoForm()
    return render(request, 'adminpanel/add_video.html', {'form': form, 'lesson': lesson})



@login_required(login_url='/404/')
@user_passes_test(is_admin)
def edit_video(request, video_id):
    """
    View to edit an existing video in the admin panel.
    """
    video = get_object_or_404(Video, id=video_id)
    
    if request.method == 'POST':
        form = VideoForm(request.POST, request.FILES, instance=video)
        if form.is_valid():
            form.save()
            messages.success(request, 'Video updated successfully!')
            return redirect('manage_videos')  # Redirect back to the videos management page
        messages.error(request, "Please correct the errors below.")
    else:
        form = VideoForm(instance=video)

    return render(request, 'adminpanel/edit_video.html', {'form': form, 'video': video})


@login_required(login_url='/404/')
@user_passes_test(is_admin)
def delete_video(request, video_id):
    video = get_object_or_404(Video, id=video_id)
    if request.method == 'POST':
        video.delete()
        messages.success(request, 'Video deleted successfully!')
        return redirect('manage_videos')
    return render(request, 'adminpanel/delete_video.html', {'video': video})

# -------------------------
# Category Management Views
# -------------------------


@login_required(login_url='/404/')
@user_passes_test(is_admin)
def category_list(request):
    categories = CourseCategory.objects.all()
    return render(request, 'adminpanel/manage_categories.html', {'categories': categories})

@login_required(login_url='/404/')
@user_passes_test(is_admin)
def create_category(request):
    if request.method == 'POST':
        form = CourseCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category created successfully!')
            return redirect('category_list')
        messages.error(request, "Please correct the errors below.")
    else:
        form = CourseCategoryForm()
    return render(request, 'adminpanel/create_category.html', {'form': form})

@login_required(login_url='/404/')
@user_passes_test(is_admin)
def edit_category(request, category_id):
    category = get_object_or_404(CourseCategory, id=category_id)
    if request.method == 'POST':
        form = CourseCategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully!')
            return redirect('category_list')
        messages.error(request, "Please correct the errors below.")
    else:
        form = CourseCategoryForm(instance=category)
    return render(request, 'adminpanel/edit_category.html', {'form': form, 'category': category})


@login_required(login_url='/404/')
@user_passes_test(is_admin)
def mentors_list(request):
    mentors = MentorProfile.objects.select_related('user')
    return render(request, 'adminpanel/manage_mentors.html', {'mentors': mentors})


@login_required(login_url='/404/')
@user_passes_test(is_admin)
def add_mentor(request):
    if request.method == 'POST':
        form = MentorProfileForm(request.POST, request.FILES)
        if form.is_valid():
            mentor_profile = form.save(commit=False)
            user_profile = UserProfile.objects.get(user=mentor_profile.user)
            user_profile.role = 'mentor'
            user_profile.save()
            mentor_profile.save()
            messages.success(request, 'Mentor added successfully.')
            return redirect('manage_mentors')
    else:
        form = MentorProfileForm()
    return render(request, 'adminpanel/add_mentor.html', {'form': form})


@login_required(login_url='/404/')
@user_passes_test(is_admin)
def edit_mentor(request, mentor_id):
    mentor = get_object_or_404(MentorProfile, id=mentor_id)
    
    if request.method == 'POST':
        form = MentorProfileForm(request.POST, request.FILES, instance=mentor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Mentor updated successfully.')
            return redirect('manage_mentors')  # Redirect to the mentor management page or list of mentors
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = MentorProfileForm(instance=mentor)
    
    context = {
        'form': form,
        'mentor': mentor,
    }
    return render(request, 'adminpanel/edit_mentor.html', context)


@login_required(login_url='/404/')
@user_passes_test(is_admin)
def delete_mentor(request, mentor_id):
    mentor = get_object_or_404(MentorProfile, id=mentor_id)
    if request.method == 'POST':
        mentor.delete()
        messages.success(request, 'Mentor deleted successfully.')
        return redirect('manage_mentors')
    return render(request, 'adminpanel/delete_mentor.html', {'mentor': mentor})

@login_required(login_url='/404/')
@user_passes_test(is_admin)
def view_mentor(request, mentor_id):
    # Retrieve the mentor profile or return a 404 if not found
    mentor = get_object_or_404(MentorProfile, id=mentor_id)

    context = {
        'mentor': mentor,
    }
    return render(request, 'adminpanel/view_mentor.html', context)

@login_required(login_url='/404/')
@user_passes_test(is_admin)
def view_user(request, user_id):
    user_profile = get_object_or_404(UserProfile, user_id=user_id)
    user = user_profile.user
    
    # Retrieve active coupons associated with the user
    coupons = Coupon.objects.filter(user=user, active=True)
    
    # Only show courses that don’t already have an active coupon for this user
    available_courses = Course.objects.exclude(
        id__in=coupons.values_list('course_id', flat=True)
    )
    
    context = {
        'user': user,
        'user_profile': user_profile,
        'coupons': coupons,
        'available_courses': available_courses
    }
    return render(request, 'adminpanel/view_user.html', context)



def generate_random_code(length=12):
    characters = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(random.choice(characters) for _ in range(length))

@login_required(login_url='/404/')
@user_passes_test(is_admin)
def generate_coupon(request, user_id):
    user_profile = get_object_or_404(UserProfile, user_id=user_id)
    user = user_profile.user
    if request.method == "POST":
        course_id = request.POST.get("course")
        course = get_object_or_404(Course, id=course_id)
        
        # Ensure there's no existing coupon for the selected course and user
        if not Coupon.objects.filter(course=course, user=user, active=True).exists():
            # Determine expiration based on the course duration
            valid_to = timezone.now() + (
                timedelta(days=course.duration_value * 30) if course.duration_type == 'month' else timedelta(weeks=course.duration_value)
            )
            
            # Create the coupon and associate it with the user
            coupon = Coupon.objects.create(
                code=generate_random_code(),
                course=course,
                user=user,  # Associate the coupon with the user
                valid_from=timezone.now(),
                valid_to=valid_to,
                active=True,
            )
            messages.success(request, f"Coupon '{coupon.code}' generated for {course.title} and assigned to {user.username}.")
        else:
            messages.error(request, f"A coupon for '{course.title}' already exists for this user.")
    
    return redirect('view_user', user_id=user.id)




@login_required(login_url='/404/')
@user_passes_test(is_admin)
def delete_coupon(request, coupon_id):
    coupon = get_object_or_404(Coupon, id=coupon_id)
    user_id = Enrollment.objects.filter(course=coupon.course).values_list('user', flat=True).first()

    # Delete the coupon
    coupon.delete()
    messages.success(request, "Coupon deleted successfully.")
    
    # Redirect to the user’s view page if user_id is found
    if user_id:
        return redirect('view_user', user_id=user_id)
    else:
        return redirect('manage_users')

@login_required(login_url='/404/')
@user_passes_test(is_admin)
def delete_category(request, category_id):
    category = get_object_or_404(CourseCategory, id=category_id)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted successfully!')
        return redirect('category_list')
    return render(request, 'adminpanel/delete_category.html', {'category': category})

# -------------------------
# User Management Views
# -------------------------

@login_required(login_url='/404/')
@user_passes_test(is_admin)
def manage_users(request):
    users = User.objects.filter(is_superuser=False, userprofile__role__in=['student', 'mentor']).select_related('userprofile')
    return render(request, 'adminpanel/manage_users.html', {'users': users})

@login_required(login_url='/404/')
@user_passes_test(is_admin)
def activate_user(request, user_id):
    user_profile = get_object_or_404(UserProfile, user_id=user_id)
    user_profile.status = 'active'
    user_profile.save()
    messages.success(request, "User activated successfully.")
    return redirect('manage_users')

@login_required(login_url='/404/')
@user_passes_test(is_admin)
def deactivate_user(request, user_id):
    user_profile = get_object_or_404(UserProfile, user_id=user_id)
    user_profile.status = 'inactive'
    user_profile.save()
    messages.success(request, "User deactivated successfully.")
    return redirect('manage_users')


@login_required(login_url='/404/')
@user_passes_test(is_admin)
def logout_view(request):
    auth_logout(request)
    return redirect('landing')


@login_required(login_url='/404/')
@user_passes_test(is_admin)
def create_promotion(request):
    if request.method == 'POST':
        form = PromotionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Promotion created successfully!')
            return redirect('manage_promotions')  # Redirect to promotions management page
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PromotionForm()

    return render(request, 'adminpanel/add_promotion.html', {'form': form})

@login_required(login_url='/404/')
@user_passes_test(is_admin)
def edit_promotion(request, promotion_id):
    promotion = get_object_or_404(Promotion, id=promotion_id)
    if request.method == 'POST':
        form = PromotionForm(request.POST, instance=promotion)
        if form.is_valid():
            form.save()
            messages.success(request, 'Promotion updated successfully!')
            return redirect('manage_promotions')  # Redirect to manage promotions page
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PromotionForm(instance=promotion)

    return render(request, 'adminpanel/edit_promotion.html', {'form': form, 'promotion': promotion})

@login_required(login_url='/404/')
@user_passes_test(is_admin)
def manage_promotions(request):
    promotions = Promotion.objects.all()  # Get all promotions
    return render(request, 'adminpanel/manage_promotions.html', {'promotions': promotions})

@login_required(login_url='/404/')
@user_passes_test(is_admin)
def toggle_promotion_status(request, promotion_id):
    promotion = get_object_or_404(Promotion, id=promotion_id)
    promotion.is_active = not promotion.is_active  # Toggle the active status
    promotion.save()

    status = "activated" if promotion.is_active else "deactivated"
    messages.success(request, f'Promotion has been {status} successfully.')

    return redirect('manage_promotions')  # Redirect to the manage promotions page


@login_required(login_url='/404/')
@user_passes_test(is_admin)
def admin_profile(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('admin_profile')  # Redirect to the same page after saving
    else:
        form = UserProfileForm(instance=user_profile)

    context = {
        'user_profile': user_profile,
        'form': form
    }
    return render(request, 'adminpanel/admin_profile.html', context)


@login_required(login_url='/404/')
def admin_change_password(request):
    """
    Handle the admin's password change.
    """
    if request.user.is_staff:  # Check if the user is an admin
        if request.method == 'POST':
            form = ResetPasswordForm(request.user, request.POST)
            if form.is_valid():
                form.save()  # Save the new password
                update_session_auth_hash(request, request.user)  # Keep the user logged in after password change
                messages.success(request, 'Your password was successfully updated!')
                return redirect('admin_home')  # Redirect to the admin home page (adjust as needed)
            else:
                messages.error(request, 'Please correct the errors below.')
        else:
            form = ResetPasswordForm(request.user)  # Instantiate the form with the user instance

        context = {
            'form': form,
        }
        return render(request, 'adminpanel/admin_change_password.html', context)
    else:
        messages.error(request, 'You do not have permission to change this password.')
        return redirect('admin_home')  # Redirect to the admin home if the user is not an admin

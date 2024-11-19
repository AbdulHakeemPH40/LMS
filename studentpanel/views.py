# studentpanel/views.py
from django.contrib import messages
from django.contrib.auth import logout, update_session_auth_hash, get_user_model
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from django.urls import reverse
import logging
from django.views.decorators.http import require_POST
from django.utils import timezone
from urllib.parse import urlparse
from django.conf import settings
import os
from django.db.models import Prefetch
from django.utils import timezone


# Importing models from sitevisitor app
from sitevisitor.models import (
    Promotion,
    UserProfile,
    Comment,
    Enrollment,
    Course,
    Video,
    Module,
    Lesson,
    Video,
    Coupon,Review,
     
    
)

# Importing forms from sitevisitor app
from sitevisitor.forms import (
    UserProfileForm,
    ResetPasswordForm,
    CommentForm,
    ReviewForm

)

@login_required(login_url='/404/')
def student_home(request):
    # Get the promotions that are active
    promotions = Promotion.objects.filter(is_active=True)

    # Get the user's enrolled courses
    my_courses = Course.objects.filter(enrollment__user=request.user, status='published')

    # Get the course IDs of the courses the user is enrolled in
    enrolled_course_ids = my_courses.values_list('id', flat=True)

    # Get the available courses the user is not enrolled in
    explore_courses = Course.objects.exclude(enrollment__user=request.user).filter(status='published')

    context = {
        'my_courses': my_courses,
        'explore_courses': explore_courses,
        'promotions': promotions,  # Pass the promotions to the template
        'enrolled_course_ids': enrolled_course_ids,  # Pass the list of enrolled course IDs to the template
    }
    return render(request, 'studentpanel/student_home.html', context)

@login_required(login_url='/404/')
def view_profile(request):
    """
    Display and handle updating the user's own profile.
    """
    # Get or create a UserProfile instance for the user
    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('student_home')  # Redirect after successful update
        else:
            messages.error(request, "There was an error updating your profile.")
    else:
        form = UserProfileForm(instance=user_profile)

    context = {
        'form': form,
        'user_profile': user_profile,
    }
    return render(request, 'studentpanel/student_profile.html', context)


@login_required(login_url='/404/')
def edit_profile(request, user_id):
    """
    Edit another user's profile. Ensure that only authorized users can perform this action.
    """
    # Only allow users to edit their own profile
    if request.user.id != user_id:
        messages.error(request, "You are not authorized to edit this profile.")
        return redirect('student_home')

    user_profile = get_object_or_404(UserProfile, user__id=user_id)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile, user=user_profile.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('student_home')
        else:
            messages.error(request, "There was an error updating your profile.")
            logger.error("UserProfileForm errors: %s", form.errors)
    else:
        form = UserProfileForm(instance=user_profile, user=user_profile.user)

    context = {
        'form': form,
        'user_profile': user_profile,
    }
    return render(request, 'studentpanel/student_profile.html', context)


@login_required(login_url='/404/')
def reset_password(request):
    """
    Handle password reset for the user.
    """
    if request.method == 'POST':
        form = ResetPasswordForm(user=request.user, data=request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            request.user.set_password(new_password)
            request.user.save()
            update_session_auth_hash(request, request.user)  # Keeps the user logged in after password change
            messages.success(request, 'Your password has been updated successfully.')
            return redirect('student_home')
        else:
            messages.error(request, 'Please correct the errors below.')
            logger.error("ResetPasswordForm errors: %s", form.errors)
    else:
        form = ResetPasswordForm(user=request.user)
    return render(request, 'studentpanel/reset_password.html', {'form': form})




@login_required(login_url='/404/')
def add_comment(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.course = course  # Ensure the comment is linked to the course
            comment.user = request.user
            comment.save()
            
            messages.success(request, 'Your comment has been added successfully!')
            # Handle AJAX request
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': comment.message,
                    'username': comment.user.get_full_name(),
                    'profile_image': comment.user.userprofile.profile_image.url if comment.user.userprofile.profile_image else '/static/images/default_profile.png',
                    'posted_at': timezone.now().strftime('%B %d, %Y, %I:%M %p'),
                    'edit_url': reverse('edit_comment', args=[comment.id]),
                    'delete_url': reverse('delete_comment', args=[comment.id]),
                    'success_message': 'Your comment has been added successfully!'
                })

            return redirect('my_courses', course_id=course.id)
        else:
            messages.error(request, 'Failed to add comment. Please try again.')

    return redirect('course_detail', course_id=course.id)



@login_required(login_url='/404/')
def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, user=request.user)
    form = CommentForm(request.POST or None, instance=comment)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Comment updated successfully!')
        return redirect('my_courses', course_id=comment.course.id)
    return render(request, 'studentpanel/edit_comment.html', {'form': form, 'comment': comment})


@login_required(login_url='/404/')
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, user=request.user)
    course_id = comment.course.id
    comment.delete()
    messages.success(request, 'Comment deleted successfully!')
    return redirect('my_courses', course_id=course_id)    


@login_required(login_url='/404/')
def checkout(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    # Check if the user is already enrolled
    is_enrolled = Enrollment.objects.filter(user=request.user, course=course).exists()
    if is_enrolled:
        messages.info(request, "You are already enrolled in this course.")
        return redirect('my_courses', course_id=course.id)

    if request.method == 'POST':
        coupon_code = request.POST.get('coupon_code', '').strip()

        # Enforce the condition that the coupon is required
        if not coupon_code:
            messages.error(request, 'Coupon code is required to enroll in this course.')
            return redirect('checkout', course_id=course.id)  # Redirect back to the checkout page

        # Validate the coupon code if provided
        coupon = Coupon.objects.filter(
            code=coupon_code,
            course=course,
            user=request.user,  # Ensure the coupon is for the specific user
            valid_from__lte=timezone.now(),
            valid_to__gte=timezone.now(),
            active=True,
        ).first()

        if coupon:
            # Create enrollment for the user
            Enrollment.objects.get_or_create(user=request.user, course=course)
            coupon.active = False  # Mark the coupon as used
            coupon.save()
            messages.success(request, f'Successfully enrolled in {course.title} with coupon code {coupon_code}.')
            return redirect('my_courses', course_id=course.id)
        else:
            messages.error(request, "Invalid or expired coupon code for this course.")
            return redirect('checkout', course_id=course.id)  # Redirect back to the checkout page with error message

    else:
        # If it's a GET request, we still render the checkout page
        return render(request, 'studentpanel/checkout.html', {'course': course})


@login_required(login_url='/404/')
def sign_out(request):
    """
    Log out the user and redirect to the landing page.
    """
    logout(request)
    return redirect('landing')


User = get_user_model()
logger = logging.getLogger(__name__)

@login_required(login_url='/404/')
def my_courses(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    is_enrolled = Enrollment.objects.filter(user=request.user, course=course).exists()
    if not is_enrolled:
        messages.error(request, "You are not enrolled in this course.")
        return redirect('student_home')

    # Corrected to use 'lesson_videos' instead of 'videos' as the related_name
    modules = Module.objects.filter(course=course).prefetch_related(
        Prefetch(
            'lessons',
            queryset=Lesson.objects.prefetch_related(
                Prefetch(
                    'lesson_videos',  # Correct related_name here
                    queryset=Video.objects.order_by('order')
                )
            ).order_by('order')
        )
    ).order_by('order')

    comments = Comment.objects.filter(course=course).select_related('user__userprofile').order_by('-posted_at')
    
    current_video_embed_url = None
    selected_video_id = request.GET.get('video_id')
    current_video = Video.objects.filter(id=selected_video_id, lesson__module__course=course).first() if selected_video_id else None
    current_video_embed_url = current_video.get_video_src if current_video else None

    comment_form = CommentForm()
    review_form = ReviewForm()
    reviews = Review.objects.filter(course=course).select_related('user')

    context = {
        'course': course,
        'modules': modules,
        'comments': comments,
        'current_video': current_video,
        'current_video_embed_url': current_video_embed_url,
        'comment_form': comment_form,
        'review_form': review_form,
        'reviews': reviews,
        'active_tab': 'lessons',
    }
    return render(request, 'studentpanel/my_courses.html', context)


@login_required(login_url='/404/')
def explore_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    # Check if the user is enrolled
    user_enrollment = Enrollment.objects.filter(user=request.user, course=course).first()
    is_enrolled = user_enrollment is not None

    # Prefetch the lessons and their associated videos correctly
    modules = Module.objects.filter(course=course).prefetch_related(
        Prefetch(
            'lessons',
            queryset=Lesson.objects.prefetch_related(
                Prefetch(
                    'lesson_videos',  # Correct related_name for lesson videos
                    queryset=Video.objects.order_by('order')
                )
            ).order_by('order')
        )
    ).order_by('order')

    # Fetch comments for the course
    comments = Comment.objects.filter(course=course).select_related('user__userprofile').order_by('-posted_at')

    # Initialize variables for video handling
    current_video_embed_url = None
    selected_video_id = request.GET.get('video_id')
    current_video = None

    if selected_video_id:
        current_video = Video.objects.filter(id=selected_video_id, lesson__module__course=course).first()
        if current_video:
            current_video_embed_url = current_video.get_video_src

    # Handle comment form submission
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.course = course
            comment.user = request.user
            comment.save()
            return redirect(reverse('explore_course', args=[course_id]))
    else:
        comment_form = CommentForm()

    # Context to pass to the template
    context = {
        'course': course,
        'modules': modules,
        'comments': comments,
        'current_video': current_video,
        'current_video_embed_url': current_video_embed_url,
        'user_has_access': is_enrolled,
        'comment_form': comment_form,
    }

    return render(request, 'studentpanel/explore_courses.html', context)





@login_required(login_url='/404/')
@require_POST
def add_review(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if not Enrollment.objects.filter(user=request.user, course=course).exists():
        messages.error(request, "You are not enrolled in this course.")
        return redirect('student_home')
    
    form = ReviewForm(request.POST)
    if form.is_valid():
        review = form.save(commit=False)
        review.course = course
        review.user = request.user
        review.save()
        messages.success(request, 'Your review has been submitted successfully!')
        
        # Handle AJAX request
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': review.comment,
                'username': review.user.get_full_name(),
                'rating': review.rating,
                'posted_at': review.created_at.strftime('%B %d, %Y, %I:%M %p'),
            })
        
        return redirect('my_courses', course_id=course.id)
    else:
        messages.error(request, 'Failed to submit review. Please ensure all fields are correct.')
        # Optionally, you can redirect back with form errors
        return redirect('my_courses', course_id=course.id)

# Updated `serve_video` view
@login_required(login_url='/404/')
def serve_video(request, video_id):
    video = get_object_or_404(Video, id=video_id)
    course = video.lesson.module.course
    if Enrollment.objects.filter(user=request.user, course=course).exists():
        if video.video_file:
            return JsonResponse({'video_url': os.path.join(settings.MEDIA_URL, video.video_file.name), 'video_type': 'local'})
        elif video.video_url:
            return JsonResponse({'video_url': video.get_video_src, 'video_type': 'youtube'})
        return JsonResponse({'error': 'Video not available.'}, status=404)
    return HttpResponseForbidden("You are not enrolled in this course.")

# Helper function for embedding YouTube URL
def get_youtube_embed_url(url):
    if 'youtu.be' in url:
        video_id = url.split('/')[-1]
    elif 'youtube.com' in url:
        video_id = urlparse(url).query.get('v')
    return f'https://www.youtube.com/embed/{video_id[0]}' if video_id else url

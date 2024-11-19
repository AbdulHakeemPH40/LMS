from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from urllib.parse import urlparse, parse_qs
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError


class CourseCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Course(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    DURATION_CHOICES = [
        ('month', 'Month(s)'),
        ('week', 'Week(s)'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()

    # Update the ForeignKey to connect to UserProfile if mentors are represented by UserProfiles
    mentor = models.ForeignKey(
        'UserProfile',  # Points to UserProfile
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={'role': 'mentor'},
        related_name='mentor_courses'
    )

    category = models.ForeignKey(CourseCategory, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)  # Allow null for existing rows
    thumbnail = models.ImageField(
        upload_to='course_thumbnails/',
        null=True,
        blank=True,
        default='course_thumbnails/default_thumbnail.jpg'
    )
    price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    curriculum = models.FileField(
        upload_to='course_curriculums/',
        null=True,
        blank=True,
        help_text="Upload a PDF file for the course curriculum."
    )

    # New fields for course duration
    duration_type = models.CharField(
        max_length=5,
        choices=DURATION_CHOICES,
        default='month',
        help_text="Select the type of duration (Month or Week)"
    )
    duration_value = models.PositiveIntegerField(
        default=1,
        help_text="Enter the number of months or weeks for the course duration"
    )

    def __str__(self):
        return self.title


class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # Made nullable
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    active = models.BooleanField(default=True)
    usage_limit = models.PositiveIntegerField(null=True, blank=True, help_text="Total number of times this coupon can be used.")
    times_used = models.PositiveIntegerField(default=0)
    
    def is_valid(self):
        now = timezone.now()
        return self.active and self.valid_from <= now <= self.valid_to and \
               (self.usage_limit is None or self.times_used < self.usage_limit)
    
    def increment_usage(self):
        if self.usage_limit is not None:
            self.times_used += 1
            if self.times_used >= self.usage_limit:
                self.active = False
            self.save()


class Enrollment(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey('Course', on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    coupon = models.ForeignKey(
        'Coupon', on_delete=models.SET_NULL, null=True, blank=True,
        help_text="Coupon used for enrollment"
    )
    valid_to = models.DateTimeField(null=True, blank=True)
    progress = models.IntegerField(default=0)  # Represents percentage (0-100)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')

    def __str__(self):
        return f'{self.user.username} enrolled in {self.course.title}'



class Module(models.Model):
    LEVEL_CHOICES = [('basic', 'Basic'), ('intermediate', 'Intermediate'), ('advanced', 'Advanced')]
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    order = models.PositiveIntegerField()
    level = models.CharField(max_length=15, choices=LEVEL_CHOICES, default='basic')

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Lesson(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    order = models.PositiveIntegerField()
    subtitle = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.title

class Video(models.Model):
    VIDEO_TYPE_CHOICES = [
        ('local', 'Local'),
        ('youtube', 'YouTube')
    ]
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='lesson_videos')  # Using 'lesson_videos' as related_name
    title = models.CharField(max_length=255)
    video_type = models.CharField(max_length=10, choices=VIDEO_TYPE_CHOICES, default='local')
    video_file = models.FileField(upload_to='lessons/videos/', null=True, blank=True)
    video_url = models.URLField(max_length=200, null=True, blank=True)
    order = models.PositiveIntegerField()
    is_locked = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def clean(self):
        # Ensure only one of `video_file` or `video_url` is provided based on `video_type`
        if self.video_type == 'local' and not self.video_file:
            raise ValidationError("Please upload a video file for local videos.")
        elif self.video_type == 'youtube' and not self.video_url:
            raise ValidationError("Please provide a YouTube URL for YouTube videos.")

    @property
    def get_video_src(self):
        # Returns the appropriate video source URL
        if self.video_type == 'local' and self.video_file:
            return self.video_file.url
        elif self.video_type == 'youtube' and self.video_url:
            return self.convert_youtube_url_to_embed(self.video_url)
        return ''

    def convert_youtube_url_to_embed(self, url):
        """
        Converts a YouTube URL to an embed URL for iframe embedding.
        """
        video_id = None
        if 'youtu.be' in url:
            video_id = url.split('/')[-1]
        elif 'youtube.com' in url:
            parsed_url = urlparse(url)
            query = parse_qs(parsed_url.query)
            video_id = query.get('v', [None])[0]
        return f'https://www.youtube.com/embed/{video_id}' if video_id else ''


class UserProfile(models.Model):
    USER_ROLES = (
        ('student', 'Student'),
        ('admin', 'Admin/Instructor'),
        ('mentor', 'Mentor'),
    )
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('pending', 'Pending Approval'),
    )
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    role = models.CharField(max_length=10, choices=USER_ROLES, default='student')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    profile_image = models.ImageField(upload_to='profile/', blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        blank=True,
        null=True
    )
    date_of_birth = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.user.username

    def is_student(self):
        return self.role == 'student'

    def is_mentor(self):
        return self.role == 'mentor'

    def is_admin(self):
        return self.role == 'admin'

    def get_full_name(self):
        return f"{self.user.first_name} {self.user.last_name}"

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        instance.userprofile.save()

class MentorProfile(models.Model):
    # Fields for mentor details
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="mentor_profile")
    skills = models.TextField(blank=True, null=True, help_text="List of skills, separated by commas.")
    experience = models.TextField(blank=True, null=True, help_text="Details about the mentor's experience.")
    awards_and_recognitions = models.TextField(blank=True, null=True, help_text="Awards and recognitions received by the mentor.")
    bio = models.TextField(blank=True, null=True, help_text="Short bio of the mentor.")
    profile_image = models.ImageField(upload_to='mentor_images/', blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - Mentor Profile"
    
    @property
    def split_skills(self):
        return self.skills.split(',') if self.skills else []

    @property
    def split_awards(self):
        return self.awards_and_recognitions.split(',') if self.awards_and_recognitions else []





class Review(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.course.title}'


class Comment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    message = models.TextField()
    posted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user} on {self.course}"


class ActivityLog(models.Model):
    ACTION_TYPES = (
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('enrollment', 'Enrollment'),
        ('submission', 'Submission'),
        ('comment', 'Comment'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.action_type} by {self.user.username} at {self.timestamp}'


class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=150)
    message = models.TextField()
    submitted_at = models.DateTimeField(default=timezone.now)
    mobile = models.CharField(max_length=15, blank=True, null=True) 

    def __str__(self):
        return f"Message from {self.name} - {self.subject}"


class Promotion(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    button_text = models.CharField(max_length=50)
    link_url = models.URLField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE, default=1)  # Default course ID (e.g., 1)
    is_active = models.BooleanField(default=True)  # Add the is_active field

    def __str__(self):
        return self.title




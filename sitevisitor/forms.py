from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from .models import (
    CourseCategory, Course, Coupon, Enrollment, Module, Lesson,
    ActivityLog, Contact, Promotion, Video, UserProfile,MentorProfile,Comment,Review
)

class UserRegistrationForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=30, required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        max_length=30, required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'})
    )
    mobile = forms.CharField(
        max_length=10, required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mobile Number'})
    )

    class Meta:
        model = User
        fields = [
            'username', 'first_name', 'last_name', 'email',
            'password1', 'password2', 'mobile'
        ]

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already in use.')
        return email

    def clean_mobile(self):
        mobile = self.cleaned_data.get('mobile')
        if not mobile.isdigit():
            raise forms.ValidationError('Mobile number must contain only digits.')
        if len(mobile) != 10:
            raise forms.ValidationError('Mobile number must be exactly 10 digits.')
        return mobile

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            user_profile = user.userprofile
            user_profile.phone = self.cleaned_data['mobile']
            user_profile.save()
        return user


class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your first name'})
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your last name'})
    )
    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )

    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name', 'profile_image', 'phone', 'gender', 'date_of_birth']
        widgets = {
            'profile_image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your phone number'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),  # For date input widget
        }
        labels = {
            'profile_image': 'Profile Image',
            'phone': 'Mobile Number',
            'gender': 'Gender',
            'date_of_birth': 'Date of Birth',  # Label for the date of birth field
        }

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['date_of_birth'].initial = self.instance.date_of_birth  # Pre-populate date_of_birth if exists

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and not phone.isdigit():
            raise ValidationError("Phone number must contain only digits.")
        if phone and len(phone) != 10:
            raise ValidationError("Phone number must be exactly 10 digits.")
        return phone

    def save(self, commit=True):
        profile = super(UserProfileForm, self).save(commit=False)
        user = profile.user
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            profile.save()
        return profile


class MentorProfileForm(forms.ModelForm):
    user = forms.ModelChoiceField(
        queryset=User.objects.filter(userprofile__role='mentor'),  # Only mentors
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Select Mentor User"
    )
    skills = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter skills separated by commas'}),
        help_text="Enter skills separated by commas, e.g., Python, Data Science, Machine Learning"
    )
    awards_and_recognitions = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter awards separated by commas'}),
        help_text="Enter awards and recognitions separated by commas, e.g., Best Educator 2020, Mentor of the Year"
    )

    class Meta:
        model = MentorProfile
        fields = ['user', 'skills', 'experience', 'awards_and_recognitions', 'bio', 'profile_image']
        widgets = {
            'experience': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Experience details'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Short bio'}),
            'profile_image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }



class CourseForm(forms.ModelForm):
    thumbnail = forms.ImageField(
        required=True,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
    )
    curriculum = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        help_text="Upload a PDF for the course curriculum"
    )
    price = forms.DecimalField(
        required=False,
        max_digits=8,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = Course
        fields = [
            'title', 'description', 'mentor', 'category', 'status', 'thumbnail',
            'curriculum', 'price', 'duration_type', 'duration_value'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'mentor': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'duration_type': forms.Select(attrs={'class': 'form-control'}),
            'duration_value': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter number'}),
        }

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is not None and price <= 0:
            raise forms.ValidationError("Price must be a positive number.")
        return price

    def clean_curriculum(self):
        curriculum = self.cleaned_data.get('curriculum')
        if curriculum and not curriculum.name.endswith('.pdf'):
            raise forms.ValidationError("Only PDF files are allowed for the curriculum.")
        return curriculum


class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ['code', 'course', 'valid_from', 'valid_to', 'active']  # Removed 'usage_limit'
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Coupon Code', 'readonly': 'readonly'}),
            'course': forms.Select(attrs={'class': 'form-select'}),
            'active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'code': 'Coupon Code',
            'course': 'Course',
            'valid_to': 'Expiration Date',
            'active': 'Active',
        }


# Enrollment Form
class EnrollmentForm(forms.ModelForm):
    coupon_code = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Coupon Code'}),
        label='Coupon Code'
    )

    class Meta:
        model = Enrollment
        fields = ['coupon_code']

    def clean_coupon_code(self):
        code = self.cleaned_data.get('coupon_code')
        if code:
            try:
                coupon = Coupon.objects.get(code=code)
                if not coupon.is_valid():
                    raise ValidationError("This coupon is not valid.")
            except Coupon.DoesNotExist:
                raise ValidationError("Invalid coupon code.")
        return code

    def save(self, commit=True):
        enrollment = super().save(commit=False)
        code = self.cleaned_data.get('coupon_code')
        if code:
            coupon = Coupon.objects.get(code=code)
            enrollment.coupon = coupon
            coupon.increment_usage()
        if commit:
            enrollment.save()
        return enrollment


# Separate form for module management
class ModuleForm(forms.ModelForm):
    class Meta:
        model = Module
        fields = ['title', 'description', 'order']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }


# Lesson Form
class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['title', 'subtitle', 'order']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'subtitle': forms.TextInput(attrs={'class': 'form-control'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class VideoForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ['title', 'video_type', 'video_file', 'video_url', 'order', 'is_locked']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Video Title'}),
            'video_type': forms.Select(attrs={'class': 'form-control'}),
            'video_file': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'video_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'YouTube URL'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_locked': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        video_type = cleaned_data.get('video_type')
        video_file = cleaned_data.get('video_file')
        video_url = cleaned_data.get('video_url')

        if video_type == 'local' and not video_file:
            raise ValidationError("Please upload a video file for local videos.")
        elif video_type == 'youtube' and not video_url:
            raise ValidationError("Please provide a YouTube URL for YouTube videos.")
        return cleaned_data



# Course Category Form
class CourseCategoryForm(forms.ModelForm):
    class Meta:
        model = CourseCategory
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter category name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter a description for the category', 'rows': 4}),
        }
class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'email', 'subject', 'mobile', 'message']  # Add 'mobile' field here
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subject'}),
            'mobile': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mobile Number'}),  # Mobile input added
            'message': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Your Message', 'rows': 5}),
        }


class PromotionForm(forms.ModelForm):
    class Meta:
        model = Promotion
        fields = ['title', 'description', 'button_text', 'course', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Promotion Title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Promotion Description'}),
            'button_text': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Button Text'}),
            'course': forms.Select(attrs={'class': 'form-control'}),  # Dropdown for course selection
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),  # Add is_active field
            
        }


# Activity Log Form (Optional)
class ActivityLogForm(forms.ModelForm):
    class Meta:
        model = ActivityLog
        fields = ['user', 'action_type', 'description']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control'}),
            'action_type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


# Login Form
class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))


# Reset Password Form
class ResetPasswordForm(forms.Form):
    old_password = forms.CharField(
        label="Old Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter your old password'}),
        required=True
    )
    new_password = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter your new password'}),
        required=True
    )
    confirm_password = forms.CharField(
        label="Confirm New Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm your new password'}),
        required=True
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(ResetPasswordForm, self).__init__(*args, **kwargs)

    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password')
        if not self.user.check_password(old_password):
            raise ValidationError("Old password is incorrect.")
        return old_password

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if new_password and confirm_password and new_password != confirm_password:
            raise forms.ValidationError("New passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        new_password = self.cleaned_data['new_password']
        self.user.set_password(new_password)
        if commit:
            self.user.save()
        return self.user

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Type your comment here...',
                'rows': 3,
                'style': 'resize: none; border-radius: 8px; padding: 10px; font-size: 14px;',
            }),
        }
        labels = {
            'message': 'Comment',
        }

class ReviewForm(forms.ModelForm):
    rating = forms.IntegerField(
        widget=forms.HiddenInput(),
        required=True,
    )
    comment = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Write your review here', 'rows': 4}),
        label='Comment'
    )

    class Meta:
        model = Review
        fields = ['rating', 'comment']

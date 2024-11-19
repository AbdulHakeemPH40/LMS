from django import forms
from sitevisitor.models import UserProfile
from django.contrib.auth.models import User

class UserProfileForm(forms.ModelForm):
    # Adding first_name and last_name fields manually
    first_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}))

    class Meta:
        model = UserProfile
        fields = ['profile_image', 'phone', 'gender', 'date_of_birth', 'first_name', 'last_name']  # Include first_name and last_name in the fields
        widgets = {
            'profile_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),  # Date input widget
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Automatically populate first_name and last_name from the related User model if they exist
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name

    def save(self, commit=True):
        user_profile = super().save(commit=False)
        # Ensure that first_name and last_name are also updated in the User model
        if self.cleaned_data['first_name'] != self.instance.user.first_name:
            self.instance.user.first_name = self.cleaned_data['first_name']
        if self.cleaned_data['last_name'] != self.instance.user.last_name:
            self.instance.user.last_name = self.cleaned_data['last_name']
        
        if commit:
            # Save the user instance as well as the user profile
            self.instance.user.save()
            user_profile.save()
        return user_profile

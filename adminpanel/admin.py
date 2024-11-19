from django.contrib import admin
from django.utils.html import format_html
from sitevisitor.models import MentorProfile

class MentorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'skills', 'experience', 'awards_and_recognitions', 'display_profile_image')
    search_fields = ('user__username', 'skills', 'experience')
    list_filter = ('user__is_active',)

    def display_profile_image(self, obj):
        if obj.profile_image:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 5px;" />', obj.profile_image.url)
        return "No Image"
    display_profile_image.short_description = 'Profile Image'

# Register the MentorProfile model with the custom admin class
admin.site.register(MentorProfile, MentorProfileAdmin)

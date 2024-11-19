from django.contrib import admin
from .models import (
    CourseCategory, Course, Coupon, Enrollment, Module, Lesson,
    Video, UserProfile, Review, Comment, ActivityLog,
    Contact, Promotion
)

# Register models
admin.site.register(CourseCategory)
admin.site.register(Course)
admin.site.register(Coupon)
admin.site.register(Enrollment)
admin.site.register(Module)
admin.site.register(Lesson)
admin.site.register(Video)
admin.site.register(UserProfile)
admin.site.register(Review)
admin.site.register(Comment)
admin.site.register(ActivityLog)
admin.site.register(Contact)
admin.site.register(Promotion)


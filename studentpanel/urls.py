from django.urls import path
from .views import (
    student_home, my_courses, checkout, view_profile, reset_password,
    sign_out, edit_profile, explore_course, add_comment, edit_comment,
    delete_comment, serve_video, add_review  # Import add_review
)

urlpatterns = [
    path('', student_home, name='student_home'),
    path('my_courses/<int:course_id>/', my_courses, name='my_courses'),
    path('my_courses/', my_courses, name='my_courses'),
    path('checkout/<int:course_id>/', checkout, name='checkout'),
    path('profile/', view_profile, name='view_profile'),
    path('edit_profile/<int:user_id>/', edit_profile, name='edit_profile'),
    path('reset_password/', reset_password, name='reset_password'),
    path('sign_out/', sign_out, name='sign_out'),
    path('course/<int:course_id>/', explore_course, name='course_detail'),
    path('course/<int:course_id>/add_comment/', add_comment, name='add_comment'),
    path('course/<int:course_id>/add_review/', add_review, name='add_review'),  # New URL for reviews
    path('comment/<int:comment_id>/edit/', edit_comment, name='edit_comment'),
    path('comment/<int:comment_id>/delete/', delete_comment, name='delete_comment'),
    path('video/<int:video_id>/serve/', serve_video, name='serve_video'),
    path('explore_course/<int:course_id>/', explore_course, name='explore_course'),
     path('my_courses/<int:course_id>/', my_courses, name='my_courses'),

]

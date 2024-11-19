from django.urls import path
from . import views

urlpatterns = [
    # Admin Dashboard
    path('', views.admin_home, name='admin_home'),

    # Course Management
    path('courses/manage/', views.manage_courses, name='manage_courses'),
    path('courses/create/', views.create_course, name='create_course'),
    path('courses/<int:course_id>/view/', views.admin_view_course, name='admin_view_course'),
    path('courses/<int:course_id>/edit/', views.edit_course, name='edit_course'),
    path('courses/<int:course_id>/delete/', views.delete_course, name='delete_course'),

    # Module Management within a Course
    path('courses/<int:course_id>/modules/', views.manage_modules, name='manage_modules'),
    path('courses/<int:course_id>/modules/add/', views.add_module, name='add_module'),
    path('modules/<int:module_id>/edit/', views.edit_module, name='edit_module'),
    path('modules/<int:module_id>/delete/', views.delete_module, name='delete_module'),

    # Lesson Management within a Module
    path('modules/<int:module_id>/lessons/add/', views.add_lesson, name='add_lesson'),
    path('lessons/manage/', views.manage_lessons, name='manage_lessons'),
    path('lessons/<int:lesson_id>/edit/', views.edit_lesson, name='edit_lesson'),
    path('lessons/<int:lesson_id>/delete/', views.delete_lesson, name='delete_lesson'),

    # Video Management within a Lesson
    path('videos/manage/', views.manage_videos, name='manage_videos'),
    path('videos/manage/<int:course_id>/', views.manage_videos, name='manage_videos_course'),
    path('videos/<int:lesson_id>/add/', views.add_video, name='add_video'),
    path('videos/<int:video_id>/edit/', views.edit_video, name='edit_video'),
    path('videos/<int:video_id>/delete/', views.delete_video, name='delete_video'),

    # Coupon Management
    path('coupon/generate/<int:user_id>/', views.generate_coupon, name='generate_coupon'),
    path('coupon/<int:coupon_id>/delete/', views.delete_coupon, name='delete_coupon'),

    # User Management
    path('users/manage/', views.manage_users, name='manage_users'),
    path('users/<int:user_id>/view/', views.view_user, name='view_user'),
    path('users/<int:user_id>/activate/', views.activate_user, name='activate_user'),
    path('users/<int:user_id>/deactivate/', views.deactivate_user, name='deactivate_user'),

    # Category Management
    path('categories/manage/', views.category_list, name='category_list'),
    path('categories/create/', views.create_category, name='create_category'),
    path('categories/<int:category_id>/edit/', views.edit_category, name='edit_category'),
    path('categories/<int:category_id>/delete/', views.delete_category, name='delete_category'),

    # Mentors Management
    path('mentors/manage/', views.mentors_list, name='manage_mentors'),
    path('mentors/add/', views.add_mentor, name='add_mentor'),
    path('mentors/<int:mentor_id>/view/', views.view_mentor, name='view_mentor'),
    path('mentors/<int:mentor_id>/edit/', views.edit_mentor, name='edit_mentor'),
    path('mentors/<int:mentor_id>/delete/', views.delete_mentor, name='delete_mentor'),

    path('contact-form-submissions/', views.manage_contact_submissions, name='manage_contact_submissions'),
    path('view-contact/<int:contact_id>/', views.view_contact, name='view_contact'),

    path('manage_promotions/', views.manage_promotions, name='manage_promotions'),
    path('create_promotion/', views.create_promotion, name='create_promotion'),
    path('edit_promotion/<int:promotion_id>/', views.edit_promotion, name='edit_promotion'),
    
    path('toggle_promotion_status/<int:promotion_id>/', views.toggle_promotion_status, name='toggle_promotion_status'),

    path('admin/profile/', views.admin_profile, name='admin_profile'),
    path('change_password/', views.admin_change_password, name='admin_change_password'),
    path('logout/', views.logout_view, name='logout'),
]

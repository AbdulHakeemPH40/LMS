from django.urls import path
from .views import landing,mentors,course_overview,contact,sign_up,sign_in,error_page


urlpatterns = [
    path('',landing,name='landing'),
    path('mentors/',mentors,name='mentors'),
    path('courses/',course_overview,name='courses'),
    path('contact/',contact,name='contact'),
    path('signup/',sign_up,name='sign_up'),
    path('signin/', sign_in, name='sign_in'),
    path('404/', error_page, name='error_page'),
]
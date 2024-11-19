# studentpanel/middleware.py
from django.utils.deprecation import MiddlewareMixin
from .models import UserProfile

class EnsureUserProfileMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            UserProfile.objects.get_or_create(user=request.user)


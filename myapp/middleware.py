from django.conf import settings
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.urls import reverse


class BannedUserMiddleware:
    """Middleware that logs out and redirects banned users to a 'banned' page.

    It ignores static/media/admin and the banned page itself to avoid redirect loops.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Allow unauthenticated users
        if not request.user.is_authenticated:
            return self.get_response(request)

        path = request.path

        # Safe paths to ignore
        static_url = getattr(settings, 'STATIC_URL', '/static/')
        ignore_prefixes = [static_url, '/media/', '/admin/']

        try:
            banned_path = reverse('banned')
        except Exception:
            banned_path = '/banned/'

        ignore_prefixes.append(banned_path)

        if any(path.startswith(p) for p in ignore_prefixes):
            return self.get_response(request)

        # Check profile ban flag
        try:
            profile = request.user.profile
        except Exception:
            profile = None

        if profile and getattr(profile, 'is_banned', False):
            # Logout user and redirect to banned page
            logout(request)
            return redirect('banned')

        return self.get_response(request)

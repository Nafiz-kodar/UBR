from functools import wraps
from django.http import HttpResponseForbidden

from .models import Profile


def role_required(role):
    """Decorator to require a specific Profile.user_type for a view.

    Returns HTTP 403 when the logged-in user does not have the required role.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            # Try attribute access first (Django OneToOne creates `user.profile`),
            # otherwise fetch to be robust.
            profile = getattr(request.user, 'profile', None)
            if profile is None:
                try:
                    profile = Profile.objects.get(user=request.user)
                except Exception:
                    profile = None

            if profile and profile.user_type == role:
                return view_func(request, *args, **kwargs)
            return HttpResponseForbidden('Forbidden: insufficient permissions')

        return _wrapped

    return decorator

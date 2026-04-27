from functools import wraps
from ninja.errors import HttpError
from django.contrib.auth.models import Group

def role_required(allowed_roles):
    """
    Decorator untuk membatasi akses berdasarkan Group (Role) user.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                raise HttpError(401, "Unauthorized")
                
            if request.user.is_superuser:
                return func(request, *args, **kwargs)
                
            user_groups = request.user.groups.values_list('name', flat=True)
            has_role = any(role in user_groups for role in allowed_roles)
            
            if not has_role:
                raise HttpError(403, "Forbidden: Anda tidak memiliki akses ke endpoint ini")
                
            return func(request, *args, **kwargs)
        return wrapper
    return decorator

def assign_role(user, role_name):
    """Assign role (Group) ke user."""
    group, created = Group.objects.get_or_create(name=role_name)
    user.groups.add(group)

# core/helpers.py
from ninja.errors import HttpError


def get_object_or_404(model, **kwargs):
    """
    Mengambil satu object dari database.
    Raise HttpError 404 jika tidak ditemukan.

    Penggunaan:
        course = get_object_or_404(Course, pk=id)
        content = get_object_or_404(CourseContent, pk=id)
    """
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        model_name = model.__name__
        raise HttpError(404, f"{model_name} tidak ditemukan")


from django.contrib.auth.models import User

def get_authenticated_user(request):
    """Mendapatkan objek User dari request yang terautentikasi."""
    return User.objects.get(pk=request.user.id)

def check_course_owner(course, user):
    """Memeriksa apakah user adalah pemilik course."""
    if course.teacher != user:
        raise HttpError(403, "Hanya pemilik course yang dapat melakukan aksi ini")

def check_owner_or_superadmin(obj_owner, user):
    """Memeriksa apakah user adalah pemilik objek atau superadmin."""
    if obj_owner != user and not user.is_superuser:
        raise HttpError(403, "Anda tidak memiliki izin untuk melakukan aksi ini")

def check_enrollment(user, course):
    """Memeriksa apakah user terdaftar di course tertentu."""
    from core.models import CourseMember
    if not CourseMember.objects.filter(user_id=user, course_id=course).exists():
        raise HttpError(403, "Anda tidak terdaftar di course ini")

from functools import wraps

def is_admin(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_superuser:
            raise HttpError(403, "Akses ditolak: Membutuhkan role Admin")
        return func(request, *args, **kwargs)
    return wrapper

def is_instructor(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or (not request.user.is_staff and not request.user.is_superuser):
            raise HttpError(403, "Akses ditolak: Membutuhkan role Instructor")
        return func(request, *args, **kwargs)
    return wrapper

def is_student(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise HttpError(403, "Akses ditolak: Membutuhkan role Student (terotentikasi)")
        return func(request, *args, **kwargs)
    return wrapper

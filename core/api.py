from ninja import NinjaAPI, Query, Router
from ninja_simple_jwt.auth.ninja_auth import HttpJwtAuth
from django.contrib.auth.models import User
from ninja.errors import HttpError
from typing import List

from core.models import Course, CourseContent, CourseMember, Comment, CourseProgress
from core.schemas import (
    Register, UserOut, CourseIn, CourseOut, DetailCourseOut, CourseFilterSchema,
    CourseContentIn, CourseContentOut, CourseMemberOut, CommentIn, CommentUpdate,
    ProfileUpdate, ProgressIn, ProgressOut
)
from core.helpers import (
    get_authenticated_user, check_course_owner, 
    check_owner_or_superadmin, check_enrollment,
    is_admin, is_instructor, is_student
)
from ninja_simple_jwt.auth.views.schemas import SignInRequest, MobileSignInResponse, MobileTokenRefreshRequest, MobileTokenRefreshResponse
from ninja_simple_jwt.auth.views.api import mobile_sign_in, mobile_token_refresh

api = NinjaAPI(title="Simple LMS API", version="1.0.0")

# Inisialisasi JWT auth handler
apiAuth = HttpJwtAuth()

auth_router = Router(tags=["Authentication"])
courses_router = Router(tags=["Courses"])
enrollments_router = Router(tags=["Enrollments"])
comments_router = Router(tags=["Comments"])

# ==================== User & Auth Endpoints ====================

@auth_router.post('/register', response={201: UserOut})
def register(request, data: Register):
    if User.objects.filter(username=data.username).exists():
        raise HttpError(400, "Username sudah digunakan")

    if User.objects.filter(email=data.email).exists():
        raise HttpError(400, "Email sudah digunakan")

    newUser = User.objects.create_user(
        username=data.username,
        password=data.password,
        email=data.email,
        first_name=data.first_name,
        last_name=data.last_name
    )
    return 201, newUser

@auth_router.post("/login", response=MobileSignInResponse)
def login(request, payload: SignInRequest):
    return mobile_sign_in(request, payload)

@auth_router.post("/refresh", response=MobileTokenRefreshResponse)
def refresh(request, payload: MobileTokenRefreshRequest):
    return mobile_token_refresh(request, payload)

@auth_router.get('/me', auth=apiAuth, response=UserOut)
@is_student
def get_profile(request):
    user = User.objects.get(pk=request.user.id)
    return user

@auth_router.put('/me', auth=apiAuth, response=UserOut)
@is_student
def update_profile(request, data: ProfileUpdate):
    user = User.objects.get(pk=request.user.id)
    if data.first_name is not None:
        user.first_name = data.first_name
    if data.last_name is not None:
        user.last_name = data.last_name
    if data.email is not None:
        user.email = data.email
    user.save()
    return user

# ==================== Courses Endpoints ====================

@courses_router.get('', response=List[CourseOut])
def list_courses(request, filters: CourseFilterSchema = Query(...)):
    courses = Course.objects.all().select_related('teacher')
    courses = filters.filter(courses)
    return courses

@courses_router.get('/{id}', response=DetailCourseOut)
def get_course(request, id: int):
    course = Course.objects.filter(id=id).first()
    if not course:
        raise HttpError(404, "Course tidak ditemukan")
    return course

@courses_router.post('', auth=apiAuth, response={201: CourseOut})
@is_instructor
def createCourse(request, data: CourseIn):
    user = User.objects.get(pk=request.user.id)
    course = Course.objects.create(
        name=data.name,
        description=data.description,
        price=data.price,
        teacher=user
    )
    return 201, course

@courses_router.patch('/{id}', auth=apiAuth, response=CourseOut)
@is_instructor
def updateCourse(request, id: int, data: CourseIn):
    user = get_authenticated_user(request)

    course = Course.objects.filter(id=id).first()
    if course is None:
        raise HttpError(404, "Course tidak ditemukan")

    check_course_owner(course, user)

    course.name = data.name
    course.description = data.description
    course.price = data.price
    course.save()
    return course

@courses_router.delete('/{id}', auth=apiAuth)
@is_admin
def deleteCourse(request, id: int):
    user = get_authenticated_user(request)

    course = Course.objects.filter(id=id).first()
    if course is None:
        raise HttpError(404, "Course tidak ditemukan")

    # is_admin decorator will ensure only admin reaches here, but we also check_owner_or_superadmin
    check_owner_or_superadmin(course.teacher, user)

    course.delete()
    return {"message": "Course berhasil dihapus"}

# ==================== Enrollments ====================

@enrollments_router.post('', auth=apiAuth, response={201: CourseMemberOut})
@is_student
def courseEnrollment(request, course_id: int):
    user_id = User.objects.get(pk=request.user.id)
    course = Course.objects.filter(pk=course_id).first()
    
    if not course:
        raise HttpError(404, "Course tidak ditemukan")

    if CourseMember.objects.filter(user_id=user_id, course_id=course).exists():
        raise HttpError(400, "Anda sudah terdaftar di course ini")

    enrollment = CourseMember.objects.create(
        user_id=user_id,
        course_id=course,
        roles='std'
    )
    return 201, enrollment

@enrollments_router.get('/my-courses', auth=apiAuth, response=List[CourseMemberOut])
@is_student
def getMyCourses(request):
    user_id = User.objects.get(pk=request.user.id)
    mycourses = CourseMember.objects.filter(
        user_id=user_id
    ).select_related('course_id', 'user_id')
    return mycourses

@enrollments_router.post('/{id}/progress', auth=apiAuth, response={201: ProgressOut})
@is_student
def markLessonComplete(request, id: int, data: ProgressIn):
    user = get_authenticated_user(request)
    course = Course.objects.filter(id=id).first()
    
    if not course:
        raise HttpError(404, "Course tidak ditemukan")

    check_enrollment(user, course)

    content = CourseContent.objects.filter(id=data.content_id, course=course).first()
    if not content:
        raise HttpError(404, "Konten pelajaran tidak ditemukan dalam course ini")

    progress, created = CourseProgress.objects.get_or_create(
        user=user,
        content=content,
        defaults={'is_completed': data.is_completed}
    )
    
    if not created:
        progress.is_completed = data.is_completed
        progress.save()

    return 201, progress

# ==================== Comments Endpoints ====================

@comments_router.post('', auth=apiAuth)
@is_student
def postComment(request, data: CommentIn):
    user = get_authenticated_user(request)
    content = CourseContent.objects.filter(id=data.content_id).first()

    if content is None:
        raise HttpError(404, "Content tidak ditemukan")

    check_enrollment(user, content.course_id)

    Comment.objects.create(
        comment=data.comment,
        user_id=user,
        content_id=content
    )
    return {"message": "Komentar berhasil ditambahkan"}

@comments_router.put('/{id}', auth=apiAuth)
@is_student
def updateComment(request, id: int, data: CommentUpdate):
    user = get_authenticated_user(request)

    comment = Comment.objects.filter(id=id).first()
    if comment is None:
        raise HttpError(404, "Komentar tidak ditemukan")

    if comment.user_id != user:
        raise HttpError(403, "Anda tidak memiliki izin untuk mengedit komentar ini")

    comment.comment = data.comment
    comment.save()
    return {"message": "Komentar berhasil diperbarui"}

@comments_router.delete('/{id}', auth=apiAuth)
def deleteComment(request, id: int):
    user = get_authenticated_user(request)

    comment = Comment.objects.select_related('content_id__course_id').filter(id=id).first()
    if comment is None:
        raise HttpError(404, "Komentar tidak ditemukan")

    is_comment_owner = (comment.user_id == user)
    course = comment.content_id.course_id
    is_course_owner = (course.teacher == user)
    is_superadmin = user.is_superuser

    if is_comment_owner or is_course_owner or is_superadmin:
        comment.delete()
        return {"message": "Komentar berhasil dihapus"}
    else:
        raise HttpError(403, "Anda tidak memiliki izin untuk menghapus komentar ini")

# Register routers
api.add_router("/auth", auth_router)
api.add_router("/courses", courses_router)
api.add_router("/enrollments", enrollments_router)
api.add_router("/comments", comments_router)

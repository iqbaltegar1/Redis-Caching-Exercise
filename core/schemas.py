# core/schemas.py
from ninja import Schema, Field, FilterSchema
from datetime import datetime
from typing import Optional, List


# ==================== User Schemas ====================

class UserOut(Schema):
    """Schema untuk data User yang dikembalikan dalam response."""
    id: int
    username: str
    first_name: str
    last_name: str
    email: str

class Register(Schema):
    username: str
    password: str
    email: str
    first_name: str
    last_name: str

class ProfileUpdate(Schema):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None


# ==================== Course Schemas ====================

class CourseIn(Schema):
    """Schema untuk input saat membuat/mengupdate Course."""
    name: str
    description: str = '-'
    price: int = 10000


class CourseOut(Schema):
    """Schema untuk output data Course."""
    id: int
    name: str
    description: str
    price: int
    image: Optional[str] = ''
    teacher: UserOut
    created_at: datetime
    updated_at: datetime


class ContentTitleOut(Schema):
    """Schema untuk menampilkan judul konten saja."""
    id: int
    name: str


class DetailCourseOut(CourseOut):
    """Schema untuk detail Course beserta daftar konten."""
    contents: List[ContentTitleOut] = Field(
        ..., alias="coursecontent_set"
    )

class CourseFilterSchema(FilterSchema):
    search: Optional[str] = Field(None, q=['name__icontains', 'description__icontains'])
    min_price: Optional[int] = Field(None, q='price__gte')
    max_price: Optional[int] = Field(None, q='price__lte')


# ==================== CourseContent Schemas ====================

class CourseContentIn(Schema):
    """Schema untuk input saat membuat/mengupdate CourseContent."""
    name: str
    description: str = '-'
    video_url: Optional[str] = None
    course_id: int
    parent_id: Optional[int] = None


class CourseContentOut(Schema):
    """Schema untuk output data CourseContent."""
    id: int
    name: str
    description: str
    video_url: Optional[str] = None
    course_id: int
    parent_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime


class CourseMemberOut(Schema):
    id: int
    course_id: CourseOut
    roles: str
    created_at: datetime


class CommentIn(Schema):
    comment: str
    content_id: int


class CommentUpdate(Schema):
    comment: str

class ProgressIn(Schema):
    content_id: int
    is_completed: bool = True

class ProgressOut(Schema):
    id: int
    user_id: int
    content_id: int
    is_completed: bool
    completed_at: datetime

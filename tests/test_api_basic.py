"""
Basic Integration tests untuk Simple LMS API endpoints.

Mencakup:
- Course list dan detail
- Comment operations
- Basic data validation
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from core.models import Course, CourseMember, CourseContent, Comment
import json


class TestCourseAPIBasic(TestCase):
    """Basic tests untuk Course API."""

    def setUp(self):
        """Setup test data."""
        self.client = Client()
        self.teacher = User.objects.create_user(
            username='teacher1',
            password='pass123'
        )
        self.course = Course.objects.create(
            name='Django Testing Course',
            description='Belajar testing',
            price=200000,
            teacher=self.teacher
        )

    def test_list_courses_returns_200(self):
        """Test list courses endpoint returns 200."""
        response = self.client.get('/api/v1/courses')
        self.assertEqual(response.status_code, 200)

    def test_get_course_detail_returns_200(self):
        """Test get course detail returns 200."""
        response = self.client.get(f'/api/v1/courses/{self.course.id}')
        self.assertEqual(response.status_code, 200)

    def test_get_nonexistent_course_returns_404(self):
        """Test get nonexistent course returns 404."""
        response = self.client.get('/api/v1/courses/99999')
        self.assertEqual(response.status_code, 404)

    def test_course_content_relationship(self):
        """Test course dapat memiliki banyak content."""
        content1 = CourseContent.objects.create(
            course=self.course,
            name='Lesson 1'
        )
        content2 = CourseContent.objects.create(
            course=self.course,
            name='Lesson 2'
        )
        self.assertEqual(self.course.coursecontent_set.count(), 2)


class TestCommentAPIBasic(TestCase):
    """Basic tests untuk Comment API."""

    def setUp(self):
        """Setup test data."""
        self.client = Client()
        self.teacher = User.objects.create_user(
            username='teacher1',
            password='pass123'
        )
        self.student = User.objects.create_user(
            username='student1',
            password='pass123'
        )
        self.course = Course.objects.create(
            name='Test Course',
            teacher=self.teacher
        )
        self.student_member = CourseMember.objects.create(
            user_id=self.student,
            course_id=self.course,
            roles='std'
        )
        self.content = CourseContent.objects.create(
            course=self.course,
            name='Test Content'
        )

    def test_comments_can_be_created(self):
        """Test comments dapat dibuat."""
        comment = Comment.objects.create(
            user_id=self.student,
            content_id=self.content,
            comment='Test comment'
        )
        self.assertEqual(comment.comment, 'Test comment')

    def test_multiple_comments_on_content(self):
        """Test multiple comments pada content yang sama."""
        Comment.objects.create(
            user_id=self.student,
            content_id=self.content,
            comment='Comment 1'
        )
        Comment.objects.create(
            user_id=self.teacher,
            content_id=self.content,
            comment='Comment 2'
        )
        self.assertEqual(Comment.objects.filter(content_id=self.content).count(), 2)

    def test_comment_deletion(self):
        """Test comment dapat dihapus."""
        comment = Comment.objects.create(
            user_id=self.student,
            content_id=self.content,
            comment='Test'
        )
        comment_id = comment.id
        comment.delete()
        self.assertFalse(Comment.objects.filter(id=comment_id).exists())


class TestCourseMemberBasic(TestCase):
    """Basic tests untuk Course Member."""

    def setUp(self):
        """Setup test data."""
        self.teacher = User.objects.create_user(
            username='teacher1',
            password='pass123'
        )
        self.student = User.objects.create_user(
            username='student1',
            password='pass123'
        )
        self.course = Course.objects.create(
            name='Test Course',
            teacher=self.teacher
        )

    def test_student_can_join_course(self):
        """Test student dapat bergabung dengan course."""
        member = CourseMember.objects.create(
            user_id=self.student,
            course_id=self.course,
            roles='std'
        )
        self.assertEqual(member.roles, 'std')

    def test_multiple_students_can_join_same_course(self):
        """Test multiple students dapat bergabung dengan course yang sama."""
        student2 = User.objects.create_user(
            username='student2',
            password='pass123'
        )
        CourseMember.objects.create(
            user_id=self.student,
            course_id=self.course,
            roles='std'
        )
        CourseMember.objects.create(
            user_id=student2,
            course_id=self.course,
            roles='std'
        )
        self.assertEqual(self.course.coursemember_set.count(), 2)

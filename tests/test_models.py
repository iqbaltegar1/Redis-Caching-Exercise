"""
Unit tests untuk Django models di Simple LMS.

Mencakup:
- Course model
- CourseMember model
- CourseContent model
- Comment model
- CourseProgress model
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.db import IntegrityError
from core.models import Course, CourseMember, CourseContent, Comment, CourseProgress


class TestCourseModel(TestCase):
    """Test cases untuk model Course."""

    def setUp(self):
        """Setup data yang digunakan di setiap test."""
        self.teacher = User.objects.create_user(
            username='teacher1',
            password='testpass123',
            email='teacher1@example.com'
        )

    def test_create_course(self):
        """Test membuat course baru."""
        course = Course.objects.create(
            name="Django for Beginners",
            description="Belajar Django dari nol",
            price=100000,
            teacher=self.teacher
        )
        self.assertEqual(course.name, "Django for Beginners")
        self.assertEqual(course.price, 100000)
        self.assertEqual(course.teacher, self.teacher)

    def test_course_str(self):
        """Test representasi string course."""
        course = Course.objects.create(
            name="Python Basics",
            teacher=self.teacher
        )
        self.assertEqual(str(course), "Python Basics")

    def test_course_default_price(self):
        """Test default price adalah 10000."""
        course = Course.objects.create(
            name="Free Course",
            teacher=self.teacher
        )
        self.assertEqual(course.price, 10000)

    def test_course_ordering(self):
        """Test course diurutkan berdasarkan created_at descending."""
        course1 = Course.objects.create(
            name="Course 1",
            teacher=self.teacher
        )
        course2 = Course.objects.create(
            name="Course 2",
            teacher=self.teacher
        )
        courses = Course.objects.all()
        # Course terbaru harus muncul pertama
        self.assertEqual(courses[0], course2)
        self.assertEqual(courses[1], course1)

    def test_course_teacher_relationship(self):
        """Test relasi course dengan teacher."""
        Course.objects.create(
            name="Course A",
            teacher=self.teacher
        )
        Course.objects.create(
            name="Course B",
            teacher=self.teacher
        )
        self.assertEqual(self.teacher.courses.count(), 2)

    def test_course_cascade_delete(self):
        """Test course content dihapus ketika course dihapus."""
        course = Course.objects.create(
            name="Test Course",
            teacher=self.teacher
        )
        content = CourseContent.objects.create(
            name="Test Content",
            course=course
        )
        self.assertEqual(CourseContent.objects.count(), 1)
        course.delete()
        self.assertEqual(CourseContent.objects.count(), 0)


class TestCourseMemberModel(TestCase):
    """Test cases untuk model CourseMember."""

    def setUp(self):
        """Setup data yang digunakan di setiap test."""
        self.teacher = User.objects.create_user(
            username='teacher1',
            password='testpass123'
        )
        self.student = User.objects.create_user(
            username='student1',
            password='testpass123'
        )
        self.course = Course.objects.create(
            name="Django Course",
            price=150000,
            teacher=self.teacher
        )

    def test_create_course_member(self):
        """Test mendaftarkan member ke course."""
        member = CourseMember.objects.create(
            user_id=self.student,
            course_id=self.course,
            roles='std'
        )
        self.assertEqual(member.course_id, self.course)
        self.assertEqual(member.user_id, self.student)
        self.assertEqual(member.roles, 'std')

    def test_course_member_str(self):
        """Test representasi string course member."""
        member = CourseMember.objects.create(
            user_id=self.student,
            course_id=self.course,
            roles='std'
        )
        expected = f"{self.student.username} - {self.course.name}"
        self.assertEqual(str(member), expected)

    def test_default_role_is_student(self):
        """Test default role adalah 'std' (student)."""
        member = CourseMember.objects.create(
            user_id=self.student,
            course_id=self.course
        )
        self.assertEqual(member.roles, 'std')

    def test_cascade_delete_course(self):
        """Test member dihapus jika course dihapus."""
        CourseMember.objects.create(
            course_id=self.course,
            user_id=self.student,
            roles='std'
        )
        self.assertEqual(CourseMember.objects.count(), 1)
        self.course.delete()
        self.assertEqual(CourseMember.objects.count(), 0)

    def test_cascade_delete_user(self):
        """Test member dihapus jika user dihapus."""
        CourseMember.objects.create(
            course_id=self.course,
            user_id=self.student,
            roles='std'
        )
        self.assertEqual(CourseMember.objects.count(), 1)
        self.student.delete()
        self.assertEqual(CourseMember.objects.count(), 0)

    def test_member_with_teacher_role(self):
        """Test member dengan role teacher."""
        member = CourseMember.objects.create(
            user_id=self.teacher,
            course_id=self.course,
            roles='tea'
        )
        self.assertEqual(member.roles, 'tea')


class TestCourseContentModel(TestCase):
    """Test cases untuk model CourseContent."""

    def setUp(self):
        """Setup data yang digunakan di setiap test."""
        self.teacher = User.objects.create_user(
            username='teacher1',
            password='testpass123'
        )
        self.course = Course.objects.create(
            name="Django Course",
            teacher=self.teacher
        )

    def test_create_course_content(self):
        """Test membuat course content."""
        content = CourseContent.objects.create(
            name="Introduction to Django",
            description="Pengenalan framework Django",
            video_url="https://youtube.com/watch?v=example",
            course=self.course
        )
        self.assertEqual(content.name, "Introduction to Django")
        self.assertEqual(content.course, self.course)

    def test_course_content_str(self):
        """Test representasi string content."""
        content = CourseContent.objects.create(
            name="Lesson 1",
            course=self.course
        )
        expected = f"{self.course.name} - Lesson 1"
        self.assertEqual(str(content), expected)

    def test_content_ordering(self):
        """Test content diurutkan berdasarkan created_at ascending."""
        content1 = CourseContent.objects.create(
            name="Lesson 1",
            course=self.course
        )
        content2 = CourseContent.objects.create(
            name="Lesson 2",
            course=self.course
        )
        contents = CourseContent.objects.all()
        # Lesson 1 harus muncul pertama (ascending order)
        self.assertEqual(contents[0], content1)
        self.assertEqual(contents[1], content2)

    def test_nested_content_with_parent(self):
        """Test content dapat memiliki parent content (nested structure)."""
        parent = CourseContent.objects.create(
            name="Module 1",
            course=self.course
        )
        child = CourseContent.objects.create(
            name="Lesson 1.1",
            course=self.course,
            parent=parent
        )
        self.assertEqual(child.parent, parent)
        self.assertEqual(parent.children.count(), 1)

    def test_cascade_delete_with_parent(self):
        """Test child content jika parent dihapus."""
        parent = CourseContent.objects.create(
            name="Module 1",
            course=self.course
        )
        child = CourseContent.objects.create(
            name="Lesson 1.1",
            course=self.course,
            parent=parent
        )
        parent.delete()
        # Parent dihapus, child.parent menjadi NULL (SET_NULL)
        child.refresh_from_db()
        self.assertIsNone(child.parent)


class TestCommentModel(TestCase):
    """Test cases untuk model Comment."""

    def setUp(self):
        """Setup data yang digunakan di setiap test."""
        self.teacher = User.objects.create_user(
            username='teacher1',
            password='testpass123'
        )
        self.student = User.objects.create_user(
            username='student1',
            password='testpass123'
        )
        self.course = Course.objects.create(
            name="Django Course",
            teacher=self.teacher
        )
        self.content = CourseContent.objects.create(
            name="Lesson 1",
            course=self.course
        )

    def test_create_comment(self):
        """Test membuat komentar."""
        comment = Comment.objects.create(
            user_id=self.student,
            content_id=self.content,
            comment="Ini adalah komentar test"
        )
        self.assertEqual(comment.comment, "Ini adalah komentar test")
        self.assertEqual(comment.user_id, self.student)

    def test_comment_str(self):
        """Test representasi string comment."""
        comment = Comment.objects.create(
            user_id=self.student,
            content_id=self.content,
            comment="Test"
        )
        expected = f"{self.student.username} on {self.content.name}"
        self.assertEqual(str(comment), expected)

    def test_cascade_delete_content(self):
        """Test comment dihapus jika content dihapus."""
        Comment.objects.create(
            user_id=self.student,
            content_id=self.content,
            comment="Test comment"
        )
        self.assertEqual(Comment.objects.count(), 1)
        self.content.delete()
        self.assertEqual(Comment.objects.count(), 0)

    def test_cascade_delete_user(self):
        """Test comment dihapus jika user dihapus."""
        Comment.objects.create(
            user_id=self.student,
            content_id=self.content,
            comment="Test comment"
        )
        self.assertEqual(Comment.objects.count(), 1)
        self.student.delete()
        self.assertEqual(Comment.objects.count(), 0)

    def test_multiple_comments_on_same_content(self):
        """Test multiple comments dapat dibuat pada content yang sama."""
        comment1 = Comment.objects.create(
            user_id=self.student,
            content_id=self.content,
            comment="Komentar pertama"
        )
        comment2 = Comment.objects.create(
            user_id=self.teacher,
            content_id=self.content,
            comment="Komentar kedua"
        )
        self.assertEqual(Comment.objects.filter(content_id=self.content).count(), 2)


class TestCourseProgressModel(TestCase):
    """Test cases untuk model CourseProgress."""

    def setUp(self):
        """Setup data yang digunakan di setiap test."""
        self.teacher = User.objects.create_user(
            username='teacher1',
            password='testpass123'
        )
        self.student = User.objects.create_user(
            username='student1',
            password='testpass123'
        )
        self.course = Course.objects.create(
            name="Django Course",
            teacher=self.teacher
        )
        self.content = CourseContent.objects.create(
            name="Lesson 1",
            course=self.course
        )

    def test_create_progress(self):
        """Test membuat progress tracking."""
        progress = CourseProgress.objects.create(
            user=self.student,
            content=self.content,
            is_completed=False
        )
        self.assertEqual(progress.user, self.student)
        self.assertEqual(progress.content, self.content)
        self.assertFalse(progress.is_completed)

    def test_progress_str(self):
        """Test representasi string progress."""
        progress = CourseProgress.objects.create(
            user=self.student,
            content=self.content,
            is_completed=True
        )
        expected = f"{self.student.username} - {self.content.name} (Completed: True)"
        self.assertEqual(str(progress), expected)

    def test_unique_together_constraint(self):
        """Test user tidak bisa membuat progress untuk content yang sama dua kali."""
        CourseProgress.objects.create(
            user=self.student,
            content=self.content,
            is_completed=False
        )
        with self.assertRaises(IntegrityError):
            CourseProgress.objects.create(
                user=self.student,
                content=self.content,
                is_completed=True
            )

    def test_mark_content_as_completed(self):
        """Test menandai content sebagai completed."""
        progress = CourseProgress.objects.create(
            user=self.student,
            content=self.content,
            is_completed=False
        )
        progress.is_completed = True
        progress.save()
        progress.refresh_from_db()
        self.assertTrue(progress.is_completed)

    def test_cascade_delete_user(self):
        """Test progress dihapus jika user dihapus."""
        CourseProgress.objects.create(
            user=self.student,
            content=self.content
        )
        self.assertEqual(CourseProgress.objects.count(), 1)
        self.student.delete()
        self.assertEqual(CourseProgress.objects.count(), 0)

    def test_cascade_delete_content(self):
        """Test progress dihapus jika content dihapus."""
        CourseProgress.objects.create(
            user=self.student,
            content=self.content
        )
        self.assertEqual(CourseProgress.objects.count(), 1)
        self.content.delete()
        self.assertEqual(CourseProgress.objects.count(), 0)

    def test_user_can_have_multiple_progress_entries(self):
        """Test user dapat memiliki multiple progress entries untuk berbeda content."""
        content2 = CourseContent.objects.create(
            name="Lesson 2",
            course=self.course
        )
        progress1 = CourseProgress.objects.create(
            user=self.student,
            content=self.content
        )
        progress2 = CourseProgress.objects.create(
            user=self.student,
            content=content2
        )
        self.assertEqual(CourseProgress.objects.filter(user=self.student).count(), 2)

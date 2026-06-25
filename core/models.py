from django.db import models
from django.contrib.auth.models import User


class Course(models.Model):
    """Model untuk kursus/mata kuliah."""
    name = models.CharField(max_length=255)
    description = models.TextField(default='-')
    price = models.IntegerField(default=10000)
    image = models.ImageField(upload_to='courses/', blank=True, null=True)
    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='courses'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at', '-id']
        verbose_name = 'Course'
        verbose_name_plural = 'Courses'

    def __str__(self):
        return self.name


class CourseContent(models.Model):
    """Model untuk konten/materi dalam sebuah kursus."""
    name = models.CharField(max_length=255)
    description = models.TextField(default='-')
    video_url = models.URLField(blank=True, null=True)
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='coursecontent_set'
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Course Content'
        verbose_name_plural = 'Course Contents'

    def __str__(self):
        return f"{self.course.name} - {self.name}"


class CourseMember(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    course_id = models.ForeignKey(Course, on_delete=models.CASCADE)
    roles = models.CharField(max_length=10, default='std')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user_id.username} - {self.course_id.name}"


class Comment(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    content_id = models.ForeignKey(CourseContent, on_delete=models.CASCADE)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user_id.username} on {self.content_id.name}"


class CourseProgress(models.Model):
    """Model untuk melacak progress (lesson completion) user di suatu kursus."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progress')
    content = models.ForeignKey(CourseContent, on_delete=models.CASCADE, related_name='progress')
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'content')

    def __str__(self):
        return f"{self.user.username} - {self.content.name} (Completed: {self.is_completed})"

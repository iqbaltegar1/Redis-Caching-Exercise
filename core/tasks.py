from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Count
from datetime import datetime
from pymongo import MongoClient
from core.mongo import log_activity
from core.models import Course, CourseMember

client = MongoClient(settings.MONGO_URI)
db = client[settings.MONGO_DB_NAME]

@shared_task(bind=True)
def send_enrollment_email(self, user_email: str, course_name: str):
    subject = f"Enrollment berhasil: {course_name}"
    message = f"Anda telah berhasil mendaftar ke course {course_name}. Selamat belajar!"
    send_mail(subject, message, 'noreply@simplelms.local', [user_email], fail_silently=True)
    db.activity_logs.insert_one({
        'event': 'enrollment_email_sent',
        'user_email': user_email,
        'course_name': course_name,
        'timestamp': datetime.utcnow(),
    })
    return {'status': 'sent', 'email': user_email, 'course': course_name}

@shared_task(bind=True)
def generate_certificate(self, user_id: int, course_id: int):
    course = Course.objects.filter(id=course_id).first()
    if not course:
        return {'status': 'error', 'reason': 'course_not_found', 'course_id': course_id}
    report = {
        'event': 'certificate_generated',
        'user_id': user_id,
        'course_id': course_id,
        'course_name': course.name,
        'generated_at': datetime.utcnow(),
    }
    db.learning_analytics.insert_one(report)
    log_activity('certificate_generated', {'user_id': user_id, 'course_id': course_id, 'course_name': course.name})
    return {'status': 'generated', 'user_id': user_id, 'course_id': course_id}

@shared_task(bind=True)
def update_course_statistics(self):
    counts = CourseMember.objects.values('course_id').annotate(enroll_count=Count('id'))
    stats = [{
        'course_id': value['course_id'],
        'enroll_count': value['enroll_count'],
        'updated_at': datetime.utcnow(),
    } for value in counts]
    if stats:
        db.course_statistics.replace_one({'_id': 'latest'}, {'stats': stats, 'updated_at': datetime.utcnow()}, upsert=True)
        log_activity('course_statistics_updated', {'updated_count': len(stats)})
    return {'status': 'updated', 'count': len(stats)}

@shared_task(bind=True)
def export_course_report(self):
    courses = Course.objects.all().select_related('teacher')
    rows = []
    for course in courses:
        enroll_count = CourseMember.objects.filter(course_id=course).count()
        rows.append({
            'course_id': course.id,
            'course_name': course.name,
            'teacher': course.teacher.username,
            'enroll_count': enroll_count,
            'price': course.price,
        })
    db.activity_logs.insert_one({
        'event': 'course_report_exported',
        'row_count': len(rows),
        'exported_at': datetime.utcnow(),
    })
    return rows

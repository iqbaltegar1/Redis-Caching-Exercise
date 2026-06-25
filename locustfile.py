"""
Load testing untuk Simple LMS API menggunakan Locust.

Simulasi multiple users yang mengakses API secara concurrent.
Untuk menjalankan:
    locust -f locustfile.py --host=http://localhost:8000

Atau headless mode:
    locust -f locustfile.py --host=http://localhost:8000 --headless --users 20 --spawn-rate 2 --run-time 1m
"""

from locust import HttpUser, task, between
import json


class LMSUser(HttpUser):
    """Simulasi user yang mengakses Simple LMS API."""

    # Waktu tunggu antara setiap task (1-5 detik untuk simulasi real user)
    wait_time = between(1, 5)

    # Token autentikasi
    token = None
    user_id = None
    course_id = None

    def on_start(self):
        """Dijalankan saat user mulai - login untuk mendapatkan token."""
        try:
            # Gunakan user yang sudah ada di database
            response = self.client.post(
                "/api/v1/auth/login",
                json={
                    "username": "teacher1",
                    "password": "teacherpass123"
                },
                name="POST /api/v1/auth/login"
            )
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access") or data.get("token")
                print(f"Login success. Token: {self.token[:20]}...")
            else:
                print(f"Login failed: {response.status_code}")
        except Exception as e:
            print(f"Error during login: {e}")

    def get_headers(self):
        """Return headers dengan token autentikasi."""
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    @task(5)
    def list_courses(self):
        """
        Task: Mengambil daftar course (paling sering).
        Weight 5 = task ini 5x lebih sering dijalankan.
        """
        self.client.get(
            "/api/v1/courses",
            headers=self.get_headers(),
            name="GET /api/v1/courses"
        )

    @task(3)
    def get_course_detail(self):
        """
        Task: Mengambil detail course tertentu.
        Weight 3 = task ini 3x lebih sering dari default.
        """
        # Ambil course ID dari list courses dulu atau hardcode
        course_id = self.course_id or 1
        self.client.get(
            f"/api/v1/courses/{course_id}",
            headers=self.get_headers(),
            name="GET /api/v1/courses/{id}"
        )

    @task(2)
    def get_course_contents(self):
        """
        Task: Mengambil content dalam course.
        Weight 2.
        """
        course_id = self.course_id or 1
        self.client.get(
            f"/api/v1/courses/{course_id}/contents",
            headers=self.get_headers(),
            name="GET /api/v1/courses/{id}/contents"
        )

    @task(2)
    def list_comments(self):
        """
        Task: Mengambil daftar komentar pada content.
        Weight 2.
        """
        content_id = 1  # Assume content id 1 exists
        self.client.get(
            f"/api/v1/contents/{content_id}/comments",
            headers=self.get_headers(),
            name="GET /api/v1/contents/{id}/comments"
        )

    @task(1)
    def create_comment(self):
        """
        Task: Membuat komentar baru.
        Weight 1 = frekuensi default (paling jarang).
        """
        content_id = 1  # Assume content id 1 exists
        self.client.post(
            f"/api/v1/contents/{content_id}/comments",
            json={"comment": f"Great content! (from load test)"},
            headers=self.get_headers(),
            name="POST /api/v1/contents/{id}/comments"
        )

    @task(1)
    def get_user_profile(self):
        """
        Task: Mengambil profile user yang login.
        Weight 1.
        """
        self.client.get(
            "/api/v1/auth/me",
            headers=self.get_headers(),
            name="GET /api/v1/auth/me"
        )

    @task(1)
    def search_courses(self):
        """
        Task: Mencari courses dengan filter.
        Weight 1.
        """
        search_terms = ["Django", "Python", "Testing", "API"]
        import random
        term = random.choice(search_terms)
        
        self.client.get(
            f"/api/v1/courses?search={term}",
            headers=self.get_headers(),
            name="GET /api/v1/courses (dengan search)"
        )


class AdminUser(HttpUser):
    """Simulasi admin/teacher yang melakukan operasi CRUD lebih sering."""

    wait_time = between(2, 6)
    token = None

    def on_start(self):
        """Login sebagai teacher (admin)."""
        try:
            response = self.client.post(
                "/api/v1/auth/login",
                json={
                    "username": "teacher1",
                    "password": "teacherpass123"
                },
                name="POST /api/v1/auth/login (Admin)"
            )
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access") or data.get("token")
        except Exception as e:
            print(f"Admin login error: {e}")

    def get_headers(self):
        """Return headers dengan token."""
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    @task(4)
    def list_owned_courses(self):
        """Admin: List course yang dia miliki."""
        self.client.get(
            "/api/v1/courses",
            headers=self.get_headers(),
            name="GET /api/v1/courses (Admin)"
        )

    @task(2)
    def view_course_analytics(self):
        """Admin: Lihat analytics course."""
        course_id = 1
        self.client.get(
            f"/api/v1/courses/{course_id}",
            headers=self.get_headers(),
            name="GET /api/v1/courses/{id} (Admin Analytics)"
        )

    @task(2)
    def view_course_members(self):
        """Admin: Lihat member yang terdaftar."""
        course_id = 1
        self.client.get(
            f"/api/v1/courses/{course_id}/members",
            headers=self.get_headers(),
            name="GET /api/v1/courses/{id}/members"
        )

    @task(1)
    def create_content(self):
        """Admin: Buat content baru (jarang)."""
        course_id = 1
        self.client.post(
            f"/api/v1/courses/{course_id}/contents",
            json={
                "name": f"New Lesson (Load Test)",
                "description": "Description",
                "video_url": "https://youtube.com/watch?v=example"
            },
            headers=self.get_headers(),
            name="POST /api/v1/courses/{id}/contents"
        )

# 🎓 Simple LMS - REST API & Authentication System

Sistem backend **Simple Learning Management System (LMS)** berbasis **Django Ninja** yang dibuat untuk memenuhi tugas **Progress 3** mata kuliah **Pemrograman Sisi Server**.

Project ini mengimplementasikan **REST API lengkap**, **JWT Authentication**, **Role-Based Access Control (RBAC)**, validasi schema menggunakan **Pydantic**, serta dokumentasi API otomatis menggunakan **Swagger UI**.

---

# 👨‍🎓 Identitas Mahasiswa

| Keterangan | Data                               |
| ---------- | ---------------------------------- |
| **Nama**   | Iqbal Tegar Pratama                |
| **NIM**    | A11.2023.14969                     |
| **Kelas**  | Pemrograman Sisi Server (A11.4602) |

---

# 📌 Deskripsi Project

Simple LMS adalah sistem pembelajaran online sederhana yang memungkinkan pengguna untuk:

- Mendaftar akun
- Login menggunakan JWT Token
- Melihat daftar course
- Membuat course (Instructor)
- Mengedit course milik sendiri
- Menghapus course (Admin)
- Mendaftar course (Student)
- Melihat course yang diikuti
- Menandai progress pembelajaran

---

# 🎯 Tujuan Pembelajaran

Project ini dibuat untuk mempelajari:

✅ Pembuatan REST API menggunakan Django Ninja
✅ Implementasi JWT Authentication
✅ Sistem hak akses berbasis role
✅ Validasi data dengan Pydantic Schema
✅ Dokumentasi API otomatis dengan Swagger
✅ Struktur backend modern menggunakan Django

---

# 🛠️ Teknologi yang Digunakan

| Teknologi           | Fungsi             |
| ------------------- | ------------------ |
| Python 3            | Bahasa Pemrograman |
| Django              | Framework Backend  |
| Django Ninja        | REST API Framework |
| SQLite / PostgreSQL | Database           |
| JWT                 | Authentication     |
| Pydantic            | Validasi Schema    |
| Swagger UI          | Dokumentasi API    |

---

# 📂 Struktur Fitur

# 🔐 Authentication System

Fitur autentikasi user:

- Register akun baru
- Login user
- Generate Access Token
- Generate Refresh Token
- Melihat profil user login
- Update profil user

---

# 📚 Course Management

## Public Endpoint

Dapat diakses tanpa login:

- Melihat semua course
- Detail course
- Filter course
- Pagination

## Protected Endpoint

Butuh login:

- Membuat course (**Instructor**)
- Edit course sendiri (**Owner**)
- Hapus course (**Admin**)

---

# 📝 Enrollment System

- Student dapat daftar course
- Melihat course yang diikuti
- Menandai progress lesson selesai

---

# 🛡️ Role Based Access Control (RBAC)

Sistem role user:

| Role       | Hak Akses             |
| ---------- | --------------------- |
| Admin      | Semua akses           |
| Instructor | Membuat & edit course |
| Student    | Enroll course         |

Decorator permission:

```python id="mhcc1z"
@is_admin
@is_instructor
@is_student
```

---

# 📌 API Endpoint Lengkap

# Authentication

| Method | Endpoint             | Keterangan         |
| ------ | -------------------- | ------------------ |
| POST   | `/api/auth/register` | Register user baru |
| POST   | `/api/auth/login`    | Login user         |
| POST   | `/api/auth/refresh`  | Refresh token      |
| GET    | `/api/auth/me`       | Data user login    |
| PUT    | `/api/auth/me`       | Update profil      |

---

# Courses

| Method | Endpoint            | Keterangan    |
| ------ | ------------------- | ------------- |
| GET    | `/api/courses`      | Semua course  |
| GET    | `/api/courses/{id}` | Detail course |
| POST   | `/api/courses`      | Tambah course |
| PATCH  | `/api/courses/{id}` | Edit course   |
| DELETE | `/api/courses/{id}` | Hapus course  |

---

# Enrollments

| Method | Endpoint                         | Keterangan      |
| ------ | -------------------------------- | --------------- |
| POST   | `/api/enrollments`               | Daftar course   |
| GET    | `/api/enrollments/my-courses`    | Course saya     |
| POST   | `/api/enrollments/{id}/progress` | Update progress |

---

# 📖 Dokumentasi Swagger

Swagger UI tersedia di:

```bash id="efp94o"
http://localhost:8000/api/docs
```

Fungsi Swagger:

- Melihat semua endpoint
- Test API langsung
- Input JSON request
- Melihat response
- Testing token login

---

# ⚙️ Cara Menjalankan Project

## 1. Clone Repository

```bash id="j3e7nn"
git clone https://github.com/username/simple-lms.git
cd simple-lms
```

## 2. Install Dependency

```bash id="w5l2o7"
pip install -r requirements.txt
```

## 3. Migrasi Database

```bash id="5z2u0q"
python manage.py migrate
```

## 4. Jalankan Server

```bash id="w0v9zd"
python manage.py runserver
```

---

# 🔑 Cara Login API

## Register User

```json id="eifndj"
{
  "username": "iqbal123",
  "password": "12345678",
  "email": "iqbal@gmail.com",
  "first_name": "Iqbal",
  "last_name": "Pratama"
}
```

## Login

```json id="9gzw49"
{
  "username": "iqbal123",
  "password": "12345678"
}
```

## Response

```json id="1x4tgm"
{
  "refresh": "xxxxx",
  "access": "xxxxx"
}
```

## Authorize Swagger

Klik tombol **Authorize** lalu isi:

```text id="8db7ez"
Bearer access_token_kamu
```

---

# 📷 Screenshot Pengujian

Tambahkan screenshot berikut:

- Register berhasil
- Login berhasil
- Token authorize berhasil
- GET data user
- Create course berhasil
- Error 404
- Error validasi

---

# 🧪 Testing

Project diuji menggunakan:

- Swagger UI
- Postman

---

# 📁 Kriteria Penilaian yang Dipenuhi

✅ Kelengkapan API Endpoint
✅ JWT Authentication berjalan
✅ RBAC berjalan
✅ Schema Validation
✅ Swagger Documentation
✅ Postman Collection

---

# 👨‍💻 Author

**Iqbal Tegar Pratama**
**NIM:** A11.2023.14969
**Kelas:** Pemrograman Sisi Server (A11.4602)

---

# ⭐ Penutup

Project ini dibuat sebagai media pembelajaran implementasi backend modern menggunakan Django Ninja dan REST API.

Terima kasih.

# Simple LMS - Automated Testing Guide

> Panduan lengkap untuk menjalankan automated testing pada Simple LMS

## 🎯 Quick Start

### Run Semua Tests

```bash
cd "d:\Semester 6\Pemrograman Sisi Server\Automated Testing"
docker-compose exec web python manage.py test --no-input
```

**Expected Output:**

```
Found 70 test(s).
...
Ran 70 tests in 7.041s

OK ✅
```

### Run Tests dengan Detail

```bash
docker-compose exec web python manage.py test -v 2
```

---

## 📋 Test Structure

```
tests/
├── __init__.py                      # Test package
├── test_calculator.py              # 19 unit tests
├── test_validators.py              # 13 unit tests
├── test_models.py                  # 38 model tests
└── test_api_basic.py               # 9 integration tests
```

### Test Execution

```bash
# Run semua tests
python manage.py test

# Run specific test file
python manage.py test tests.test_calculator
python manage.py test tests.test_validators
python manage.py test tests.test_models
python manage.py test tests.test_api_basic

# Run specific test class
python manage.py test tests.test_models.TestCourseModel

# Run specific test method
python manage.py test tests.test_calculator.TestCalculator.test_divide_by_zero_raises_error

# Run dengan verbose output
python manage.py test -v 2

# Run dengan coverage
coverage run manage.py test --no-input
coverage report
```

---

## 🔍 Test Coverage

### Generate Coverage Report

```bash
# Run tests dengan coverage tracking
docker-compose exec web coverage run manage.py test --no-input

# Lihat report di terminal
docker-compose exec web coverage report

# Generate HTML report
docker-compose exec web coverage html

# Buka laporan di browser
# Buka file: htmlcov/index.html
```

### Coverage Configuration

File: `.coveragerc`

```ini
[run]
source = core, utils
omit = */migrations/*, */tests/*, */admin.py

[report]
fail_under = 80          # Minimum coverage threshold
show_missing = True      # Show uncovered lines
precision = 2           # Show 2 decimal places

[html]
directory = htmlcov     # HTML report directory
```

### Expected Coverage Results

```
Overall: 96.0%+ ✅ (Target: 80%)
- core/models.py ......... 94.7%
- utils/calculator.py .... 100%
- utils/validators.py .... 100%
```

---

## 📊 Load Testing

### Configuration

File: `locustfile.py`

**User Types:**

- **LMSUser** - Student behavior
  - List courses (5x frequency)
  - View details (3x)
  - View content (2x)
  - Read comments (2x)
  - Create comment (1x)
  - Think time: 1-5 seconds

- **AdminUser** - Teacher behavior
  - List courses (4x)
  - View analytics (2x)
  - View members (2x)
  - Create content (1x)
  - Think time: 2-6 seconds

### Run Load Tests

**Interactive Mode (Recommended for initial testing):**

```bash
locust -f locustfile.py --host=http://localhost:8000
```

Then open: http://localhost:8089

**Headless Mode (Automated):**

```bash
locust -f locustfile.py \
  --host=http://localhost:8000 \
  --headless \
  --users 20 \
  --spawn-rate 2 \
  --run-time 1m
```

**Heavy Load (untuk stress testing):**

```bash
locust -f locustfile.py \
  --host=http://localhost:8000 \
  --headless \
  --users 100 \
  --spawn-rate 10 \
  --run-time 5m \
  --csv=results/report
```

### Expected Results

```
Response Time (avg):
- GET /api/v1/courses ............... ~45ms
- GET /api/v1/courses/{id} .......... ~38ms
- POST /api/v1/contents/{id}/comments  ~92ms

Error Rate: < 1% ✅
Throughput: 50+ RPS ✅
```

---

## 📚 Test Details

### Unit Tests - Calculator (19 tests)

Tests untuk `utils/calculator.py`:

```python
✅ Addition
  - test_add_positive_numbers
  - test_add_negative_numbers
  - test_add_mixed_numbers
  - test_add_zero
  - test_add_floats

✅ Subtraction
  - test_subtract_positive_numbers
  - test_subtract_negative_result
  - test_subtract_same_number
  - test_subtract_floats

✅ Multiplication
  - test_multiply_positive_numbers
  - test_multiply_by_zero
  - test_multiply_negative_numbers
  - test_multiply_floats

✅ Division
  - test_divide_positive_numbers
  - test_divide_returns_float
  - test_divide_by_zero_raises_error
  - test_divide_negative_numbers
  - test_divide_floats
  - test_divide_fraction_result
```

### Unit Tests - Validators (13 tests)

Tests untuk `utils/validators.py`:

```python
✅ Valid Passwords
  - test_valid_password
  - test_password_exactly_8_chars
  - test_password_with_multiple_special_chars

✅ Invalid Passwords (Single Criteria)
  - test_password_too_short
  - test_password_no_uppercase
  - test_password_no_lowercase
  - test_password_no_number
  - test_password_no_special_char

✅ Edge Cases
  - test_empty_password
  - test_password_multiple_errors
  - test_password_all_errors
  - test_password_very_long
  - test_password_response_structure
```

### Unit Tests - Models (38 tests)

Tests untuk `core/models.py`:

```python
✅ Course Model (6 tests)
✅ CourseMember Model (6 tests)
✅ CourseContent Model (5 tests)
✅ Comment Model (5 tests)
✅ CourseProgress Model (7 tests)
```

### Integration Tests (9 tests)

Tests untuk `tests/test_api_basic.py`:

```python
✅ Course API (4 tests)
✅ Comment API (3 tests)
✅ Course Member/Enrollment (3 tests)
```

---

## 🚀 Tips & Best Practices

### For Development

1. **Before pushing code:**

   ```bash
   docker-compose exec web python manage.py test --no-input
   ```

2. **When tests fail:**
   - Run dengan `-v 2` untuk detail
   - Check error message for specific failure
   - Fix code dan run test again

3. **Add new tests:**
   - Create new test method di existing test class
   - Follow naming convention: `test_<feature>_<scenario>`
   - Include docstring explaining the test

### For CI/CD

1. **Add to pipeline:**

   ```yaml
   - name: Run Tests
     run: docker-compose exec web python manage.py test

   - name: Check Coverage
     run: |
       docker-compose exec web coverage run manage.py test
       docker-compose exec web coverage report --fail-under=80
   ```

2. **Generate artifacts:**
   - Coverage report HTML
   - Load test results CSV
   - Test failure reports

### For Performance Optimization

1. **Use load testing data:**
   - Identify slow endpoints
   - Check response time trends
   - Plan caching strategy

2. **Monitor improvements:**
   - Run load tests after optimization
   - Compare metrics with baseline
   - Track improvements over time

---

## 📖 Documentation

- **TESTING_REPORT.md** - Comprehensive testing analysis
- **TUGAS_10_SUBMISSION.md** - Complete submission document
- **This file** - Quick reference guide

---

## ✅ Checklist

Before submission, verify:

- [ ] All 70 tests passing
- [ ] Coverage > 80% (current: 96%)
- [ ] Load testing configured
- [ ] Documentation complete
- [ ] Code committed to repository
- [ ] README.md in project root

---

## 📞 Support

For issues or questions:

1. Check TESTING_REPORT.md for detailed explanations
2. Run `python manage.py test -v 2` for error details
3. Review test source code with docstrings

---

**Last Updated**: 2025-06-24  
**Status**: Ready for Production ✅

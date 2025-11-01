# Sietch Faces - Test Suite

Comprehensive test coverage for the Sietch Faces Core API, including unit tests, integration tests, and performance tests.

## 🎯 Coverage Goal

- **Target:** >80% test coverage
- **Current Status:** Run `pytest --cov=app --cov-report=term-missing` to check

## 📋 Test Structure

### Unit Tests
Unit tests for individual components without external dependencies:

- **`test_face_detection.py`** - Face detection service tests
  - Face detection with various confidence thresholds
  - Face extraction from images
  - Error handling for invalid inputs
  - Edge cases (no faces, multiple faces, small faces)

- **`test_face_recognition.py`** - Face recognition/embedding service tests
  - Embedding generation
  - Similarity calculation
  - Similar face search
  - Embedding serialization/deserialization

- **`test_clustering.py`** - Clustering service tests
  - DBSCAN clustering algorithm
  - Cluster statistics
  - Edge cases (empty input, single face, noise)

- **`test_models.py`** - Database model tests
  - Person and Face model creation
  - Relationships and cascading
  - Model properties and methods

### Integration Tests
Integration tests for API endpoints and interactions:

- **`test_api_endpoints.py`** - Core API endpoint tests
  - Face detection endpoint
  - Person management endpoints
  - Face listing and retrieval
  - Health and stats endpoints

- **`test_auth.py`** - Authentication and authorization tests
  - API key validation
  - Unauthorized access handling
  - Rate limiting

- **`test_error_handling.py`** - Error handling tests
  - Invalid input validation
  - Database errors
  - File upload errors
  - HTTP error codes (404, 422, 500)

- **`test_pagination.py`** - Pagination and filtering tests
  - Skip and limit parameters
  - Filtering by various criteria
  - Sorting
  - Edge cases

### Performance Tests
Performance and load tests:

- **`test_performance.py`** - Performance baseline tests
  - Face detection speed
  - Similarity search speed
  - Concurrent request handling
  - Database query performance

- **`locustfile.py`** - Load testing with Locust
  - Normal load scenarios
  - High load scenarios
  - Spike testing
  - Endurance testing

## 🚀 Running Tests

### Run All Tests
```bash
pytest tests/ -v
```

### Run Unit Tests Only
```bash
pytest tests/ -v -m unit
```

### Run Integration Tests Only
```bash
pytest tests/ -v -m integration
```

### Run Performance Tests Only
```bash
pytest tests/ -v -m performance
```

### Run with Coverage
```bash
pytest tests/ -v --cov=app --cov-report=html --cov-report=term-missing
```

### Run Specific Test File
```bash
pytest tests/test_face_detection.py -v
```

### Run Specific Test
```bash
pytest tests/test_face_detection.py::TestFaceDetector::test_detect_faces_success -v
```

## 📊 Coverage Reports

### Generate HTML Coverage Report
```bash
pytest tests/ --cov=app --cov-report=html
# Open htmlcov/index.html in browser
```

### Generate Terminal Coverage Report
```bash
pytest tests/ --cov=app --cov-report=term-missing
```

### Generate XML Coverage Report (for CI)
```bash
pytest tests/ --cov=app --cov-report=xml
```

## 🔥 Load Testing with Locust

### Install Locust
```bash
pip install locust
```

### Run Load Tests
```bash
# Start Locust web interface
locust -f tests/locustfile.py --host=http://localhost:8000

# Open http://localhost:8089 and configure:
# - Number of users: 10-100
# - Spawn rate: 1-10 users/second
# - Run time: 1-30 minutes
```

### Run Headless Load Test
```bash
# Normal load
locust -f tests/locustfile.py --host=http://localhost:8000 \
  --users=10 --spawn-rate=2 --run-time=5m --headless

# High load
locust -f tests/locustfile.py --host=http://localhost:8000 \
  --users=50 --spawn-rate=5 --run-time=10m --headless

# Spike test
locust -f tests/locustfile.py --host=http://localhost:8000 \
  --users=100 --spawn-rate=20 --run-time=2m --headless
```

## 🎨 Test Fixtures

Common fixtures are defined in `conftest.py`:

- `test_db_session` - Test database session
- `core_client` - Test client for Core API
- `sample_face_image` - Sample face image for testing
- `sample_embedding` - Sample 512D embedding
- `api_headers` - API authentication headers
- And more...

## 🏗️ CI/CD Integration

Tests run automatically on every push and pull request via GitHub Actions.

See `.github/workflows/ci.yml` for CI configuration.

### CI Jobs:
1. **Test** - Run all tests with coverage on Python 3.9, 3.10, 3.11
2. **Performance Test** - Run performance baseline tests
3. **Code Quality** - Run linting and type checking
4. **Security Scan** - Run security vulnerability scans

## 📈 Performance Baselines

Expected performance (from `test_performance.py`):

### API Endpoints
- Health check: < 100ms
- Stats endpoint: < 1s
- List persons (100 records): < 2s
- Face detection: < 10s per image

### Algorithms
- Similarity calculation: < 0.1ms per comparison
- Clustering (100 faces): < 5s
- Similarity search (1000 faces): < 1s

### Concurrency
- 50 concurrent health checks: < 5s
- 20 concurrent person creations: < 5s

## 🐛 Debugging Tests

### Run Tests with More Verbose Output
```bash
pytest tests/ -vv
```

### Show Print Statements
```bash
pytest tests/ -s
```

### Stop on First Failure
```bash
pytest tests/ -x
```

### Run Last Failed Tests
```bash
pytest tests/ --lf
```

### Run Tests in Parallel
```bash
pip install pytest-xdist
pytest tests/ -n auto
```

## 📝 Writing New Tests

### Test Naming Convention
- Test files: `test_*.py`
- Test classes: `Test*`
- Test methods: `test_*`

### Test Markers
Use pytest markers to categorize tests:
```python
@pytest.mark.unit
def test_something():
    pass

@pytest.mark.integration
def test_api_endpoint():
    pass

@pytest.mark.performance
@pytest.mark.slow
def test_load():
    pass
```

### Using Fixtures
```python
def test_with_fixtures(test_db_session, sample_face_image):
    # test_db_session and sample_face_image are fixtures
    pass
```

### Mocking External Dependencies
```python
from unittest.mock import patch

@patch('app.face_detection.RetinaFace.detect_faces')
def test_with_mock(mock_detect):
    mock_detect.return_value = {}
    # test code
```

## 🎯 Coverage Goals by Component

| Component | Current | Target |
|-----------|---------|--------|
| Face Detection | TBD | >80% |
| Face Recognition | TBD | >80% |
| Clustering | TBD | >80% |
| Database Models | TBD | >90% |
| API Endpoints | TBD | >85% |
| Authentication | TBD | >90% |
| **Overall** | **TBD** | **>80%** |

Run tests with coverage to update these values.

## 📚 Additional Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [Locust Documentation](https://docs.locust.io/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)

## 🤝 Contributing

When adding new features:
1. Write tests first (TDD approach recommended)
2. Ensure all tests pass
3. Maintain >80% coverage
4. Add performance tests for critical paths
5. Update this README if needed

## 📞 Support

For issues with tests, please:
1. Check test output and error messages
2. Review test documentation
3. Run tests with `-vv` flag for more details
4. Open an issue with test failure details

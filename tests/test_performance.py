"""
Performance tests for Core API.

Tests performance including:
- Face detection speed
- Similarity search speed
- Concurrent request handling
- Load testing scenarios
- Performance baselines
"""
import pytest
import time
import concurrent.futures
from unittest.mock import patch
import numpy as np

try:
    from app.models_core import Person, Face
    from app.face_detection import FaceDetector
    from app.face_recognition import FaceRecognizer
    from app.clustering import FaceClustering
    CORE_MODELS_AVAILABLE = True
except ImportError:
    CORE_MODELS_AVAILABLE = False


@pytest.mark.performance
@pytest.mark.slow
@pytest.mark.skipif(not CORE_MODELS_AVAILABLE, reason="Core API not available")
class TestPerformance:
    """Performance test suite."""
    
    def test_health_endpoint_response_time(self, core_client):
        """Test health endpoint responds quickly."""
        start = time.time()
        response = core_client.get("/health")
        elapsed = time.time() - start
        
        assert response.status_code == 200
        # Should respond in under 100ms
        assert elapsed < 0.1
    
    def test_stats_endpoint_performance(self, core_client, test_db_session):
        """Test stats endpoint performance with data."""
        # Create some test data
        for i in range(100):
            person = Person(name=f"Person {i}")
            test_db_session.add(person)
        test_db_session.commit()
        
        start = time.time()
        response = core_client.get("/stats")
        elapsed = time.time() - start
        
        assert response.status_code == 200
        # Should complete in reasonable time
        assert elapsed < 1.0  # 1 second
    
    def test_list_persons_performance(self, core_client, test_db_session):
        """Test listing persons with many records."""
        # Create 500 persons
        batch_size = 100
        for batch in range(5):
            persons = [Person(name=f"Person {batch*batch_size + i}") for i in range(batch_size)]
            test_db_session.add_all(persons)
            test_db_session.commit()
        
        start = time.time()
        response = core_client.get("/persons?limit=100")
        elapsed = time.time() - start
        
        assert response.status_code == 200
        # Should complete in reasonable time
        assert elapsed < 2.0  # 2 seconds
    
    def test_list_faces_performance(self, core_client, test_db_session):
        """Test listing faces with many records."""
        # Create 200 faces
        batch_size = 50
        for batch in range(4):
            faces = [
                Face(
                    image_path=f"/path/{batch*batch_size + i}.jpg",
                    bbox_x=i*10, bbox_y=i*10, bbox_width=100, bbox_height=100,
                    confidence=0.9,
                    embedding=[float(i)] * 512
                ) for i in range(batch_size)
            ]
            test_db_session.add_all(faces)
            test_db_session.commit()
        
        start = time.time()
        response = core_client.get("/faces?limit=50")
        elapsed = time.time() - start
        
        assert response.status_code == 200
        # Should complete quickly
        assert elapsed < 2.0
    
    @patch('app.routes.core.detector.detect_faces')
    @patch('app.routes.core.recognizer.generate_embedding')
    def test_detection_endpoint_performance(self, mock_embedding, mock_detect, core_client, sample_face_image):
        """Test face detection endpoint performance."""
        # Mock quick responses
        mock_detect.return_value = [{
            'facial_area': [50, 50, 100, 100],
            'score': 0.95,
            'landmarks': {}
        }]
        mock_embedding.return_value = np.random.randn(512)
        
        files = {"file": ("test.jpg", sample_face_image, "image/jpeg")}
        data = {"min_confidence": 0.9, "auto_save": False}
        
        start = time.time()
        response = core_client.post("/detect", files=files, data=data)
        elapsed = time.time() - start
        
        assert response.status_code == 200
        result = response.json()
        
        # Check performance metrics if available
        if "processing_time_ms" in result:
            # API reports processing time
            assert result["processing_time_ms"] < 5000  # 5 seconds
        
        # Total response time
        assert elapsed < 10.0  # 10 seconds max
    
    def test_concurrent_health_checks(self, core_client):
        """Test handling concurrent health check requests."""
        def make_request():
            return core_client.get("/health")
        
        start = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(50)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        elapsed = time.time() - start
        
        # All requests should succeed
        assert all(r.status_code == 200 for r in results)
        # Should handle 50 requests in reasonable time
        assert elapsed < 5.0
    
    def test_concurrent_person_creation(self, core_client):
        """Test concurrent person creation."""
        def create_person(index):
            data = {"name": f"Concurrent Person {index}"}
            return core_client.post("/persons", json=data)
        
        start = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(create_person, i) for i in range(20)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        elapsed = time.time() - start
        
        # All should succeed
        successful = [r for r in results if r.status_code == 200]
        assert len(successful) == 20
        # Should complete in reasonable time
        assert elapsed < 5.0
    
    def test_concurrent_person_reads(self, core_client, test_db_session):
        """Test concurrent reading of persons."""
        # Create test persons
        persons = [Person(name=f"Person {i}") for i in range(10)]
        test_db_session.add_all(persons)
        test_db_session.commit()
        
        person_ids = [p.id for p in persons]
        
        def read_person(person_id):
            return core_client.get(f"/persons/{person_id}")
        
        start = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(read_person, pid) for pid in person_ids * 5]  # 50 reads
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        elapsed = time.time() - start
        
        # All should succeed
        assert all(r.status_code == 200 for r in results)
        # Should be fast
        assert elapsed < 3.0
    
    def test_memory_usage_with_large_embeddings(self, test_db_session):
        """Test memory efficiency with many embeddings."""
        # Create many faces with embeddings
        num_faces = 1000
        
        start = time.time()
        for i in range(num_faces):
            face = Face(
                image_path=f"/path/{i}.jpg",
                bbox_x=0, bbox_y=0, bbox_width=100, bbox_height=100,
                confidence=0.9,
                embedding=[float(i % 100) / 100.0] * 512
            )
            test_db_session.add(face)
            
            if i % 100 == 0:
                test_db_session.commit()
        
        test_db_session.commit()
        elapsed = time.time() - start
        
        # Should complete in reasonable time
        assert elapsed < 30.0  # 30 seconds for 1000 faces
    
    def test_query_performance_with_large_dataset(self, test_db_session):
        """Test query performance with large dataset."""
        # Create dataset
        person = Person(name="Query Test")
        test_db_session.add(person)
        test_db_session.commit()
        
        # Add many faces
        for i in range(500):
            face = Face(
                image_path=f"/path/{i}.jpg",
                bbox_x=0, bbox_y=0, bbox_width=100, bbox_height=100,
                confidence=0.9,
                embedding=[float(i % 100) / 100.0] * 512,
                person_id=person.id
            )
            test_db_session.add(face)
        test_db_session.commit()
        
        # Query faces
        start = time.time()
        faces = test_db_session.query(Face).filter(Face.person_id == person.id).all()
        elapsed = time.time() - start
        
        assert len(faces) == 500
        # Query should be fast
        assert elapsed < 1.0


@pytest.mark.performance
@pytest.mark.unit
class TestAlgorithmPerformance:
    """Performance tests for algorithms."""
    
    def test_face_detector_initialization_time(self):
        """Test face detector initialization time."""
        start = time.time()
        detector = FaceDetector()
        elapsed = time.time() - start
        
        # Initialization should be fast
        assert elapsed < 1.0
    
    def test_face_recognizer_initialization_time(self):
        """Test face recognizer initialization time."""
        start = time.time()
        recognizer = FaceRecognizer()
        elapsed = time.time() - start
        
        # Initialization should be fast
        assert elapsed < 1.0
    
    def test_similarity_calculation_performance(self, sample_embedding):
        """Test similarity calculation speed."""
        recognizer = FaceRecognizer()
        
        # Create another embedding
        embedding2 = np.random.randn(512)
        embedding2 = embedding2 / np.linalg.norm(embedding2)
        
        # Measure time for 1000 similarity calculations
        start = time.time()
        for _ in range(1000):
            recognizer.calculate_similarity(sample_embedding, embedding2)
        elapsed = time.time() - start
        
        # Should be very fast (vectorized operations)
        assert elapsed < 0.1  # 100ms for 1000 calculations
    
    def test_clustering_performance(self, sample_embeddings_dict):
        """Test clustering algorithm performance."""
        clusterer = FaceClustering()
        
        # Extend to larger dataset
        large_dict = {}
        for i in range(100):
            embedding = np.random.randn(512).astype(np.float32)
            embedding = embedding / np.linalg.norm(embedding)
            large_dict[i] = embedding
        
        start = time.time()
        clusters = clusterer.cluster_faces(large_dict)
        elapsed = time.time() - start
        
        # Should complete in reasonable time
        assert elapsed < 5.0  # 5 seconds for 100 faces
    
    def test_similarity_search_performance(self, sample_embedding):
        """Test similarity search performance."""
        recognizer = FaceRecognizer()
        
        # Create large embeddings dictionary
        embeddings_dict = {}
        for i in range(1000):
            embedding = np.random.randn(512).astype(np.float32)
            embedding = embedding / np.linalg.norm(embedding)
            embeddings_dict[i] = embedding
        
        start = time.time()
        matches = recognizer.find_similar_faces(sample_embedding, embeddings_dict, threshold=0.6)
        elapsed = time.time() - start
        
        # Should search through 1000 embeddings quickly
        assert elapsed < 1.0  # 1 second for 1000 comparisons
    
    def test_embedding_serialization_performance(self, sample_embedding):
        """Test embedding serialization speed."""
        # Measure serialization
        start = time.time()
        for _ in range(1000):
            FaceRecognizer.serialize_embedding(sample_embedding)
        elapsed = time.time() - start
        
        # Should be fast
        assert elapsed < 0.5  # 500ms for 1000 serializations
    
    def test_embedding_deserialization_performance(self, sample_embedding):
        """Test embedding deserialization speed."""
        # Serialize once
        embedding_bytes = FaceRecognizer.serialize_embedding(sample_embedding)
        
        # Measure deserialization
        start = time.time()
        for _ in range(1000):
            FaceRecognizer.deserialize_embedding(embedding_bytes)
        elapsed = time.time() - start
        
        # Should be fast
        assert elapsed < 0.5  # 500ms for 1000 deserializations


# Performance baselines documentation
PERFORMANCE_BASELINES = """
Performance Baselines (as of test creation):

API Endpoints:
- Health check: < 100ms
- Stats endpoint: < 1s
- List persons (100 records): < 2s
- List faces (50 records): < 2s
- Face detection: < 10s per image

Algorithms:
- Similarity calculation: < 0.1ms per comparison
- Clustering (100 faces): < 5s
- Similarity search (1000 faces): < 1s
- Embedding serialization: < 0.5ms
- Embedding deserialization: < 0.5ms

Concurrency:
- 50 concurrent health checks: < 5s
- 20 concurrent person creations: < 5s
- 50 concurrent person reads: < 3s

Database:
- Insert 1000 faces: < 30s
- Query 500 faces by person: < 1s

Note: Actual performance depends on hardware, database configuration,
and whether ML models are GPU-accelerated.
"""

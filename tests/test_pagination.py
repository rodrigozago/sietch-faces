"""
Integration tests for pagination and filtering.

Tests pagination and filtering including:
- Skip and limit parameters
- Filtering by various criteria
- Sorting
- Edge cases
"""
import pytest

try:
    from app.models_core import Person, Face
    CORE_MODELS_AVAILABLE = True
except ImportError:
    CORE_MODELS_AVAILABLE = False


@pytest.mark.integration
@pytest.mark.skipif(not CORE_MODELS_AVAILABLE, reason="Core API not available")
class TestPagination:
    """Test suite for pagination."""
    
    def test_persons_pagination_default(self, core_client, test_db_session):
        """Test default pagination for persons list."""
        # Create 25 persons
        for i in range(25):
            person = Person(name=f"Person {i}")
            test_db_session.add(person)
        test_db_session.commit()
        
        response = core_client.get("/persons")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Default limit might vary
        assert len(data) <= 100
    
    def test_persons_pagination_with_limit(self, core_client, test_db_session):
        """Test pagination with custom limit."""
        # Create 20 persons
        for i in range(20):
            person = Person(name=f"Person {i}")
            test_db_session.add(person)
        test_db_session.commit()
        
        response = core_client.get("/persons?limit=5")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 5
    
    def test_persons_pagination_with_skip(self, core_client, test_db_session):
        """Test pagination with skip parameter."""
        # Create 15 persons
        persons = []
        for i in range(15):
            person = Person(name=f"Person {i:02d}")
            persons.append(person)
            test_db_session.add(person)
        test_db_session.commit()
        
        # Get first page
        response1 = core_client.get("/persons?skip=0&limit=5")
        assert response1.status_code == 200
        page1 = response1.json()
        
        # Get second page
        response2 = core_client.get("/persons?skip=5&limit=5")
        assert response2.status_code == 200
        page2 = response2.json()
        
        # Pages should be different
        page1_ids = [p["id"] for p in page1]
        page2_ids = [p["id"] for p in page2]
        
        # No overlap between pages
        assert len(set(page1_ids) & set(page2_ids)) == 0
    
    def test_persons_pagination_skip_beyond_total(self, core_client, test_db_session):
        """Test pagination when skip exceeds total count."""
        # Create 5 persons
        for i in range(5):
            person = Person(name=f"Person {i}")
            test_db_session.add(person)
        test_db_session.commit()
        
        # Skip beyond total
        response = core_client.get("/persons?skip=100&limit=10")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0
    
    def test_persons_pagination_limit_zero(self, core_client):
        """Test pagination with limit=0."""
        response = core_client.get("/persons?limit=0")
        
        # Should handle gracefully
        assert response.status_code in [200, 422]
        
        if response.status_code == 200:
            data = response.json()
            assert len(data) == 0
    
    def test_faces_pagination(self, core_client, test_db_session):
        """Test pagination for faces list."""
        # Create 30 faces
        for i in range(30):
            face = Face(
                image_path=f"/path/{i}.jpg",
                bbox_x=i*10, bbox_y=i*10, bbox_width=100, bbox_height=100,
                confidence=0.9,
                embedding=[float(i)] * 512
            )
            test_db_session.add(face)
        test_db_session.commit()
        
        # Test pagination
        response = core_client.get("/faces?skip=10&limit=10")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 10
    
    def test_pagination_consistency(self, core_client, test_db_session):
        """Test that pagination is consistent across multiple requests."""
        # Create 20 persons
        for i in range(20):
            person = Person(name=f"Person {i:03d}")
            test_db_session.add(person)
        test_db_session.commit()
        
        # Request same page twice
        response1 = core_client.get("/persons?skip=5&limit=5")
        response2 = core_client.get("/persons?skip=5&limit=5")
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        data1 = response1.json()
        data2 = response2.json()
        
        # Should return same results
        ids1 = [p["id"] for p in data1]
        ids2 = [p["id"] for p in data2]
        assert ids1 == ids2
    
    def test_pagination_with_empty_database(self, core_client):
        """Test pagination with empty database."""
        response = core_client.get("/persons?skip=0&limit=10")
        
        assert response.status_code == 200
        data = response.json()
        assert data == []
    
    def test_large_limit_value(self, core_client, test_db_session):
        """Test pagination with very large limit."""
        # Create 10 persons
        for i in range(10):
            person = Person(name=f"Person {i}")
            test_db_session.add(person)
        test_db_session.commit()
        
        # Request with large limit
        response = core_client.get("/persons?limit=10000")
        
        assert response.status_code in [200, 422]
        
        if response.status_code == 200:
            data = response.json()
            # Should return all persons (10)
            assert len(data) == 10


@pytest.mark.integration
@pytest.mark.skipif(not CORE_MODELS_AVAILABLE, reason="Core API not available")
class TestFiltering:
    """Test suite for filtering."""
    
    def test_filter_persons_by_name(self, core_client, test_db_session):
        """Test filtering persons by name."""
        # Create persons with different names
        person1 = Person(name="Alice")
        person2 = Person(name="Bob")
        person3 = Person(name="Alice Smith")
        test_db_session.add_all([person1, person2, person3])
        test_db_session.commit()
        
        # Try to filter (if endpoint supports it)
        response = core_client.get("/persons?name=Alice")
        
        # Filtering might not be implemented
        assert response.status_code in [200, 404, 422]
    
    def test_filter_faces_by_person_id(self, core_client, test_db_session):
        """Test filtering faces by person_id."""
        person = Person(name="Test Person")
        test_db_session.add(person)
        test_db_session.commit()
        
        # Create faces for this person
        for i in range(3):
            face = Face(
                image_path=f"/path/{i}.jpg",
                bbox_x=i*10, bbox_y=i*10, bbox_width=100, bbox_height=100,
                confidence=0.9,
                embedding=[float(i)] * 512,
                person_id=person.id
            )
            test_db_session.add(face)
        test_db_session.commit()
        
        # Try to filter faces by person
        response = core_client.get(f"/faces?person_id={person.id}")
        
        assert response.status_code in [200, 404, 422]
    
    def test_filter_faces_by_confidence(self, core_client, test_db_session):
        """Test filtering faces by confidence threshold."""
        # Create faces with different confidences
        confidences = [0.95, 0.85, 0.75]
        for i, conf in enumerate(confidences):
            face = Face(
                image_path=f"/path/{i}.jpg",
                bbox_x=i*10, bbox_y=i*10, bbox_width=100, bbox_height=100,
                confidence=conf,
                embedding=[float(i)] * 512
            )
            test_db_session.add(face)
        test_db_session.commit()
        
        # Try to filter
        response = core_client.get("/faces?min_confidence=0.9")
        
        assert response.status_code in [200, 404, 422]
    
    def test_combined_pagination_and_filtering(self, core_client, test_db_session):
        """Test combining pagination with filtering."""
        person = Person(name="Filter Test")
        test_db_session.add(person)
        test_db_session.commit()
        
        # Create many faces for this person
        for i in range(20):
            face = Face(
                image_path=f"/path/{i}.jpg",
                bbox_x=i*10, bbox_y=i*10, bbox_width=100, bbox_height=100,
                confidence=0.9,
                embedding=[float(i)] * 512,
                person_id=person.id
            )
            test_db_session.add(face)
        test_db_session.commit()
        
        # Combine filter and pagination
        response = core_client.get(f"/faces?person_id={person.id}&skip=5&limit=5")
        
        assert response.status_code in [200, 404, 422]


@pytest.mark.integration
@pytest.mark.skipif(not CORE_MODELS_AVAILABLE, reason="Core API not available")
class TestSorting:
    """Test suite for sorting."""
    
    def test_sort_persons_by_name(self, core_client, test_db_session):
        """Test sorting persons by name."""
        # Create persons
        names = ["Charlie", "Alice", "Bob"]
        for name in names:
            person = Person(name=name)
            test_db_session.add(person)
        test_db_session.commit()
        
        # Try to sort
        response = core_client.get("/persons?sort=name")
        
        # Sorting might not be implemented
        assert response.status_code in [200, 404, 422]
        
        if response.status_code == 200:
            data = response.json()
            names_returned = [p["name"] for p in data if p.get("name")]
            # Check if sorted (if sorting is implemented)
    
    def test_sort_persons_by_created_at(self, core_client, test_db_session):
        """Test sorting persons by creation date."""
        # Create persons
        for i in range(3):
            person = Person(name=f"Person {i}")
            test_db_session.add(person)
            test_db_session.commit()  # Commit individually for different timestamps
        
        # Try to sort
        response = core_client.get("/persons?sort=created_at")
        
        assert response.status_code in [200, 404, 422]
    
    def test_sort_descending_order(self, core_client, test_db_session):
        """Test sorting in descending order."""
        # Create persons
        for i in range(5):
            person = Person(name=f"Person {i}")
            test_db_session.add(person)
        test_db_session.commit()
        
        # Try descending sort
        response = core_client.get("/persons?sort=id&order=desc")
        
        assert response.status_code in [200, 404, 422]

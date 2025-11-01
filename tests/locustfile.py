"""
Locust load testing file for Sietch Faces Core API.

Run with:
    locust -f tests/locustfile.py --host=http://localhost:8000

This file defines load testing scenarios for:
- API health checks
- Face detection
- Person management
- Stats queries
"""
from locust import HttpUser, task, between, TaskSet
import random
import io
from PIL import Image


class CoreAPIUser(HttpUser):
    """
    Simulated user for Core API load testing.
    
    This user performs typical operations:
    - Checking API health
    - Viewing statistics
    - Managing persons
    - Detecting faces (simulated)
    """
    
    # Wait between 1 and 3 seconds between tasks
    wait_time = between(1, 3)
    
    def on_start(self):
        """Called when a user starts."""
        self.api_key = "change-this-in-production"  # Update with actual key
        self.headers = {"X-API-Key": self.api_key}
        self.person_ids = []
    
    @task(10)
    def check_health(self):
        """Check API health - most common operation."""
        self.client.get("/health", headers=self.headers)
    
    @task(5)
    def view_stats(self):
        """View system statistics."""
        self.client.get("/stats", headers=self.headers)
    
    @task(3)
    def list_persons(self):
        """List persons with pagination."""
        skip = random.randint(0, 50)
        limit = random.randint(10, 50)
        self.client.get(f"/persons?skip={skip}&limit={limit}", headers=self.headers)
    
    @task(2)
    def create_person(self):
        """Create a new person."""
        person_data = {
            "name": f"Load Test User {random.randint(1000, 9999)}"
        }
        response = self.client.post("/persons", json=person_data, headers=self.headers)
        
        if response.status_code == 200:
            data = response.json()
            if "id" in data:
                self.person_ids.append(data["id"])
    
    @task(3)
    def get_person(self):
        """Get a specific person."""
        if self.person_ids:
            person_id = random.choice(self.person_ids)
            self.client.get(f"/persons/{person_id}", headers=self.headers)
        else:
            # If no persons created yet, try a random ID
            person_id = random.randint(1, 100)
            self.client.get(f"/persons/{person_id}", headers=self.headers)
    
    @task(1)
    def update_person(self):
        """Update a person."""
        if self.person_ids:
            person_id = random.choice(self.person_ids)
            update_data = {
                "name": f"Updated User {random.randint(1000, 9999)}"
            }
            self.client.put(f"/persons/{person_id}", json=update_data, headers=self.headers)
    
    @task(2)
    def list_faces(self):
        """List faces with pagination."""
        skip = random.randint(0, 100)
        limit = random.randint(10, 50)
        self.client.get(f"/faces?skip={skip}&limit={limit}", headers=self.headers)
    
    @task(1)
    def detect_faces(self):
        """Simulate face detection upload."""
        # Create a simple test image
        img = Image.new('RGB', (200, 200), color='white')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        files = {"file": ("test.jpg", img_bytes, "image/jpeg")}
        data = {"min_confidence": 0.9, "auto_save": False}
        
        # Note: This might be slow depending on model performance
        with self.client.post("/detect", files=files, data=data, headers=self.headers, catch_response=True) as response:
            if response.elapsed.total_seconds() > 10:
                response.failure(f"Request took too long: {response.elapsed.total_seconds()}s")


class QuickUserBehavior(TaskSet):
    """Quick read-only operations."""
    
    @task(15)
    def health_check(self):
        self.client.get("/health")
    
    @task(10)
    def stats(self):
        self.client.get("/stats")
    
    @task(5)
    def list_persons(self):
        self.client.get("/persons?limit=20")


class HeavyUserBehavior(TaskSet):
    """Heavy operations including uploads."""
    
    @task(5)
    def detect_faces_multiple_times(self):
        """Perform multiple face detections."""
        for _ in range(3):
            img = Image.new('RGB', (300, 300), color='white')
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='JPEG')
            img_bytes.seek(0)
            
            files = {"file": ("test.jpg", img_bytes, "image/jpeg")}
            data = {"min_confidence": 0.9, "auto_save": True}
            
            self.client.post("/detect", files=files, data=data, catch_response=True)
    
    @task(3)
    def create_many_persons(self):
        """Create multiple persons."""
        for i in range(5):
            person_data = {"name": f"Batch User {random.randint(1000, 9999)}"}
            self.client.post("/persons", json=person_data)


class QuickUser(HttpUser):
    """User performing only quick read operations."""
    tasks = [QuickUserBehavior]
    wait_time = between(0.5, 1.5)
    weight = 3  # 3x more common than heavy users


class HeavyUser(HttpUser):
    """User performing heavy operations."""
    tasks = [HeavyUserBehavior]
    wait_time = between(3, 6)
    weight = 1


class SpikeTestUser(HttpUser):
    """
    User for spike testing - sudden bursts of traffic.
    
    Run with:
        locust -f tests/locustfile.py --host=http://localhost:8000 --users=100 --spawn-rate=20
    """
    wait_time = between(0.1, 0.5)
    
    @task(20)
    def rapid_health_checks(self):
        """Rapid fire health checks."""
        self.client.get("/health")
    
    @task(5)
    def rapid_stats(self):
        """Rapid fire stats requests."""
        self.client.get("/stats")
    
    @task(1)
    def rapid_person_list(self):
        """Rapid fire person listings."""
        self.client.get("/persons?limit=10")


# Load test scenarios documentation
LOAD_TEST_SCENARIOS = """
Load Testing Scenarios:

1. Normal Load (Baseline):
   locust -f tests/locustfile.py --host=http://localhost:8000 --users=10 --spawn-rate=2 --run-time=5m
   
   Expected: < 200ms response time for 95th percentile

2. High Load:
   locust -f tests/locustfile.py --host=http://localhost:8000 --users=50 --spawn-rate=5 --run-time=10m
   
   Expected: < 500ms response time for 95th percentile

3. Spike Test:
   locust -f tests/locustfile.py --host=http://localhost:8000 --users=100 --spawn-rate=20 --run-time=2m
   
   Expected: System remains stable, no crashes

4. Endurance Test:
   locust -f tests/locustfile.py --host=http://localhost:8000 --users=20 --spawn-rate=2 --run-time=30m
   
   Expected: No memory leaks, stable performance

5. Mixed Workload:
   locust -f tests/locustfile.py --host=http://localhost:8000 --users=30 --spawn-rate=3 --run-time=10m
   
   Expected: < 300ms response time for 90th percentile

Note: Update --host and API key as needed for your environment.
"""

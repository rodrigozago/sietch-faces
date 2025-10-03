"""
Test script for internal API endpoints.
Run this after starting the FastAPI server to verify internal endpoints.
"""
import requests
import base64
import json
from pathlib import Path

BASE_URL = "http://localhost:8000"
INTERNAL_API_KEY = "your-super-secret-internal-api-key-change-this"

headers = {
    "X-Internal-Token": INTERNAL_API_KEY
}


def test_register_user():
    """Test user registration with face"""
    print("\n🧪 Testing: Register User with Face")
    
    # You need a base64 encoded face image
    # For testing, use a sample image from uploads/
    image_path = Path("uploads")
    sample_images = list(image_path.glob("*.jp*g"))
    
    if not sample_images:
        print("❌ No sample images found in uploads/")
        return None
    
    # Read and encode image
    with open(sample_images[0], "rb") as f:
        image_data = base64.b64encode(f.read()).decode()
        face_image_base64 = f"data:image/jpeg;base64,{image_data}"
    
    data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "Test123456!",
        "face_image_base64": face_image_base64
    }
    
    response = requests.post(
        f"{BASE_URL}/internal/auth/register",
        headers=headers,
        data=data
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ User registered: {result['username']} (ID: {result['id']})")
        return result['id']
    elif response.status_code == 400 and "already registered" in response.text:
        print("⚠️  User already exists, using existing user")
        # Try to login to get user_id
        return test_validate_credentials()
    else:
        print(f"❌ Registration failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return None


def test_validate_credentials():
    """Test credential validation"""
    print("\n🧪 Testing: Validate Credentials")
    
    data = {
        "email": "test@example.com",
        "password": "Test123456!"
    }
    
    response = requests.post(
        f"{BASE_URL}/internal/auth/validate",
        headers=headers,
        data=data
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Credentials valid: {result['username']} (ID: {result['id']})")
        return result['id']
    else:
        print(f"❌ Validation failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return None


def test_upload_photo(user_id):
    """Test photo upload and processing"""
    print("\n🧪 Testing: Upload and Process Photo")
    
    if not user_id:
        print("❌ No user_id provided")
        return None
    
    image_path = Path("uploads")
    sample_images = list(image_path.glob("*.jp*g"))
    
    if not sample_images:
        print("❌ No sample images found in uploads/")
        return None
    
    with open(sample_images[0], "rb") as f:
        files = {"file": f}
        data = {"user_id": user_id}
        
        response = requests.post(
            f"{BASE_URL}/internal/photos/process",
            headers=headers,
            files=files,
            data=data
        )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Photo uploaded: ID {result['id']}")
        print(f"   Faces detected: {len(result['faces'])}")
        return result['id']
    else:
        print(f"❌ Upload failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return None


def test_get_user_photos(user_id):
    """Test getting user photos"""
    print("\n🧪 Testing: Get User Photos")
    
    if not user_id:
        print("❌ No user_id provided")
        return
    
    response = requests.get(
        f"{BASE_URL}/internal/users/{user_id}/photos",
        headers=headers
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Retrieved {len(result['photos'])} photos")
        for photo in result['photos'][:3]:
            print(f"   - Photo ID: {photo['id']} ({photo['image_path']})")
    else:
        print(f"❌ Failed: {response.status_code}")
        print(f"   Response: {response.text}")


def test_get_user_faces(user_id):
    """Test getting user faces"""
    print("\n🧪 Testing: Get User Faces")
    
    if not user_id:
        print("❌ No user_id provided")
        return
    
    response = requests.get(
        f"{BASE_URL}/internal/users/{user_id}/faces",
        headers=headers
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Retrieved {len(result['faces'])} faces")
        for face in result['faces'][:3]:
            print(f"   - Face ID: {face['id']}, Person: {face['person_id']}")
    else:
        print(f"❌ Failed: {response.status_code}")
        print(f"   Response: {response.text}")


def test_get_unclaimed_matches(user_id):
    """Test getting unclaimed matches"""
    print("\n🧪 Testing: Get Unclaimed Matches")
    
    if not user_id:
        print("❌ No user_id provided")
        return []
    
    response = requests.get(
        f"{BASE_URL}/internal/users/{user_id}/unclaimed-matches",
        headers=headers
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Found {len(result)} unclaimed matches")
        for match in result[:3]:
            print(f"   - Person {match['person_id']}: {match['face_count']} faces, "
                  f"confidence: {match['avg_confidence']:.2f}")
        return [m['person_id'] for m in result]
    else:
        print(f"❌ Failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return []


def test_claim_persons(user_id, person_ids):
    """Test claiming person clusters"""
    print("\n🧪 Testing: Claim Person Clusters")
    
    if not user_id:
        print("❌ No user_id provided")
        return
    
    if not person_ids:
        print("⚠️  No person IDs to claim")
        return
    
    data = {"person_ids": person_ids[:2]}  # Claim first 2
    
    response = requests.post(
        f"{BASE_URL}/internal/users/{user_id}/claim",
        headers=headers,
        json=data
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ {result['message']}")
        print(f"   Merged to person ID: {result.get('merged_to_person_id')}")
    else:
        print(f"❌ Failed: {response.status_code}")
        print(f"   Response: {response.text}")


def test_get_user_stats(user_id):
    """Test getting user statistics"""
    print("\n🧪 Testing: Get User Statistics")
    
    if not user_id:
        print("❌ No user_id provided")
        return
    
    response = requests.get(
        f"{BASE_URL}/internal/users/{user_id}/stats",
        headers=headers
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ User Statistics:")
        print(f"   - Total photos uploaded: {result['total_photos_uploaded']}")
        print(f"   - Photos with user face: {result['photos_with_user_face']}")
        print(f"   - Total faces detected: {result['total_faces_detected']}")
        print(f"   - Unique people: {result['unique_people_detected']}")
        print(f"   - Recent uploads: {len(result['recent_uploads'])}")
    else:
        print(f"❌ Failed: {response.status_code}")
        print(f"   Response: {response.text}")


def test_invalid_api_key():
    """Test with invalid API key"""
    print("\n🧪 Testing: Invalid API Key")
    
    invalid_headers = {"X-Internal-Token": "wrong-key"}
    
    response = requests.get(
        f"{BASE_URL}/internal/users/test/stats",
        headers=invalid_headers
    )
    
    if response.status_code == 401:
        print("✅ Correctly rejected invalid API key")
    else:
        print(f"❌ Unexpected response: {response.status_code}")


def main():
    """Run all tests"""
    print("=" * 60)
    print("🚀 Internal API Endpoints Test Suite")
    print("=" * 60)
    
    # Test 1: Invalid API key
    test_invalid_api_key()
    
    # Test 2: Register user (or get existing)
    user_id = test_register_user()
    
    if not user_id:
        # Try validation if registration failed
        user_id = test_validate_credentials()
    
    if not user_id:
        print("\n❌ Cannot proceed without user_id")
        return
    
    # Test 3: Upload photo
    photo_id = test_upload_photo(user_id)
    
    # Test 4: Get user photos
    test_get_user_photos(user_id)
    
    # Test 5: Get user faces
    test_get_user_faces(user_id)
    
    # Test 6: Get unclaimed matches
    person_ids = test_get_unclaimed_matches(user_id)
    
    # Test 7: Claim persons (if any)
    if person_ids:
        test_claim_persons(user_id, person_ids)
    
    # Test 8: Get stats
    test_get_user_stats(user_id)
    
    print("\n" + "=" * 60)
    print("✅ Test suite completed!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Cannot connect to FastAPI server")
        print("   Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

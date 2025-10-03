# API Usage Examples

## Upload an Image

```bash
curl -X POST "http://localhost:8000/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/image.jpg"
```

**Response:**
```json
{
  "filename": "uuid-generated-name.jpg",
  "faces_detected": 2,
  "faces": [
    {
      "id": 1,
      "image_path": "uploads/uuid-generated-name.jpg",
      "x": 100,
      "y": 150,
      "width": 200,
      "height": 250,
      "confidence": 0.998,
      "person_id": null,
      "created_at": "2025-10-02T10:30:00"
    }
  ]
}
```

## Identify a Face

```bash
curl -X POST "http://localhost:8000/identify" \
  -H "Content-Type: application/json" \
  -d '{
    "face_id": 1,
    "name": "John Doe",
    "auto_identify_similar": true
  }'
```

**Response:**
```json
{
  "person_id": 1,
  "name": "John Doe",
  "identified_faces": 5,
  "faces": [...]
}
```

## Get Person Information

```bash
curl -X GET "http://localhost:8000/person/1"
```

**Response:**
```json
{
  "id": 1,
  "name": "John Doe",
  "face_count": 5,
  "created_at": "2025-10-02T10:30:00",
  "updated_at": "2025-10-02T10:35:00",
  "faces": [...]
}
```

## Get Clusters

```bash
curl -X GET "http://localhost:8000/clusters?only_unidentified=true"
```

**Response:**
```json
{
  "total_clusters": 3,
  "clusters": [
    {
      "cluster_id": 0,
      "face_count": 8,
      "faces": [...]
    },
    {
      "cluster_id": 1,
      "face_count": 5,
      "faces": [...]
    }
  ]
}
```

## Get Statistics

```bash
curl -X GET "http://localhost:8000/stats"
```

**Response:**
```json
{
  "total_faces": 50,
  "identified_faces": 30,
  "unidentified_faces": 20,
  "total_persons": 8,
  "total_images": 25
}
```

## Delete a Face

```bash
curl -X DELETE "http://localhost:8000/stats/face/1"
```

**Response:**
```json
{
  "message": "Face 1 deleted successfully"
}
```

## List All Persons

```bash
curl -X GET "http://localhost:8000/person?skip=0&limit=10"
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "John Doe",
    "face_count": 5,
    "created_at": "2025-10-02T10:30:00",
    "updated_at": "2025-10-02T10:35:00"
  }
]
```

## Python Example

```python
import requests

# Upload image
with open('photo.jpg', 'rb') as f:
    files = {'file': f}
    response = requests.post('http://localhost:8000/upload', files=files)
    data = response.json()
    print(f"Detected {data['faces_detected']} faces")

# Identify first face
if data['faces']:
    face_id = data['faces'][0]['id']
    identify_data = {
        'face_id': face_id,
        'name': 'John Doe',
        'auto_identify_similar': True
    }
    response = requests.post('http://localhost:8000/identify', json=identify_data)
    result = response.json()
    print(f"Identified {result['identified_faces']} faces as {result['name']}")

# Get clusters
response = requests.get('http://localhost:8000/clusters')
clusters = response.json()
print(f"Found {clusters['total_clusters']} clusters")
```

## Testing with Swagger UI

The easiest way to test the API is through the interactive Swagger UI documentation:

1. Start the API: `uvicorn app.main:app --reload`
2. Open browser: `http://localhost:8000/docs`
3. Try out each endpoint directly from the browser

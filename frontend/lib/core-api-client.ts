/**
 * Core API Client
 * 
 * HTTP client for communicating with the FastAPI Core microservice.
 * Handles face detection, similarity search, person management, and clustering.
 */

const CORE_API_URL = process.env.CORE_API_URL || 'http://localhost:8000';

// ============================================================================
// Types - Match Core API schemas
// ============================================================================

export interface BoundingBox {
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface DetectedFace {
  bbox: BoundingBox;
  confidence: number;
  embedding: number[]; // 512D array
}

export interface DetectFacesResponse {
  faces: DetectedFace[];
  image_path: string;
  processing_time_ms: number;
}

export interface FaceMatch {
  face_id: number;
  person_id: number;
  similarity: number;
  image_path: string;
  bbox: BoundingBox;
  confidence: number;
}

export interface SimilaritySearchResponse {
  matches: FaceMatch[];
  query_embedding_size: number;
  search_time_ms: number;
}

export interface Person {
  id: number;
  name: string;
  metadata: Record<string, any>;
  face_count: number;
  created_at: string;
  updated_at: string;
}

export interface Face {
  id: number;
  person_id: number;
  image_path: string;
  bbox: BoundingBox;
  confidence: number;
  detected_at: string;
  metadata: Record<string, any>;
}

export interface PersonWithFaces {
  person: Person;
  faces: Face[];
}

export interface ClusterResult {
  cluster_id: number;
  face_ids: number[];
  face_count: number;
  avg_similarity: number;
  representative_face_id: number;
}

export interface ClusterResponse {
  clusters: ClusterResult[];
  noise_face_ids: number[];
  total_clusters: number;
  processing_time_ms: number;
}

export interface SystemStats {
  total_persons: number;
  total_faces: number;
  total_unclustered_faces: number;
  avg_faces_per_person: number;
  largest_person_id: number;
  largest_person_face_count: number;
  storage_used_mb: number | null;
}

export interface HealthResponse {
  status: string;
  version: string;
  database: string;
  models_loaded: boolean;
}

// ============================================================================
// Core API Client Class
// ============================================================================

class CoreAPIClient {
  private baseUrl: string;

  constructor(baseUrl: string = CORE_API_URL) {
    this.baseUrl = baseUrl;
  }

  /**
   * Health check
   */
  async health(): Promise<HealthResponse> {
    const response = await fetch(`${this.baseUrl}/health`);
    if (!response.ok) {
      throw new Error(`Health check failed: ${response.statusText}`);
    }
    return response.json();
  }

  /**
   * Get system statistics
   */
  async stats(): Promise<SystemStats> {
    const response = await fetch(`${this.baseUrl}/stats`);
    if (!response.ok) {
      throw new Error(`Failed to get stats: ${response.statusText}`);
    }
    return response.json();
  }

  /**
   * Detect faces in an image
   * 
   * @param file - Image file (File or Blob)
   * @param minConfidence - Minimum detection confidence (0.0-1.0)
   * @param autoSave - Automatically save faces to database
   */
  async detectFaces(
    file: File | Blob,
    minConfidence: number = 0.9,
    autoSave: boolean = true
  ): Promise<DetectFacesResponse> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('min_confidence', minConfidence.toString());
    formData.append('auto_save', autoSave.toString());

    const response = await fetch(`${this.baseUrl}/detect`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || `Face detection failed: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Search for similar faces using embedding vector
   * 
   * @param embedding - 512D embedding vector
   * @param threshold - Similarity threshold (0.0-1.0)
   * @param limit - Maximum number of results
   */
  async searchSimilar(
    embedding: number[],
    threshold: number = 0.6,
    limit: number = 10
  ): Promise<SimilaritySearchResponse> {
    const response = await fetch(`${this.baseUrl}/search`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        embedding,
        threshold,
        limit,
      }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || `Similarity search failed: ${response.statusText}`);
    }

    return response.json();
  }

  // ============================================================================
  // Person Management
  // ============================================================================

  /**
   * List all persons
   */
  async listPersons(skip: number = 0, limit: number = 100): Promise<Person[]> {
    const response = await fetch(
      `${this.baseUrl}/persons?skip=${skip}&limit=${limit}`
    );

    if (!response.ok) {
      throw new Error(`Failed to list persons: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Create a new person
   * 
   * @param name - Person's name
   * @param metadata - Additional metadata (e.g., app_user_id)
   */
  async createPerson(
    name: string,
    metadata: Record<string, any> = {}
  ): Promise<Person> {
    const response = await fetch(`${this.baseUrl}/persons`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        name,
        metadata,
      }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || `Failed to create person: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Get person details with all faces
   */
  async getPerson(personId: number): Promise<PersonWithFaces> {
    const response = await fetch(`${this.baseUrl}/persons/${personId}`);

    if (!response.ok) {
      if (response.status === 404) {
        throw new Error('Person not found');
      }
      throw new Error(`Failed to get person: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Update person
   */
  async updatePerson(
    personId: number,
    name?: string,
    metadata?: Record<string, any>
  ): Promise<Person> {
    const body: any = {};
    if (name !== undefined) body.name = name;
    if (metadata !== undefined) body.metadata = metadata;

    const response = await fetch(`${this.baseUrl}/persons/${personId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || `Failed to update person: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Delete person and all associated faces
   */
  async deletePerson(personId: number): Promise<{ message: string }> {
    const response = await fetch(`${this.baseUrl}/persons/${personId}`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || `Failed to delete person: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Merge multiple persons into one
   * 
   * @param sourcePersonIds - IDs of persons to merge
   * @param targetPersonId - ID of person to merge into
   * @param keepName - Optional name to keep
   */
  async mergePersons(
    sourcePersonIds: number[],
    targetPersonId: number,
    keepName?: string
  ): Promise<{
    merged_person_id: number;
    faces_transferred: number;
    deleted_person_ids: number[];
    message: string;
  }> {
    const response = await fetch(`${this.baseUrl}/persons/merge`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        source_person_ids: sourcePersonIds,
        target_person_id: targetPersonId,
        keep_name: keepName,
      }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || `Failed to merge persons: ${response.statusText}`);
    }

    return response.json();
  }

  // ============================================================================
  // Face Management
  // ============================================================================

  /**
   * List faces, optionally filtered by person
   */
  async listFaces(
    personId?: number,
    skip: number = 0,
    limit: number = 100
  ): Promise<Face[]> {
    let url = `${this.baseUrl}/faces?skip=${skip}&limit=${limit}`;
    if (personId !== undefined) {
      url += `&person_id=${personId}`;
    }

    const response = await fetch(url);

    if (!response.ok) {
      throw new Error(`Failed to list faces: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Get face details including embedding
   */
  async getFace(faceId: number): Promise<Face> {
    const response = await fetch(`${this.baseUrl}/faces/${faceId}`);

    if (!response.ok) {
      if (response.status === 404) {
        throw new Error('Face not found');
      }
      throw new Error(`Failed to get face: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Delete a face
   */
  async deleteFace(faceId: number): Promise<{ message: string }> {
    const response = await fetch(`${this.baseUrl}/faces/${faceId}`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || `Failed to delete face: ${response.statusText}`);
    }

    return response.json();
  }

  // ============================================================================
  // Clustering
  // ============================================================================

  /**
   * Cluster faces using DBSCAN
   * 
   * @param faceIds - Optional array of face IDs to cluster (empty = all faces)
   * @param eps - DBSCAN epsilon parameter (distance threshold)
   * @param minSamples - Minimum cluster size
   */
  async clusterFaces(
    faceIds: number[] = [],
    eps: number = 0.4,
    minSamples: number = 2
  ): Promise<ClusterResponse> {
    const response = await fetch(`${this.baseUrl}/cluster`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        face_ids: faceIds,
        eps,
        min_samples: minSamples,
      }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || `Clustering failed: ${response.statusText}`);
    }

    return response.json();
  }
}

// ============================================================================
// Export singleton instance
// ============================================================================

export const coreAPI = new CoreAPIClient();
export default coreAPI;

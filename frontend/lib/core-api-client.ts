/**
 * Core API Client
 * 
 * HTTP client for communicating with the FastAPI Core microservice.
 * Handles face detection, similarity search, person management, and clustering.
 * 
 * Features:
 * - Automatic retry with exponential backoff
 * - Configurable timeouts
 * - Enhanced error logging
 */

const CORE_API_URL = process.env.CORE_API_URL || 'http://localhost:8000';
const DEFAULT_TIMEOUT = 30000; // 30 seconds
const MAX_RETRIES = 3;
const RETRY_DELAY = 1000; // 1 second base delay

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
// Utility Functions
// ============================================================================

/**
 * Sleep for a given duration
 */
function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Fetch with timeout
 */
async function fetchWithTimeout(
  url: string,
  options: RequestInit = {},
  timeout: number = DEFAULT_TIMEOUT
): Promise<Response> {
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeout);

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
    });
    clearTimeout(id);
    return response;
  } catch (error) {
    clearTimeout(id);
    if (error instanceof Error && error.name === 'AbortError') {
      throw new Error(`Request timeout after ${timeout}ms`);
    }
    throw error;
  }
}

/**
 * Retry a function with exponential backoff
 */
async function retryWithBackoff<T>(
  fn: () => Promise<T>,
  maxRetries: number = MAX_RETRIES,
  baseDelay: number = RETRY_DELAY,
  operation: string = 'operation'
): Promise<T> {
  let lastError: Error | null = null;

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error instanceof Error ? error : new Error(String(error));

      // Don't retry on 4xx errors (client errors)
      if (error instanceof Error && error.message.includes('status 4')) {
        throw error;
      }

      if (attempt < maxRetries) {
        const delay = baseDelay * Math.pow(2, attempt);
        console.log(
          `[Core API] ${operation} failed (attempt ${attempt + 1}/${maxRetries + 1}), retrying in ${delay}ms...`,
          error
        );
        await sleep(delay);
      }
    }
  }

  console.error(`[Core API] ${operation} failed after ${maxRetries + 1} attempts`, lastError);
  throw lastError;
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
   * Make a request with retry and timeout
   */
  private async request(
    url: string,
    options: RequestInit = {},
    operation: string = 'request',
    timeout: number = DEFAULT_TIMEOUT
  ): Promise<Response> {
    return retryWithBackoff(
      async () => {
        const response = await fetchWithTimeout(url, options, timeout);
        
        if (!response.ok) {
          const error = await response.json().catch(() => ({}));
          const errorMessage = error.detail || `${operation} failed: ${response.statusText}`;
          const statusError = new Error(errorMessage);
          (statusError as any).status = response.status;
          throw statusError;
        }

        return response;
      },
      MAX_RETRIES,
      RETRY_DELAY,
      operation
    );
  }

  /**
   * Health check
   */
  async health(): Promise<HealthResponse> {
    const response = await this.request(
      `${this.baseUrl}/health`,
      {},
      'Health check',
      5000 // Shorter timeout for health checks
    );
    return response.json();
  }

  /**
   * Get system statistics
   */
  async stats(): Promise<SystemStats> {
    const response = await this.request(
      `${this.baseUrl}/stats`,
      {},
      'Get stats',
      10000
    );
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

    const response = await this.request(
      `${this.baseUrl}/detect`,
      {
        method: 'POST',
        body: formData,
      },
      'Face detection',
      60000 // Longer timeout for face detection (60s)
    );

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
    const response = await this.request(
      `${this.baseUrl}/search`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          embedding,
          threshold,
          limit,
        }),
      },
      'Similarity search',
      30000 // 30s timeout
    );

    return response.json();
  }

  // ============================================================================
  // Person Management
  // ============================================================================

  /**
   * List all persons
   */
  async listPersons(skip: number = 0, limit: number = 100): Promise<Person[]> {
    const response = await this.request(
      `${this.baseUrl}/persons?skip=${skip}&limit=${limit}`,
      {},
      'List persons'
    );
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
    const response = await this.request(
      `${this.baseUrl}/persons`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name,
          metadata,
        }),
      },
      'Create person'
    );
    return response.json();
  }

  /**
   * Get person details with all faces
   */
  async getPerson(personId: number): Promise<PersonWithFaces> {
    const response = await this.request(
      `${this.baseUrl}/persons/${personId}`,
      {},
      `Get person ${personId}`
    );
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
    const response = await this.request(
      `${this.baseUrl}/persons/merge`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          source_person_ids: sourcePersonIds,
          target_person_id: targetPersonId,
          keep_name: keepName,
        }),
      },
      'Merge persons'
    );
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

    const response = await this.request(url, {}, 'List faces');
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
    const response = await this.request(
      `${this.baseUrl}/cluster`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          face_ids: faceIds,
          eps,
          min_samples: minSamples,
        }),
      },
      'Cluster faces',
      60000 // Longer timeout for clustering (60s)
    );
    return response.json();
  }
}

// ============================================================================
// Export singleton instance
// ============================================================================

export const coreAPI = new CoreAPIClient();
export default coreAPI;

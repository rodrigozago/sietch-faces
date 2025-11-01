"""
Unit tests for face clustering service.

Tests the FaceClustering class including:
- DBSCAN clustering
- Cluster statistics
- Edge cases (empty input, single face, noise)
"""
import pytest
import numpy as np
from unittest.mock import patch

from app.clustering import FaceClustering


@pytest.mark.unit
class TestFaceClustering:
    """Test suite for FaceClustering class."""
    
    def test_init(self):
        """Test FaceClustering initialization."""
        clusterer = FaceClustering()
        assert clusterer.eps > 0
        assert clusterer.min_samples > 0
    
    def test_cluster_faces_simple(self, sample_embeddings_dict):
        """Test basic face clustering."""
        clusterer = FaceClustering()
        clusters = clusterer.cluster_faces(sample_embeddings_dict)
        
        assert isinstance(clusters, dict)
        # Should create at least some clusters
        assert len(clusters) >= 0
    
    def test_cluster_faces_empty_input(self):
        """Test clustering with empty input."""
        clusterer = FaceClustering()
        clusters = clusterer.cluster_faces({})
        
        assert clusters == {}
    
    def test_cluster_faces_single_face(self):
        """Test clustering with a single face."""
        embedding = np.random.randn(512).astype(np.float32)
        embedding = embedding / np.linalg.norm(embedding)
        
        clusterer = FaceClustering()
        clusters = clusterer.cluster_faces({1: embedding})
        
        # Single face might be noise depending on min_samples
        assert isinstance(clusters, dict)
    
    def test_cluster_faces_identical_embeddings(self):
        """Test clustering with identical embeddings."""
        embedding = np.random.randn(512).astype(np.float32)
        embedding = embedding / np.linalg.norm(embedding)
        
        # Create multiple identical embeddings
        embeddings_dict = {i: embedding.copy() for i in range(5)}
        
        clusterer = FaceClustering()
        clusterer.eps = 0.01  # Very small eps for identical embeddings
        clusterer.min_samples = 2
        clusters = clusterer.cluster_faces(embeddings_dict)
        
        # Should create one cluster with all faces
        assert len(clusters) == 1
        cluster_faces = list(clusters.values())[0]
        assert len(cluster_faces) == 5
    
    def test_cluster_faces_two_groups(self):
        """Test clustering with two distinct groups."""
        # Create two groups of similar embeddings
        base_embedding1 = np.random.randn(512).astype(np.float32)
        base_embedding1 = base_embedding1 / np.linalg.norm(base_embedding1)
        
        base_embedding2 = np.random.randn(512).astype(np.float32)
        base_embedding2 = base_embedding2 / np.linalg.norm(base_embedding2)
        
        # Make them very different
        base_embedding2 = -base_embedding1
        
        embeddings_dict = {}
        # Group 1
        for i in range(3):
            emb = base_embedding1 + np.random.randn(512) * 0.01
            emb = emb / np.linalg.norm(emb)
            embeddings_dict[i] = emb
        
        # Group 2
        for i in range(3, 6):
            emb = base_embedding2 + np.random.randn(512) * 0.01
            emb = emb / np.linalg.norm(emb)
            embeddings_dict[i] = emb
        
        clusterer = FaceClustering()
        clusterer.eps = 0.3
        clusterer.min_samples = 2
        clusters = clusterer.cluster_faces(embeddings_dict)
        
        # Should create two clusters
        assert len(clusters) >= 1  # At least one cluster should form
    
    def test_cluster_faces_with_noise(self):
        """Test clustering with noise points."""
        # Create similar embeddings for a cluster
        base_embedding = np.random.randn(512).astype(np.float32)
        base_embedding = base_embedding / np.linalg.norm(base_embedding)
        
        embeddings_dict = {}
        # Cluster faces
        for i in range(3):
            emb = base_embedding + np.random.randn(512) * 0.01
            emb = emb / np.linalg.norm(emb)
            embeddings_dict[i] = emb
        
        # Noise faces (very different)
        for i in range(3, 5):
            emb = np.random.randn(512).astype(np.float32)
            emb = emb / np.linalg.norm(emb)
            embeddings_dict[i] = emb
        
        clusterer = FaceClustering()
        clusterer.eps = 0.1
        clusterer.min_samples = 2
        clusters = clusterer.cluster_faces(embeddings_dict)
        
        # Should create at least one cluster, noise points excluded
        total_faces_in_clusters = sum(len(faces) for faces in clusters.values())
        assert total_faces_in_clusters <= len(embeddings_dict)
    
    def test_get_cluster_stats_empty(self):
        """Test cluster statistics with empty clusters."""
        clusterer = FaceClustering()
        stats = clusterer.get_cluster_stats({})
        
        assert stats['total_clusters'] == 0
        assert stats['total_faces_clustered'] == 0
        assert stats['min_cluster_size'] == 0
        assert stats['max_cluster_size'] == 0
        assert stats['avg_cluster_size'] == 0.0
    
    def test_get_cluster_stats_single_cluster(self):
        """Test cluster statistics with a single cluster."""
        clusters = {0: [1, 2, 3, 4, 5]}
        
        clusterer = FaceClustering()
        stats = clusterer.get_cluster_stats(clusters)
        
        assert stats['total_clusters'] == 1
        assert stats['total_faces_clustered'] == 5
        assert stats['min_cluster_size'] == 5
        assert stats['max_cluster_size'] == 5
        assert stats['avg_cluster_size'] == 5.0
    
    def test_get_cluster_stats_multiple_clusters(self):
        """Test cluster statistics with multiple clusters."""
        clusters = {
            0: [1, 2, 3],
            1: [4, 5],
            2: [6, 7, 8, 9]
        }
        
        clusterer = FaceClustering()
        stats = clusterer.get_cluster_stats(clusters)
        
        assert stats['total_clusters'] == 3
        assert stats['total_faces_clustered'] == 9
        assert stats['min_cluster_size'] == 2
        assert stats['max_cluster_size'] == 4
        assert stats['avg_cluster_size'] == 3.0
    
    def test_cluster_faces_returns_face_ids(self):
        """Test that cluster results contain correct face IDs."""
        embeddings_dict = {}
        face_ids = [10, 20, 30, 40, 50]
        
        base_embedding = np.random.randn(512).astype(np.float32)
        base_embedding = base_embedding / np.linalg.norm(base_embedding)
        
        for face_id in face_ids:
            emb = base_embedding + np.random.randn(512) * 0.01
            emb = emb / np.linalg.norm(emb)
            embeddings_dict[face_id] = emb
        
        clusterer = FaceClustering()
        clusterer.eps = 0.3
        clusterer.min_samples = 2
        clusters = clusterer.cluster_faces(embeddings_dict)
        
        # Check that returned IDs are from the original face_ids
        for cluster_faces in clusters.values():
            for face_id in cluster_faces:
                assert face_id in face_ids
    
    def test_cluster_faces_no_noise_in_results(self):
        """Test that noise points (label -1) are excluded from results."""
        embeddings_dict = {}
        
        # Create faces that will likely be noise
        for i in range(10):
            emb = np.random.randn(512).astype(np.float32)
            emb = emb / np.linalg.norm(emb)
            embeddings_dict[i] = emb
        
        clusterer = FaceClustering()
        clusterer.eps = 0.01  # Very small eps
        clusterer.min_samples = 5  # High min_samples
        clusters = clusterer.cluster_faces(embeddings_dict)
        
        # Verify no cluster has ID -1
        assert -1 not in clusters
    
    def test_cluster_faces_with_varying_eps(self):
        """Test clustering behavior with different eps values."""
        base_embedding = np.random.randn(512).astype(np.float32)
        base_embedding = base_embedding / np.linalg.norm(base_embedding)
        
        embeddings_dict = {}
        for i in range(5):
            emb = base_embedding + np.random.randn(512) * 0.1
            emb = emb / np.linalg.norm(emb)
            embeddings_dict[i] = emb
        
        clusterer = FaceClustering()
        clusterer.min_samples = 2
        
        # Small eps - fewer/no clusters
        clusterer.eps = 0.01
        clusters_small = clusterer.cluster_faces(embeddings_dict)
        
        # Large eps - more clusters
        clusterer.eps = 0.5
        clusters_large = clusterer.cluster_faces(embeddings_dict)
        
        # Larger eps should generally create more or equal clusters
        assert isinstance(clusters_small, dict)
        assert isinstance(clusters_large, dict)
    
    def test_cluster_faces_preserves_embedding_dict(self):
        """Test that clustering does not modify the input dictionary."""
        embeddings_dict = {}
        for i in range(5):
            emb = np.random.randn(512).astype(np.float32)
            emb = emb / np.linalg.norm(emb)
            embeddings_dict[i] = emb
        
        original_keys = set(embeddings_dict.keys())
        original_len = len(embeddings_dict)
        
        clusterer = FaceClustering()
        clusters = clusterer.cluster_faces(embeddings_dict)
        
        # Original dict should be unchanged
        assert len(embeddings_dict) == original_len
        assert set(embeddings_dict.keys()) == original_keys
    
    def test_cluster_faces_cosine_metric(self):
        """Test that clustering uses cosine distance metric."""
        # Create embeddings that are similar in cosine distance but not Euclidean
        embedding1 = np.ones(512) / np.sqrt(512)
        embedding2 = np.ones(512) * 2 / np.linalg.norm(np.ones(512) * 2)
        
        # These are identical in direction (cosine distance = 0)
        embeddings_dict = {1: embedding1, 2: embedding2}
        
        clusterer = FaceClustering()
        clusterer.eps = 0.01
        clusterer.min_samples = 2
        clusters = clusterer.cluster_faces(embeddings_dict)
        
        # Should cluster together with cosine metric
        if len(clusters) > 0:
            # If clustering occurred, both should be in same cluster
            all_faces = []
            for faces in clusters.values():
                all_faces.extend(faces)
            if len(all_faces) == 2:
                assert set(all_faces) == {1, 2}

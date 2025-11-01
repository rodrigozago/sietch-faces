"""Face clustering module using DBSCAN algorithm for grouping similar faces."""

import numpy as np
from sklearn.cluster import DBSCAN
from typing import List, Dict
import logging

from app.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


class FaceClustering:
    """
    Face clustering using DBSCAN (Density-Based Spatial Clustering of Applications with Noise).
    
    This class automatically groups similar faces into clusters based on their embedding
    similarity, useful for identifying the same person across multiple photos.
    
    Attributes:
        eps (float): Maximum distance between two samples to be considered in the same neighborhood.
        min_samples (int): Minimum number of samples in a neighborhood for a point to be a core point.
        
    Example:
        >>> clusterer = FaceClustering()
        >>> embeddings = {1: emb1, 2: emb2, 3: emb3}
        >>> clusters = clusterer.cluster_faces(embeddings)
        >>> print(f"Found {len(clusters)} clusters")
    """
    
    def __init__(self):
        """Initialize FaceClustering with DBSCAN parameters from configuration."""
        self.eps = settings.dbscan_eps
        self.min_samples = settings.dbscan_min_samples
    
    def cluster_faces(self, embeddings_dict: Dict[int, np.ndarray]) -> Dict[int, List[int]]:
        """
        Cluster faces based on embedding similarity using DBSCAN algorithm.
        
        Groups faces with similar embeddings into clusters, representing the same person.
        Faces that don't fit into any cluster (noise) are excluded from the results.
        
        Args:
            embeddings_dict (Dict[int, np.ndarray]): Dictionary mapping face IDs to their embeddings.
            
        Returns:
            Dict[int, List[int]]: Dictionary mapping cluster IDs to lists of face IDs.
                Cluster ID -1 (noise) is filtered out.
                
        Note:
            Uses cosine distance metric for similarity comparison.
            Faces with label -1 are considered noise and not included in any cluster.
            
        Example:
            >>> clusterer = FaceClustering()
            >>> clusters = clusterer.cluster_faces({1: emb1, 2: emb2, 3: emb3})
            >>> for cluster_id, face_ids in clusters.items():
            ...     print(f"Cluster {cluster_id}: {len(face_ids)} faces")
        """
        if not embeddings_dict:
            logger.warning("Empty embeddings dictionary provided for clustering")
            return {}
        
        # Extract face IDs and embeddings
        face_ids = list(embeddings_dict.keys())
        embeddings = np.array([embeddings_dict[fid] for fid in face_ids])
        
        logger.info(f"Clustering {len(face_ids)} faces with eps={self.eps}, min_samples={self.min_samples}")
        
        # DBSCAN clustering with cosine distance
        # eps controls the maximum distance between two samples
        # min_samples is the minimum cluster size
        clustering = DBSCAN(
            eps=self.eps,
            min_samples=self.min_samples,
            metric='cosine'
        )
        
        labels = clustering.fit_predict(embeddings)
        
        # Organize results by cluster
        clusters = {}
        noise_count = 0
        
        for face_id, label in zip(face_ids, labels):
            # label = -1 means noise (not assigned to any cluster)
            if label == -1:
                noise_count += 1
                continue
            
            if label not in clusters:
                clusters[label] = []
            
            clusters[label].append(face_id)
        
        logger.info(f"Created {len(clusters)} clusters, {noise_count} noise faces")
        return clusters
    
    def get_cluster_stats(self, clusters: Dict[int, List[int]]) -> Dict[str, float]:
        """
        Calculate statistical metrics about face clusters.
        
        Provides insights into cluster distribution, including total clusters,
        total faces, and cluster size statistics.
        
        Args:
            clusters (Dict[int, List[int]]): Dictionary of cluster_id to face_ids lists.
            
        Returns:
            Dict[str, float]: Dictionary containing:
                - total_clusters: Number of clusters
                - total_faces_clustered: Total faces in all clusters
                - min_cluster_size: Smallest cluster size
                - max_cluster_size: Largest cluster size
                - avg_cluster_size: Average cluster size
                
        Example:
            >>> stats = clusterer.get_cluster_stats(clusters)
            >>> print(f"Average cluster size: {stats['avg_cluster_size']:.1f}")
        """
        total_clusters = len(clusters)
        total_faces_clustered = sum(len(faces) for faces in clusters.values())
        
        cluster_sizes = [len(faces) for faces in clusters.values()]
        
        stats = {
            'total_clusters': total_clusters,
            'total_faces_clustered': total_faces_clustered,
            'min_cluster_size': min(cluster_sizes) if cluster_sizes else 0,
            'max_cluster_size': max(cluster_sizes) if cluster_sizes else 0,
            'avg_cluster_size': float(np.mean(cluster_sizes)) if cluster_sizes else 0.0
        }
        
        logger.debug(f"Cluster stats: {stats}")
        return stats

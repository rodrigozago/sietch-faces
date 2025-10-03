import numpy as np
from sklearn.cluster import DBSCAN
from typing import List, Dict
from app.config import get_settings

settings = get_settings()


class FaceClustering:
    """Clustering faces using DBSCAN"""
    
    def __init__(self):
        self.eps = settings.dbscan_eps
        self.min_samples = settings.dbscan_min_samples
    
    def cluster_faces(self, embeddings_dict: Dict[int, np.ndarray]) -> Dict[int, List[int]]:
        """
        Cluster faces based on embedding similarity using DBSCAN
        
        Args:
            embeddings_dict: Dictionary of {face_id: embedding}
            
        Returns:
            Dictionary of {cluster_id: [face_ids]}
        """
        if not embeddings_dict:
            return {}
        
        # Extract face IDs and embeddings
        face_ids = list(embeddings_dict.keys())
        embeddings = np.array([embeddings_dict[fid] for fid in face_ids])
        
        # DBSCAN clustering
        # We use cosine distance metric
        # eps controls the maximum distance between two samples
        clustering = DBSCAN(
            eps=self.eps,
            min_samples=self.min_samples,
            metric='cosine'
        )
        
        labels = clustering.fit_predict(embeddings)
        
        # Organize results by cluster
        clusters = {}
        
        for face_id, label in zip(face_ids, labels):
            # label = -1 means noise (not assigned to any cluster)
            if label == -1:
                continue
            
            if label not in clusters:
                clusters[label] = []
            
            clusters[label].append(face_id)
        
        return clusters
    
    def get_cluster_stats(self, clusters: Dict[int, List[int]]) -> Dict:
        """
        Get statistics about clusters
        
        Args:
            clusters: Dictionary of {cluster_id: [face_ids]}
            
        Returns:
            Dictionary with cluster statistics
        """
        total_clusters = len(clusters)
        total_faces_clustered = sum(len(faces) for faces in clusters.values())
        
        cluster_sizes = [len(faces) for faces in clusters.values()]
        
        stats = {
            'total_clusters': total_clusters,
            'total_faces_clustered': total_faces_clustered,
            'min_cluster_size': min(cluster_sizes) if cluster_sizes else 0,
            'max_cluster_size': max(cluster_sizes) if cluster_sizes else 0,
            'avg_cluster_size': np.mean(cluster_sizes) if cluster_sizes else 0
        }
        
        return stats

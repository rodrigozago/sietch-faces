from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import ClustersResponse, ClusterResponse, FaceResponse
from app.models import Face
from app.clustering import FaceClustering
from app.face_recognition import FaceRecognizer

router = APIRouter()

face_clustering = FaceClustering()


@router.get("", response_model=ClustersResponse)
async def get_clusters(
    only_unidentified: bool = True,
    db: Session = Depends(get_db)
):
    """
    Cluster faces automatically using DBSCAN
    
    - Groups similar faces together
    - Only clusters unidentified faces by default
    - Returns clusters sorted by size (largest first)
    """
    
    # Query faces
    query = db.query(Face)
    
    if only_unidentified:
        query = query.filter(Face.person_id == None)
    
    faces = query.all()
    
    if not faces:
        return ClustersResponse(
            total_clusters=0,
            clusters=[]
        )
    
    # Build embeddings dictionary
    embeddings_dict = {
        face.id: FaceRecognizer.deserialize_embedding(face.embedding)
        for face in faces
    }
    
    # Cluster faces
    clusters = face_clustering.cluster_faces(embeddings_dict)
    
    # Build response
    cluster_responses = []
    
    for cluster_id, face_ids in clusters.items():
        # Get face objects
        cluster_faces = [
            face for face in faces if face.id in face_ids
        ]
        
        face_responses = [FaceResponse.model_validate(f) for f in cluster_faces]
        
        cluster_responses.append(ClusterResponse(
            cluster_id=cluster_id,
            face_count=len(face_ids),
            faces=face_responses
        ))
    
    # Sort by face count (largest first)
    cluster_responses.sort(key=lambda x: x.face_count, reverse=True)
    
    return ClustersResponse(
        total_clusters=len(cluster_responses),
        clusters=cluster_responses
    )

"""
Service for claiming unclaimed persons and managing user-person relationships
"""
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models import User, Person, Face, Photo
from app.services.face_matching import FaceMatchingService


class ClaimService:
    """Service for managing person claims"""
    
    def __init__(self, db: Session):
        self.db = db
        self.matching_service = FaceMatchingService(db)
    
    def claim_persons(
        self,
        user: User,
        person_ids: List[int]
    ) -> dict:
        """
        Claim one or more unclaimed persons for a user
        
        Args:
            user: User claiming the persons
            person_ids: List of person IDs to claim
            
        Returns:
            dict with claimed_count, person_ids, total_photos
        """
        claimed_count = 0
        total_photos = 0
        
        for person_id in person_ids:
            person = self.db.query(Person).filter(
                Person.id == person_id,
                Person.is_claimed == False  # Only unclaimed persons
            ).first()
            
            if person:
                # Claim the person
                person.is_claimed = True
                person.user_id = user.id
                person.name = user.username  # Set name to username
                
                # Count photos
                total_photos += len(person.faces)
                
                claimed_count += 1
        
        # If user doesn't have a primary person yet, set the first one
        if not user.person_id and claimed_count > 0:
            user.person_id = person_ids[0]
        
        self.db.commit()
        
        return {
            "claimed_count": claimed_count,
            "person_ids": person_ids[:claimed_count],
            "total_photos": total_photos
        }
    
    def merge_persons(
        self,
        target_person_id: int,
        source_person_ids: List[int]
    ) -> dict:
        """
        Merge multiple persons into one
        (useful for cleaning up duplicates)
        
        Args:
            target_person_id: Person to keep
            source_person_ids: Persons to merge into target
            
        Returns:
            dict with merged_count, total_faces_moved
        """
        target_person = self.db.query(Person).filter(
            Person.id == target_person_id
        ).first()
        
        if not target_person:
            return {"error": "Target person not found"}
        
        merged_count = 0
        total_faces_moved = 0
        
        for source_id in source_person_ids:
            if source_id == target_person_id:
                continue  # Skip self
            
            source_person = self.db.query(Person).filter(
                Person.id == source_id
            ).first()
            
            if not source_person:
                continue
            
            # Move all faces to target person
            faces_moved = self.db.query(Face).filter(
                Face.person_id == source_id
            ).update({"person_id": target_person_id})
            
            total_faces_moved += faces_moved
            
            # Delete source person
            self.db.delete(source_person)
            merged_count += 1
        
        self.db.commit()
        
        return {
            "merged_count": merged_count,
            "total_faces_moved": total_faces_moved,
            "target_person_id": target_person_id
        }
    
    def transfer_person_to_user(
        self,
        person_id: int,
        user: User
    ) -> Optional[Person]:
        """
        Transfer an unclaimed person to a user
        
        Args:
            person_id: Person to transfer
            user: User to transfer to
            
        Returns:
            Person if successful, None otherwise
        """
        person = self.db.query(Person).filter(
            Person.id == person_id,
            Person.is_claimed == False
        ).first()
        
        if not person:
            return None
        
        # Transfer person to user
        person.is_claimed = True
        person.user_id = user.id
        person.name = user.username
        
        # If user doesn't have a primary person, set this one
        if not user.person_id:
            user.person_id = person_id
        
        self.db.commit()
        self.db.refresh(person)
        
        return person
    
    def unclaim_person(
        self,
        person_id: int,
        user: User
    ) -> bool:
        """
        Unclaim a person (remove user association)
        
        Args:
            person_id: Person to unclaim
            user: User who owns the person
            
        Returns:
            True if successful, False otherwise
        """
        person = self.db.query(Person).filter(
            Person.id == person_id,
            Person.user_id == user.id
        ).first()
        
        if not person:
            return False
        
        # Unclaim the person
        person.is_claimed = False
        person.user_id = None
        
        # If this was user's primary person, clear it
        if user.person_id == person_id:
            user.person_id = None
        
        self.db.commit()
        
        return True
    
    def get_user_photos_with_person(
        self,
        user: User,
        include_unclaimed: bool = False
    ) -> List[Photo]:
        """
        Get all photos where user appears (based on face recognition)
        
        Args:
            user: User to find photos for
            include_unclaimed: Include photos from unclaimed persons
            
        Returns:
            List of Photo objects
        """
        if not user.person_id and not include_unclaimed:
            return []
        
        # Get all faces of user's person(s)
        query = self.db.query(Face)
        
        if user.person_id:
            # Get faces from user's primary person
            person_ids = [user.person_id]
            
            # Also get faces from other claimed persons by this user
            other_persons = self.db.query(Person).filter(
                Person.user_id == user.id,
                Person.id != user.person_id
            ).all()
            person_ids.extend([p.id for p in other_persons])
            
            query = query.filter(Face.person_id.in_(person_ids))
        
        faces = query.all()
        
        # Get unique photos
        photo_ids = set(face.photo_id for face in faces if face.photo_id)
        
        photos = self.db.query(Photo).filter(
            Photo.id.in_(photo_ids)
        ).order_by(Photo.uploaded_at.desc()).all()
        
        return photos

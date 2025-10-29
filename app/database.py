from sqlalchemy import create_engine, text, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import get_settings
from app.services.api_key_service import ApiKeyService

settings = get_settings()

# Create engine
if settings.database_url.startswith("sqlite"):
    engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(settings.database_url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _ensure_person_schema(conn):
    inspector = inspect(conn)
    if not inspector.has_table("persons"):
        return

    person_columns = {col["name"] for col in inspector.get_columns("persons")}

    if "is_claimed" not in person_columns:
        conn.execute(text("ALTER TABLE persons ADD COLUMN is_claimed BOOLEAN DEFAULT FALSE"))

    if "user_id" not in person_columns:
        conn.execute(text("ALTER TABLE persons ADD COLUMN user_id VARCHAR"))

    conn.execute(text("ALTER TABLE persons ALTER COLUMN is_claimed SET DEFAULT FALSE"))
    conn.execute(text("UPDATE persons SET is_claimed = FALSE WHERE is_claimed IS NULL"))

    person_indexes = {idx["name"] for idx in inspector.get_indexes("persons")}
    if "ix_persons_user_id" not in person_indexes:
        conn.execute(text("CREATE INDEX IF NOT EXISTS ix_persons_user_id ON persons (user_id)"))

    existing_person_fk = {
        tuple(fk["constrained_columns"])
        for fk in inspector.get_foreign_keys("persons")
    }
    if ("user_id",) not in existing_person_fk and inspector.has_table("users"):
        conn.execute(text(
            "ALTER TABLE persons "
            "ADD CONSTRAINT fk_persons_user_id_users "
            "FOREIGN KEY (user_id) REFERENCES users (id) "
            "ON DELETE SET NULL"
        ))


def _ensure_faces_schema(conn):
    inspector = inspect(conn)
    if not inspector.has_table("faces"):
        return

    face_columns = {col["name"] for col in inspector.get_columns("faces")}

    if "photo_id" not in face_columns:
        conn.execute(text("ALTER TABLE faces ADD COLUMN photo_id VARCHAR"))

    bbox_map = {
        "x": "bbox_x",
        "y": "bbox_y",
        "width": "bbox_width",
        "height": "bbox_height",
    }

    for new_col, legacy_col in bbox_map.items():
        if new_col not in face_columns:
            conn.execute(text(f"ALTER TABLE faces ADD COLUMN {new_col} INTEGER"))
            if legacy_col in face_columns:
                conn.execute(text(
                    f"UPDATE faces SET {new_col} = {legacy_col} WHERE {legacy_col} IS NOT NULL"
                ))
            conn.execute(text(f"UPDATE faces SET {new_col} = 0 WHERE {new_col} IS NULL"))
            conn.execute(text(f"ALTER TABLE faces ALTER COLUMN {new_col} SET DEFAULT 0"))
            conn.execute(text(f"ALTER TABLE faces ALTER COLUMN {new_col} SET NOT NULL"))

    if "created_at" not in face_columns:
        conn.execute(text("ALTER TABLE faces ADD COLUMN created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()"))

    face_indexes = {idx["name"] for idx in inspector.get_indexes("faces")}
    if "ix_faces_person_id" not in face_indexes:
        conn.execute(text("CREATE INDEX IF NOT EXISTS ix_faces_person_id ON faces (person_id)"))
    if "ix_faces_photo_id" not in face_indexes:
        conn.execute(text("CREATE INDEX IF NOT EXISTS ix_faces_photo_id ON faces (photo_id)"))

    existing_face_fk = {
        tuple(fk["constrained_columns"])
        for fk in inspector.get_foreign_keys("faces")
    }
    if ("photo_id",) not in existing_face_fk and inspector.has_table("photos"):
        conn.execute(text(
            "ALTER TABLE faces "
            "ADD CONSTRAINT fk_faces_photo_id_photos "
            "FOREIGN KEY (photo_id) REFERENCES photos (id) "
            "ON DELETE SET NULL"
        ))
    if ("person_id",) not in existing_face_fk and inspector.has_table("persons"):
        conn.execute(text(
            "ALTER TABLE faces "
            "ADD CONSTRAINT fk_faces_person_id_persons "
            "FOREIGN KEY (person_id) REFERENCES persons (id) "
            "ON DELETE SET NULL"
        ))


def init_db():
    """Initialize database tables"""
    from app.models import Face, Person, User, Photo, ApiKey
    _ = ApiKey  # ensure model is registered before create_all
    Base.metadata.create_all(bind=engine)

    with engine.begin() as conn:
        _ensure_person_schema(conn)
        _ensure_faces_schema(conn)

    # Ensure bootstrap API key exists for service-to-service authentication
    with SessionLocal() as db:
        service = ApiKeyService(db)
        service.ensure_bootstrap_key(settings.core_api_bootstrap_key)

    print("Database initialized successfully!")


if __name__ == "__main__":
    init_db()

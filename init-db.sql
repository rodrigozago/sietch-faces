-- Initialize Sietch Faces Database
-- This script runs automatically when the container is first created

-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE sietch_faces TO sietch_user;

-- Create schema (optional)
-- CREATE SCHEMA IF NOT EXISTS app AUTHORIZATION sietch_user;

-- Log initialization
DO $$
BEGIN
    RAISE NOTICE 'Sietch Faces database initialized successfully!';
END $$;

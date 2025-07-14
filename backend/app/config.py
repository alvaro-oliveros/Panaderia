import os
from pathlib import Path

class Config:
    # Database configuration
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./panaderias.db")
    
    # Server configuration
    HOST = os.getenv("HOST", "127.0.0.1")
    PORT = int(os.getenv("PORT", "8000"))
    
    # CORS configuration
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
    
    @classmethod
    def get_database_url(cls):
        """Get database URL, ensuring SQLite path is absolute for Docker"""
        if cls.DATABASE_URL.startswith("sqlite:///"):
            # Make SQLite path absolute if it's not already
            db_path = cls.DATABASE_URL.replace("sqlite:///", "")
            if not os.path.isabs(db_path):
                # Create absolute path relative to project root
                project_root = Path(__file__).parent.parent
                db_path = project_root / db_path
            return f"sqlite:///{db_path}"
        return cls.DATABASE_URL
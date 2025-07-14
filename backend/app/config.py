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
        """Get database URL with proper configuration for different database types"""
        if cls.DATABASE_URL.startswith("sqlite:///"):
            # SQLite-specific handling for absolute paths (backwards compatibility)
            db_path = cls.DATABASE_URL.replace("sqlite:///", "")
            if not os.path.isabs(db_path):
                # Create absolute path relative to project root
                project_root = Path(__file__).parent.parent
                db_path = project_root / db_path
            return f"sqlite:///{db_path}"
        elif cls.DATABASE_URL.startswith("postgresql://"):
            # PostgreSQL connection - return as-is
            return cls.DATABASE_URL
        else:
            # Other database types (MySQL, etc.) - return as-is
            return cls.DATABASE_URL
    
    @classmethod
    def get_engine_options(cls):
        """Get database engine options based on database type"""
        if cls.DATABASE_URL.startswith("postgresql://"):
            # PostgreSQL-specific optimizations
            return {
                "pool_size": 10,
                "max_overflow": 20,
                "pool_pre_ping": True,
                "pool_recycle": 300,
                "echo": False  # Set to True for SQL debugging
            }
        elif cls.DATABASE_URL.startswith("sqlite:///"):
            # SQLite-specific options
            return {
                "echo": False,
                "connect_args": {"check_same_thread": False}
            }
        else:
            # Default options
            return {"echo": False}
from fastapi import FastAPI, Depends
import uvicorn
import os
import psycopg2
import redis
from minio import Minio

app = FastAPI()

@app.get("/health")
def health_check():
    status = {
        "api": "healthy",
        "dependencies": {}
    }
    
    # Vérification de la connexion PostgreSQL
    try:
        db_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@postgres:5432/commitment")
        conn = psycopg2.connect(db_url)
        conn.close()
        status["dependencies"]["postgres"] = "connected"
    except Exception as e:
        status["dependencies"]["postgres"] = f"error: {str(e)}"
    
    # Vérification de la connexion Redis
    try:
        redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
        r = redis.from_url(redis_url)
        r.ping()
        status["dependencies"]["redis"] = "connected"
    except Exception as e:
        status["dependencies"]["redis"] = f"error: {str(e)}"
    
    # Vérification de la connexion MinIO
    try:
        minio_endpoint = os.getenv("MINIO_ENDPOINT", "storage:9000")
        minio_access_key = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
        minio_secret_key = os.getenv("MINIO_SECRET_KEY", "minioadmin")
        
        client = Minio(
            minio_endpoint,
            access_key=minio_access_key,
            secret_key=minio_secret_key,
            secure=False
        )
        
        # Lister les buckets pour vérifier la connexion
        buckets = client.list_buckets()
        status["dependencies"]["minio"] = "connected"
    except Exception as e:
        status["dependencies"]["minio"] = f"error: {str(e)}"
    
    return status

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 5000)))

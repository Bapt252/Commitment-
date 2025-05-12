import uvicorn
import os

if __name__ == "__main__":
    # Utiliser le port 7000 au lieu de 8000 ou 5000
    port = int(os.environ.get('PORT', 7000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)

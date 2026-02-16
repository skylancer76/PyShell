# Vercel serverless function entry point
import sys
import os
from pathlib import Path

# Add parent directory to path to import main
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Change to backend directory for relative imports
os.chdir(backend_dir)

# Import the FastAPI app
try:
    from main import app
except Exception as e:
    # Fallback for import errors
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    
    app = FastAPI()
    
    @app.get("/{path:path}")
    @app.post("/{path:path}")
    def error_handler(path: str):
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to initialize app: {str(e)}"}
        )



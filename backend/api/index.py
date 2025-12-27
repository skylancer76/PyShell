# Vercel serverless function entry point
import sys
import os
from pathlib import Path

# Add parent directory to path to import main
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Change to backend directory for relative imports
os.chdir(backend_dir)

try:
    from main import app
    from mangum import Mangum
    
    # Export handler for Vercel
    handler = Mangum(app, lifespan="off")
except Exception as e:
    # Create a minimal error handler if import fails
    from fastapi import FastAPI
    from mangum import Mangum
    
    error_app = FastAPI()
    
    @error_app.get("/{path:path}")
    @error_app.post("/{path:path}")
    def error_handler(path: str):
        return {"error": f"Failed to initialize app: {str(e)}"}
    
    handler = Mangum(error_app, lifespan="off")


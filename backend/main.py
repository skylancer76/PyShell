from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import psutil
import time
from command_processor import CommandProcessor
from commands_list import COMMANDS

# Initialize FastAPI app
app = FastAPI(title="PyShell Terminal API", version="1.0.0")

# CORS middleware - allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global command processor instance (lazy initialization)
processor = None

def get_processor():
    global processor
    if processor is None:
        try:
            processor = CommandProcessor()
        except Exception as e:
            print(f"Error initializing CommandProcessor: {e}")
            # Return a minimal processor that will handle errors gracefully
            processor = CommandProcessor()
    return processor

class CommandRequest(BaseModel):
    command: str

@app.post("/execute")
def run_command(req: CommandRequest):
    try:
        proc = get_processor()
        output = proc.execute(req.command)
        return {"output": output}
    except Exception as e:
        # Log error for debugging
        print(f"Error executing command '{req.command}': {str(e)}")
        return {"output": f"Error: {str(e)}"}

@app.get("/autocomplete")
def autocomplete(prefix: str):
    if not prefix:
        return {"suggestions": []}
    
    # Simple prefix matching
    matches = [c for c in COMMANDS if c.startswith(prefix.lower())]
    return {"suggestions": matches}

@app.get("/stats")
def stats():
    try:
        mem = psutil.virtual_memory().percent
        cpu = psutil.cpu_percent(interval=1)  # Get actual CPU usage
        net = psutil.net_io_counters()
        
        return {
            "cpu": round(cpu, 1),
            "mem": round(mem, 1),
            "net_up": net.bytes_sent,
            "net_down": net.bytes_recv
        }
    except Exception as e:
        print(f"Error getting stats: {e}")
        # Return default values if stats fail
        return {
            "cpu": 0.0,
            "mem": 0.0,
            "net_up": 0,
            "net_down": 0
        }

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "ok", "timestamp": time.time()}

# Test endpoint for CORS debugging
@app.get("/test")
def test_endpoint():
    return {"message": "CORS is working!", "timestamp": time.time()}

# Vercel serverless function handler
from mangum import Mangum
handler = Mangum(app)
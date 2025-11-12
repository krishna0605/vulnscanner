import sys
import os
import uvicorn

# Add backend to Python path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

# Import the app
from backend.main import app

if __name__ == "__main__":
    print("Starting backend server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
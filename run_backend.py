import uvicorn
import sys
import os

# Add backend to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

if __name__ == "__main__":
    # Change to backend directory
    os.chdir(os.path.join(os.path.dirname(__file__), 'backend'))
    
    # Import the app
    from backend.main import app
    
    # Run the server
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
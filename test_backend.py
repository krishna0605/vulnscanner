import sys
import os

# Add backend to Python path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

print(f"Python path: {sys.path}")
print(f"Backend path exists: {os.path.exists(backend_path)}")

try:
    # Try to import the main module
    from backend.main import app
    print("Successfully imported app")
except Exception as e:
    print(f"Error importing app: {e}")
    import traceback
    traceback.print_exc()
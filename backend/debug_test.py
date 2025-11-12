#!/usr/bin/env python3

from schemas.dashboard import ProjectCreate
from pydantic import ValidationError

def test_domain_validation():
    """Test domain validation."""
    invalid_domains = [
        "",  # Empty
        "not-a-domain",  # Invalid format
        "http://example.com",  # Should not include protocol
        "example.com/path",  # Should not include path
    ]
    
    for domain in invalid_domains:
        data = {
            "name": "Test Project",
            "target_domain": domain
        }
        
        try:
            project = ProjectCreate(**data)
            print(f"ERROR: No validation error for domain='{domain}'")
            print(f"Created project: {project}")
            return False
        except ValidationError as e:
            print(f"SUCCESS: ValidationError for domain='{domain}': {e}")
            continue
    
    # Test valid domains
    valid_domains = ["example.com", "sub.example.com", "localhost", "192.168.1.1"]
    for domain in valid_domains:
        data = {
            "name": "Test Project",
            "target_domain": domain
        }
        
        try:
            project = ProjectCreate(**data)
            print(f"SUCCESS: Valid domain '{domain}' accepted")
        except ValidationError as e:
            print(f"ERROR: Valid domain '{domain}' rejected: {e}")
            return False
    
    return True

if __name__ == "__main__":
    test_domain_validation()
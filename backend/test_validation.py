#!/usr/bin/env python3

from schemas.dashboard import ProjectCreate
from pydantic import ValidationError

def test_empty_name():
    try:
        ProjectCreate(name='', target_domain='example.com')
        print("Empty name: No error raised")
        return False
    except ValidationError:
        print("Empty name: ValidationError raised")
        return True

def test_long_name():
    try:
        ProjectCreate(name='a' * 101, target_domain='example.com')
        print("Long name: No error raised")
        return False
    except ValidationError:
        print("Long name: ValidationError raised")
        return True

def test_empty_domain():
    try:
        ProjectCreate(name='Test Project', target_domain='')
        print("Empty domain: No error raised")
        return False
    except ValidationError:
        print("Empty domain: ValidationError raised")
        return True

if __name__ == "__main__":
    test_empty_name()
    test_long_name()
    test_empty_domain()
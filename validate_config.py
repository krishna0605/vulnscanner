#!/usr/bin/env python3
"""
Configuration Validation Script for VulnScanner

This script validates the current configuration and provides recommendations
for security and production readiness.
"""

import sys
from pathlib import Path

# Add backend to path for imports
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

try:
    from core.config import settings
    from pydantic import ValidationError
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running this from the project root directory")
    sys.exit(1)


def print_header(title: str):
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'-'*40}")
    print(f" {title}")
    print(f"{'-'*40}")


def validate_environment():
    """Validate the current environment configuration."""
    print_header("VULNSCANNER CONFIGURATION VALIDATION")
    
    # Basic configuration info
    print_section("Environment Information")
    print(f"📋 Application Name: {settings.app_name}")
    print(f"🌍 Environment: {settings.app_env}")
    print(f"🐛 Debug Mode: {settings.debug}")
    print(f"📊 Log Level: {settings.log_level}")
    print(f"🔧 Development Mode: {settings.development_mode}")
    
    # Security configuration
    print_section("Security Configuration")
    print(f"🔐 Secret Key Length: {len(settings.secret_key)} chars")
    print(f"🎫 JWT Algorithm: {settings.jwt_algorithm}")
    print(f"⏰ JWT Expiry: {settings.jwt_exp_minutes} minutes")
    print(f"🛡️ CSRF Protection: {'Enabled' if settings.csrf_secret else 'Disabled'}")
    print(f"🔒 Security Headers: {'Enabled' if settings.security_headers_enabled else 'Disabled'}")
    
    # Database configuration
    print_section("Database Configuration")
    has_supabase = bool(settings.supabase_db_url)
    has_direct_db = bool(settings.database_url)
    print(f"🗄️ Supabase DB: {'Configured' if has_supabase else 'Not configured'}")
    print(f"🗄️ Direct DB: {'Configured' if has_direct_db else 'Not configured'}")
    print(f"📢 DB Echo: {settings.db_echo}")
    print(f"🚫 Skip Supabase: {settings.skip_supabase}")
    
    # Supabase configuration
    print_section("Supabase Configuration")
    print(f"🌐 Supabase URL: {'Set' if settings.supabase_url else 'Not set'}")
    print(f"🔑 Anon Key: {'Set' if settings.supabase_anon_key else 'Not set'}")
    print(f"🔑 Service Role Key: {'Set' if settings.supabase_service_role_key else 'Not set'}")
    
    # CORS configuration
    print_section("CORS Configuration")
    if isinstance(settings.cors_origins, list):
        print(f"🌐 CORS Origins ({len(settings.cors_origins)}):")
        for origin in settings.cors_origins:
            print(f"   - {origin}")
    else:
        print(f"🌐 CORS Origins: {settings.cors_origins}")
    
    # Redis/Celery configuration
    print_section("Redis/Celery Configuration")
    print(f"🔴 Redis URL: {settings.redis_url}")
    print(f"📨 Celery Broker: {settings.celery_broker_url}")
    print(f"📊 Celery Backend: {settings.celery_result_backend}")
    
    # Crawler configuration
    print_section("Crawler Configuration")
    print(f"🕷️ Max Depth: {settings.crawler_max_depth}")
    print(f"📄 Max Pages: {settings.crawler_max_pages}")
    print(f"⚡ Requests/Second: {settings.crawler_requests_per_second}")
    print(f"⏱️ Timeout: {settings.crawler_timeout}s")
    print(f"🤖 User Agent: {settings.crawler_user_agent}")


def check_security_issues():
    """Check for security issues in the configuration."""
    print_section("Security Analysis")
    
    issues = []
    warnings = []
    
    # Check secret key
    if settings.secret_key == "change-me":
        issues.append("Secret key is using default value")
    elif len(settings.secret_key) < 32:
        issues.append("Secret key is too short (< 32 characters)")
    
    # Check JWT configuration
    if not settings.jwt_secret_key:
        warnings.append("JWT secret key not set, using main secret key")
    
    # Check CSRF
    if not settings.csrf_secret and settings.app_env == "production":
        issues.append("CSRF secret not set in production")
    
    # Check debug mode
    if settings.debug and settings.app_env == "production":
        issues.append("Debug mode enabled in production")
    
    # Check development mode
    if settings.development_mode and settings.app_env == "production":
        issues.append("Development mode enabled in production")
    
    # Check database configuration
    if not settings.get_database_url():
        issues.append("No database URL configured")
    
    # Check CORS for production
    if settings.app_env == "production" and "localhost" in str(settings.cors_origins):
        warnings.append("CORS includes localhost in production")
    
    # Display results
    if issues:
        print("🚨 SECURITY ISSUES FOUND:")
        for issue in issues:
            print(f"   ❌ {issue}")
    
    if warnings:
        print("\n⚠️ WARNINGS:")
        for warning in warnings:
            print(f"   ⚠️ {warning}")
    
    if not issues and not warnings:
        print("✅ No security issues detected!")
    
    return len(issues) == 0


def check_production_readiness():
    """Check if configuration is ready for production."""
    print_section("Production Readiness")
    
    if settings.app_env != "production":
        print("ℹ️ Not running in production mode - skipping production checks")
        return True
    
    production_issues = settings.validate_production_config()
    
    if production_issues:
        print("🚨 PRODUCTION ISSUES FOUND:")
        for issue in production_issues:
            print(f"   ❌ {issue}")
        return False
    else:
        print("✅ Configuration is production-ready!")
        return True


def provide_recommendations():
    """Provide configuration recommendations."""
    print_section("Recommendations")
    
    recommendations = []
    
    # Environment-specific recommendations
    if settings.app_env == "development":
        recommendations.append("Generate secure keys for production: python generate_secure_keys.py")
        recommendations.append("Set up proper database connection for production")
        recommendations.append("Configure CSRF protection for production")
    
    # Security recommendations
    if not settings.security_headers_enabled:
        recommendations.append("Enable security headers for better protection")
    
    if settings.log_level == "DEBUG" and settings.app_env != "development":
        recommendations.append("Change log level from DEBUG in non-development environments")
    
    # Performance recommendations
    if settings.crawler_requests_per_second > 50:
        recommendations.append("Consider reducing crawler RPS to be more respectful to target servers")
    
    if settings.crawler_max_pages > 10000:
        recommendations.append("Large page limits may impact performance - consider chunking scans")
    
    if recommendations:
        print("💡 RECOMMENDATIONS:")
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. {rec}")
    else:
        print("✅ Configuration looks good - no specific recommendations!")


def main():
    """Main validation function."""
    try:
        # Run all validation checks
        validate_environment()
        security_ok = check_security_issues()
        production_ok = check_production_readiness()
        provide_recommendations()
        
        # Final summary
        print_header("VALIDATION SUMMARY")
        
        if security_ok and production_ok:
            print("✅ Configuration validation PASSED")
            print("🚀 Ready to proceed with implementation!")
            return 0
        else:
            print("❌ Configuration validation FAILED")
            print("🔧 Please address the issues above before proceeding")
            return 1
            
    except ValidationError as e:
        print_header("VALIDATION ERROR")
        print(f"❌ Configuration validation failed: {e}")
        return 1
    except Exception as e:
        print_header("UNEXPECTED ERROR")
        print(f"💥 Unexpected error during validation: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
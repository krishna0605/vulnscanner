#!/usr/bin/env python3
"""
Create test user in Supabase for frontend authentication
"""
import asyncio
from supabase import create_client, Client
from core.config import settings

async def create_test_user():
    """Create test user in Supabase"""
    print("🚀 Creating test user in Supabase...")
    
    # Test credentials
    email = "test@example.com"
    password = "testpassword123"
    
    try:
        # Initialize Supabase client with service role key (admin access)
        supabase: Client = create_client(
            settings.supabase_url,
            settings.supabase_service_role_key  # Use service role for admin operations
        )
        
        print(f"📧 Email: {email}")
        print(f"🔑 Password: {password}")
        print(f"🌐 Supabase URL: {settings.supabase_url}")
        print("-" * 50)
        
        # Try to create the user
        response = supabase.auth.admin.create_user({
            "email": email,
            "password": password,
            "email_confirm": True,  # Auto-confirm email
            "user_metadata": {
                "full_name": "Test User"
            }
        })
        
        if response.user:
            print("✅ Test user created successfully in Supabase!")
            print(f"👤 User ID: {response.user.id}")
            print(f"📧 Email: {response.user.email}")
            print(f"✅ Email Confirmed: {response.user.email_confirmed_at is not None}")
            return True
        else:
            print("❌ Failed to create user - no user returned")
            return False
            
    except Exception as e:
        error_msg = str(e)
        if "User already registered" in error_msg or "already been registered" in error_msg:
            print("ℹ️ Test user already exists in Supabase - that's okay!")
            
            # Try to get the existing user
            try:
                users = supabase.auth.admin.list_users()
                test_user = None
                for user in users:
                    if user.email == email:
                        test_user = user
                        break
                
                if test_user:
                    print(f"👤 Existing User ID: {test_user.id}")
                    print(f"📧 Email: {test_user.email}")
                    print(f"✅ Email Confirmed: {test_user.email_confirmed_at is not None}")
                    
                    # If email is not confirmed, confirm it
                    if not test_user.email_confirmed_at:
                        print("📧 Confirming email for existing user...")
                        supabase.auth.admin.update_user_by_id(
                            test_user.id,
                            {"email_confirm": True}
                        )
                        print("✅ Email confirmed!")
                
            except Exception as list_error:
                print(f"⚠️ Could not verify existing user: {list_error}")
            
            return True
        else:
            print(f"❌ Error creating test user: {error_msg}")
            return False

async def test_supabase_login():
    """Test login with the created user"""
    print("\n🧪 Testing Supabase login...")
    
    email = "test@example.com"
    password = "testpassword123"
    
    try:
        # Use anon key for regular user operations
        supabase: Client = create_client(
            settings.supabase_url,
            settings.supabase_anon_key
        )
        
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        if response.user:
            print("✅ Supabase login successful!")
            print(f"👤 User ID: {response.user.id}")
            print(f"📧 Email: {response.user.email}")
            print(f"🎫 Access Token: {response.session.access_token[:50]}..." if response.session else "No session")
            return True
        else:
            print("❌ Supabase login failed - no user returned")
            return False
            
    except Exception as e:
        print(f"❌ Supabase login error: {e}")
        return False

async def main():
    print("🚀 Supabase Test User Setup")
    print("=" * 50)
    
    # Check if Supabase is configured
    if not settings.supabase_url or not settings.supabase_service_role_key:
        print("❌ Supabase is not configured!")
        print("💡 Check your .env file for SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY")
        return
    
    # Create test user
    user_created = await create_test_user()
    
    if user_created:
        # Test login
        login_success = await test_supabase_login()
        
        print("\n" + "=" * 50)
        if login_success:
            print("🎉 Test user setup complete!")
            print("💡 You can now login with test@example.com / testpassword123")
        else:
            print("💥 Test user created but login failed!")
            print("💡 Check Supabase dashboard for user status")
    else:
        print("\n💥 Failed to create test user!")

if __name__ == "__main__":
    asyncio.run(main())
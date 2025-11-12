// Simple test to check Supabase authentication in browser console
// Run this in the browser console on http://localhost:3000

console.log('Testing Supabase authentication...');

// Check if supabase is available
if (typeof window !== 'undefined' && window.localStorage) {
  console.log('LocalStorage contents:');
  for (let i = 0; i < localStorage.length; i++) {
    const key = localStorage.key(i);
    if (key && key.includes('supabase')) {
      console.log(`${key}:`, localStorage.getItem(key));
    }
  }
  
  console.log('\nSessionStorage contents:');
  for (let i = 0; i < sessionStorage.length; i++) {
    const key = sessionStorage.key(i);
    if (key && key.includes('supabase')) {
      console.log(`${key}:`, sessionStorage.getItem(key));
    }
  }
}

// Test API call with current auth
async function testAuthenticatedAPI() {
  try {
    const response = await fetch('http://localhost:8000/api/v1/overview', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    console.log('API Response Status:', response.status);
    console.log('API Response:', await response.text());
  } catch (error) {
    console.error('API Error:', error);
  }
}

testAuthenticatedAPI();
import { supabase } from './src/lib/supabase';

async function test() {
  console.log('Testing Env...');
  const url = process.env.SUPABASE_URL;
  console.log('URL:', url ? 'Found' : 'Missing');
  if (url) console.log('URL starts with:', url.substring(0, 10));
}

test();

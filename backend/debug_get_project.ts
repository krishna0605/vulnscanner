import { supabase } from './src/lib/supabase';

async function run() {
  const { data, error } = await supabase.from('projects').select('id').limit(1);
  if (error) {
    console.error('Error:', error);
  } else {
    console.log('Project ID:', data?.[0]?.id);
  }
}
run();

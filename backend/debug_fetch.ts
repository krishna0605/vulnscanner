async function run() {
  try {
    const res = await fetch('http://127.0.0.1:3001/projects');
    console.log('Status:', res.status);
    const text = await res.text();
    console.log('Body:', text);
  } catch (e) {
    console.error('Fetch error:', e);
  }
}
run();

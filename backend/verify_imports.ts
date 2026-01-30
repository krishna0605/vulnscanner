import { CrawlerService } from './src/lib/crawler';

async function run() {
  try {
    console.log('Importing CrawlerService...');
    const crawler = new CrawlerService();
    console.log('Crawler instantiated successfully.');
  } catch (e) {
    console.error('Error:', e);
  }
}
run();

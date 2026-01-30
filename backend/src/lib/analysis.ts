export async function analyzePage(url: string, content: string) {
  const vulnerabilities = [];

  // 1. Check for missing security headers (Mock logic)
  // In real implementation, we would check response headers from the crawler
  // For now, we simulate finding issues
  if (Math.random() > 0.5) {
    vulnerabilities.push({
      type: 'Missing Headers',
      severity: 'medium',
      description: 'Strict-Transport-Security header is missing.',
      evidence: 'Response Headers: Server: nginx/1.18.0',
    });
  }

  // 2. Simple regex checks for sensitivity in content
  if (content.includes('password') || content.includes('key')) {
    vulnerabilities.push({
      type: 'Sensitive Information',
      severity: 'low',
      description: 'Page contains potential sensitive keywords like "password" or "key".',
      evidence: 'Found "password" in body text.',
    });
  }

  return vulnerabilities;
}

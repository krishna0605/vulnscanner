// ================================================
// Security Academy Data
// ================================================

// OWASP Top 10
export interface OWASPItem {
  id: string;
  title: string;
  severity: 'critical' | 'high' | 'medium';
  description: string;
  example: string;
  prevention: string[];
  icon: string;
}

export const owaspTop10: OWASPItem[] = [
  {
    id: 'A01',
    title: 'Broken Access Control',
    severity: 'critical',
    icon: 'lock_open',
    description: 'Restrictions on authenticated users are not properly enforced, allowing attackers to access unauthorized functionality or data.',
    example: 'Modifying URL parameters to access another user\'s account: /api/users/123 → /api/users/456',
    prevention: [
      'Implement proper access control checks on every request',
      'Deny access by default',
      'Use role-based access control (RBAC)',
      'Log access control failures and alert admins',
    ],
  },
  {
    id: 'A02',
    title: 'Cryptographic Failures',
    severity: 'critical',
    icon: 'key_off',
    description: 'Failures related to cryptography which often lead to exposure of sensitive data.',
    example: 'Storing passwords in plain text or using weak hashing algorithms like MD5.',
    prevention: [
      'Use strong, up-to-date encryption algorithms',
      'Never store passwords in plain text',
      'Use bcrypt, scrypt, or Argon2 for password hashing',
      'Implement proper key management',
    ],
  },
  {
    id: 'A03',
    title: 'Injection',
    severity: 'critical',
    icon: 'code',
    description: 'User-supplied data is not validated, filtered, or sanitized, leading to SQL, NoSQL, OS, or LDAP injection.',
    example: "SELECT * FROM users WHERE id = '\" + userId + \"' -- SQL Injection vulnerable code",
    prevention: [
      'Use parameterized queries or prepared statements',
      'Validate and sanitize all user inputs',
      'Use ORMs with proper escaping',
      'Implement least privilege database access',
    ],
  },
  {
    id: 'A04',
    title: 'Insecure Design',
    severity: 'high',
    icon: 'architecture',
    description: 'Missing or ineffective security controls and business logic flaws.',
    example: 'No rate limiting on password reset, allowing brute force attacks.',
    prevention: [
      'Use threat modeling during design phase',
      'Implement security design patterns',
      'Write security user stories',
      'Perform design reviews with security focus',
    ],
  },
  {
    id: 'A05',
    title: 'Security Misconfiguration',
    severity: 'high',
    icon: 'settings_applications',
    description: 'Missing security hardening, unnecessary features enabled, or default credentials in use.',
    example: 'Default admin credentials left unchanged: admin/admin',
    prevention: [
      'Remove unused features and frameworks',
      'Review and update configurations regularly',
      'Implement automated security configuration checks',
      'Use security headers properly',
    ],
  },
  {
    id: 'A06',
    title: 'Vulnerable Components',
    severity: 'high',
    icon: 'inventory_2',
    description: 'Using components with known vulnerabilities that can be exploited.',
    example: 'Using an outdated version of Log4j with CVE-2021-44228.',
    prevention: [
      'Maintain inventory of all components and versions',
      'Subscribe to security advisories',
      'Regularly update dependencies',
      'Use software composition analysis (SCA) tools',
    ],
  },
  {
    id: 'A07',
    title: 'Auth Failures',
    severity: 'high',
    icon: 'person_off',
    description: 'Authentication and session management implemented incorrectly.',
    example: 'Session IDs exposed in URLs, no session timeout, weak passwords allowed.',
    prevention: [
      'Implement multi-factor authentication',
      'Never ship with default credentials',
      'Implement proper session management',
      'Use secure password policies',
    ],
  },
  {
    id: 'A08',
    title: 'Data Integrity Failures',
    severity: 'medium',
    icon: 'verified',
    description: 'Code and infrastructure that does not protect against integrity violations.',
    example: 'Insecure deserialization allowing remote code execution.',
    prevention: [
      'Use digital signatures for software updates',
      'Verify integrity of downloaded dependencies',
      'Use secure CI/CD pipelines',
      'Implement code signing',
    ],
  },
  {
    id: 'A09',
    title: 'Logging Failures',
    severity: 'medium',
    icon: 'assignment_late',
    description: 'Insufficient logging, monitoring, and alerting capabilities.',
    example: 'Failed login attempts not logged, no alerts for suspicious activity.',
    prevention: [
      'Log all authentication and authorization events',
      'Implement centralized log management',
      'Set up real-time alerting',
      'Create incident response procedures',
    ],
  },
  {
    id: 'A10',
    title: 'SSRF',
    severity: 'medium',
    icon: 'cloud_off',
    description: 'Server-Side Request Forgery - fetching remote resources without validating user-supplied URLs.',
    example: 'Accessing internal services: fetch(userUrl) where userUrl = "http://localhost:8080/admin"',
    prevention: [
      'Validate and sanitize all user-supplied URLs',
      'Use allowlists for permitted domains',
      'Disable HTTP redirects',
      'Segment remote resource access',
    ],
  },
];

// Flashcards
export interface Flashcard {
  id: string;
  question: string;
  answer: string;
  category: string;
}

export const flashcards: Flashcard[] = [
  { id: 'f1', question: 'What is XSS?', answer: 'Cross-Site Scripting - injecting malicious scripts into trusted websites that execute in victims\' browsers.', category: 'Attacks' },
  { id: 'f2', question: 'What is CSRF?', answer: 'Cross-Site Request Forgery - tricking authenticated users into submitting unwanted requests.', category: 'Attacks' },
  { id: 'f3', question: 'What is SQL Injection?', answer: 'Inserting malicious SQL code into application queries to manipulate the database.', category: 'Attacks' },
  { id: 'f4', question: 'What is the CIA Triad?', answer: 'Confidentiality, Integrity, Availability - the three pillars of information security.', category: 'Concepts' },
  { id: 'f5', question: 'What is MFA?', answer: 'Multi-Factor Authentication - requiring multiple forms of verification to prove identity.', category: 'Defense' },
  { id: 'f6', question: 'What is a Zero-Day?', answer: 'A vulnerability unknown to the vendor with no available patch.', category: 'Concepts' },
  { id: 'f7', question: 'What is HTTPS?', answer: 'HTTP Secure - HTTP encrypted with TLS/SSL to protect data in transit.', category: 'Protocols' },
  { id: 'f8', question: 'What is a WAF?', answer: 'Web Application Firewall - filters and monitors HTTP traffic to protect web apps.', category: 'Defense' },
  { id: 'f9', question: 'What is Penetration Testing?', answer: 'Authorized simulated attacks to evaluate system security.', category: 'Concepts' },
  { id: 'f10', question: 'What is Social Engineering?', answer: 'Manipulating people into divulging confidential information or performing actions.', category: 'Attacks' },
  { id: 'f11', question: 'What is a CVE?', answer: 'Common Vulnerabilities and Exposures - a standardized ID for security vulnerabilities.', category: 'Concepts' },
  { id: 'f12', question: 'What is CORS?', answer: 'Cross-Origin Resource Sharing - a mechanism allowing restricted resources to be requested from another domain.', category: 'Protocols' },
];

// Code Examples
export interface CodeExample {
  id: string;
  title: string;
  language: string;
  vulnerableCode: string;
  secureCode: string;
  explanation: string;
}

export const codeExamples: CodeExample[] = [
  {
    id: 'c1',
    title: 'SQL Injection Prevention',
    language: 'javascript',
    vulnerableCode: `// ❌ VULNERABLE
const query = "SELECT * FROM users WHERE id = '" + userId + "'";
db.query(query);`,
    secureCode: `// ✅ SECURE
const query = "SELECT * FROM users WHERE id = $1";
db.query(query, [userId]);`,
    explanation: 'Use parameterized queries to prevent SQL injection.',
  },
  {
    id: 'c2',
    title: 'XSS Prevention',
    language: 'javascript',
    vulnerableCode: `// ❌ VULNERABLE
element.innerHTML = userInput;`,
    secureCode: `// ✅ SECURE
element.textContent = userInput;`,
    explanation: 'Use textContent instead of innerHTML to prevent XSS.',
  },
  {
    id: 'c3',
    title: 'Password Hashing',
    language: 'javascript',
    vulnerableCode: `// ❌ VULNERABLE
const hash = md5(password);`,
    secureCode: `// ✅ SECURE
const hash = await bcrypt.hash(password, 12);`,
    explanation: 'Use bcrypt, not MD5, for password hashing.',
  },
];

// CTF Platforms
export interface CTFPlatform {
  id: string;
  name: string;
  description: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced' | 'all';
  url: string;
  icon: string;
  color: string;
  tags: string[];
}

export const ctfPlatforms: CTFPlatform[] = [
  {
    id: 'htb',
    name: 'Hack The Box',
    description: 'Real-world pentesting labs with active machines and challenges.',
    difficulty: 'intermediate',
    url: 'https://www.hackthebox.com',
    icon: 'terminal',
    color: 'from-green-500 to-emerald-600',
    tags: ['Pentesting', 'Machines', 'Pro Labs'],
  },
  {
    id: 'thm',
    name: 'TryHackMe',
    description: 'Guided cybersecurity training with learning paths for beginners.',
    difficulty: 'beginner',
    url: 'https://tryhackme.com',
    icon: 'school',
    color: 'from-red-500 to-rose-600',
    tags: ['Learning Paths', 'Guided', 'Beginner'],
  },
  {
    id: 'pico',
    name: 'PicoCTF',
    description: 'Free CTF platform designed for students and beginners.',
    difficulty: 'beginner',
    url: 'https://picoctf.org',
    icon: 'flag',
    color: 'from-blue-500 to-indigo-600',
    tags: ['Free', 'Students', 'CTF'],
  },
  {
    id: 'portswigger',
    name: 'PortSwigger Labs',
    description: 'Web security academy with hands-on labs from Burp Suite creators.',
    difficulty: 'all',
    url: 'https://portswigger.net/web-security',
    icon: 'bug_report',
    color: 'from-orange-500 to-amber-600',
    tags: ['Web Security', 'Free', 'Labs'],
  },
  {
    id: 'webgoat',
    name: 'OWASP WebGoat',
    description: 'Deliberately insecure application for learning web security.',
    difficulty: 'beginner',
    url: 'https://owasp.org/www-project-webgoat/',
    icon: 'pets',
    color: 'from-purple-500 to-violet-600',
    tags: ['OWASP', 'Self-hosted', 'Learning'],
  },
  {
    id: 'rootme',
    name: 'Root Me',
    description: '400+ challenges across web, network, forensics, and crypto.',
    difficulty: 'all',
    url: 'https://www.root-me.org',
    icon: 'hub',
    color: 'from-gray-500 to-slate-600',
    tags: ['Challenges', 'Forensics', 'Crypto'],
  },
];

// Resources (Cheat Sheets)
export interface Resource {
  id: string;
  title: string;
  type: 'cheatsheet' | 'tool' | 'reference';
  description: string;
  url: string;
  icon: string;
}

export const resources: Resource[] = [
  {
    id: 'r1',
    title: 'OWASP Cheat Sheet Series',
    type: 'cheatsheet',
    description: 'Comprehensive security cheat sheets for developers.',
    url: 'https://cheatsheetseries.owasp.org',
    icon: 'menu_book',
  },
  {
    id: 'r2',
    title: 'PayloadsAllTheThings',
    type: 'reference',
    description: 'Useful payloads for web app testing and CTFs.',
    url: 'https://github.com/swisskyrepo/PayloadsAllTheThings',
    icon: 'code',
  },
  {
    id: 'r3',
    title: 'HackTricks',
    type: 'reference',
    description: 'Pentesting tricks and techniques wiki.',
    url: 'https://book.hacktricks.xyz',
    icon: 'auto_stories',
  },
  {
    id: 'r4',
    title: 'CyberChef',
    type: 'tool',
    description: 'The Cyber Swiss Army Knife for encoding/decoding.',
    url: 'https://gchq.github.io/CyberChef',
    icon: 'build',
  },
  {
    id: 'r5',
    title: 'Security Headers',
    type: 'tool',
    description: 'Analyze HTTP response headers for security.',
    url: 'https://securityheaders.com',
    icon: 'verified_user',
  },
  {
    id: 'r6',
    title: 'GTFOBins',
    type: 'reference',
    description: 'Unix binaries for privilege escalation.',
    url: 'https://gtfobins.github.io',
    icon: 'terminal',
  },
];

// Security News
export interface NewsItem {
  id: string;
  title: string;
  type: 'cve' | 'breach' | 'advisory';
  severity: 'critical' | 'high' | 'medium' | 'low';
  source: string;
  url: string;
}

export const securityNews: NewsItem[] = [
  {
    id: 'n1',
    title: 'CVE Database',
    type: 'cve',
    severity: 'high',
    source: 'NIST NVD',
    url: 'https://nvd.nist.gov',
  },
  {
    id: 'n2',
    title: 'CISA Known Exploited Vulnerabilities',
    type: 'advisory',
    severity: 'critical',
    source: 'CISA',
    url: 'https://www.cisa.gov/known-exploited-vulnerabilities-catalog',
  },
  {
    id: 'n3',
    title: 'The Hacker News',
    type: 'breach',
    severity: 'medium',
    source: 'THN',
    url: 'https://thehackernews.com',
  },
  {
    id: 'n4',
    title: 'Krebs on Security',
    type: 'breach',
    severity: 'medium',
    source: 'Krebs',
    url: 'https://krebsonsecurity.com',
  },
  {
    id: 'n5',
    title: 'Exploit Database',
    type: 'cve',
    severity: 'high',
    source: 'Exploit-DB',
    url: 'https://www.exploit-db.com',
  },
];

// Community Links
export interface CommunityLink {
  id: string;
  name: string;
  platform: 'discord' | 'reddit' | 'twitter' | 'slack' | 'forum';
  description: string;
  url: string;
  icon: string;
  members?: string;
}

export const communityLinks: CommunityLink[] = [
  {
    id: 'c1',
    name: 'r/netsec',
    platform: 'reddit',
    description: 'Information security news and discussion.',
    url: 'https://reddit.com/r/netsec',
    icon: 'forum',
    members: '600K+',
  },
  {
    id: 'c2',
    name: 'Hack The Box Discord',
    platform: 'discord',
    description: 'Official HTB community with help channels.',
    url: 'https://discord.gg/hackthebox',
    icon: 'chat',
    members: '300K+',
  },
  {
    id: 'c3',
    name: 'OWASP Slack',
    platform: 'slack',
    description: 'Connect with OWASP project contributors.',
    url: 'https://owasp.org/slack/invite',
    icon: 'group',
    members: '50K+',
  },
  {
    id: 'c4',
    name: 'r/AskNetsec',
    platform: 'reddit',
    description: 'Q&A for security professionals.',
    url: 'https://reddit.com/r/AskNetsec',
    icon: 'help',
    members: '200K+',
  },
  {
    id: 'c5',
    name: 'InfoSec Twitter',
    platform: 'twitter',
    description: 'Follow security researchers and news.',
    url: 'https://twitter.com/search?q=%23infosec',
    icon: 'tag',
  },
];

// Security concepts data for the explorable knowledge section

export interface Concept {
  id: string;
  title: string;
  subtitle: string;
  description: string;
  keyPoints: string[];
  icon: string;
  learnMoreUrl: string;
}

export interface Resource {
  id: string;
  name: string;
  url: string;
  description: string;
  icon: string;
}

export const concepts: Record<string, Concept> = {
  CIA_TRIAD: {
    id: 'cia-triad',
    title: 'CIA Triad',
    subtitle: 'Confidentiality, Integrity, Availability',
    description: 'The CIA Triad is the foundational model for information security, guiding policies and practices to protect data and systems.',
    keyPoints: [
      'Confidentiality: Ensuring information is accessible only to authorized users',
      'Integrity: Maintaining accuracy and completeness of data throughout its lifecycle',
      'Availability: Ensuring authorized users have reliable access to information when needed'
    ],
    icon: 'security',
    learnMoreUrl: '/learn#cia-triad'
  },
  MFA: {
    id: 'mfa',
    title: 'Multi-Factor Authentication',
    subtitle: 'Layered Security Defense',
    description: 'MFA adds extra layers of protection by requiring multiple forms of verification before granting access to systems or data.',
    keyPoints: [
      'Something you know: Passwords, PINs, security questions',
      'Something you have: Phone, hardware token, smart card',
      'Something you are: Biometrics like fingerprint or face recognition'
    ],
    icon: 'verified_user',
    learnMoreUrl: '/learn#mfa'
  },
  ENCRYPTION: {
    id: 'encryption',
    title: 'Encryption',
    subtitle: 'Data Protection Through Cryptography',
    description: 'Encryption transforms readable data into an encoded format that can only be decoded with the correct key, protecting sensitive information.',
    keyPoints: [
      'At-rest encryption: Protects stored data on disks and databases',
      'In-transit encryption: Secures data moving across networks (TLS/SSL)',
      'End-to-end encryption: Only sender and recipient can read the data'
    ],
    icon: 'lock',
    learnMoreUrl: '/learn#encryption'
  }
};

export const resources: Resource[] = [
  {
    id: 'owasp',
    name: 'OWASP',
    url: 'https://owasp.org',
    description: 'Open Web Application Security Project - Free security resources and tools',
    icon: 'public'
  },
  {
    id: 'nist',
    name: 'NIST',
    url: 'https://www.nist.gov/cybersecurity',
    description: 'National Institute of Standards and Technology - Security frameworks and guidelines',
    icon: 'account_balance'
  },
  {
    id: 'mitre',
    name: 'MITRE ATT&CK',
    url: 'https://attack.mitre.org',
    description: 'Knowledge base of adversary tactics and techniques',
    icon: 'hub'
  }
];

export const conceptsList = Object.values(concepts);

// Knowledge Base items for Core Principles and Essential Precautions
export interface KnowledgeItem {
  id: string;
  category: 'principle' | 'precaution';
  title: string;
  icon: string;
  description: string;
  tips: string[];
  learnMoreUrl: string;
}

export const knowledgeItems: KnowledgeItem[] = [
  // Core Principles
  {
    id: 'least-privilege',
    category: 'principle',
    title: 'Principle of Least Privilege',
    icon: 'check_circle',
    description: 'Users, programs, and systems should only have the minimum access rights necessary to perform their tasks. This limits the potential damage from accidents, errors, or unauthorized use.',
    tips: [
      'Grant permissions on a need-to-know basis only',
      'Regularly audit and revoke unnecessary access rights',
      'Use role-based access control (RBAC) for scalable management',
      'Implement time-limited elevated privileges when needed'
    ],
    learnMoreUrl: '/learn#least-privilege'
  },
  {
    id: 'secure-coding',
    category: 'principle',
    title: 'Secure Coding Practices',
    icon: 'check_circle',
    description: 'Writing code with security in mind from the start prevents vulnerabilities before they reach production. This includes input validation, output encoding, and proper error handling.',
    tips: [
      'Validate and sanitize all user inputs',
      'Use parameterized queries to prevent SQL injection',
      'Implement proper error handling without exposing sensitive info',
      'Keep dependencies updated and scan for known vulnerabilities'
    ],
    learnMoreUrl: '/learn#secure-coding'
  },
  {
    id: 'patch-management',
    category: 'principle',
    title: 'Continuous Patch Management',
    icon: 'check_circle',
    description: 'Regularly updating software and systems closes security gaps before attackers can exploit them. A structured patch management process is essential for maintaining security.',
    tips: [
      'Establish a regular patching schedule (e.g., weekly or monthly)',
      'Prioritize critical security patches for immediate deployment',
      'Test patches in staging before production rollout',
      'Maintain an inventory of all software and dependencies'
    ],
    learnMoreUrl: '/learn#patch-management'
  },
  {
    id: 'mfa-principle',
    category: 'principle',
    title: 'Multi-Factor Authentication (MFA)',
    icon: 'check_circle',
    description: 'MFA adds extra layers of security by requiring multiple forms of verification. Even if one factor is compromised, attackers cannot gain access without the others.',
    tips: [
      'Enable MFA on all critical accounts and systems',
      'Prefer authenticator apps or hardware keys over SMS',
      'Educate users on recognizing MFA phishing attempts',
      'Have backup recovery codes stored securely'
    ],
    learnMoreUrl: '/learn#mfa-principle'
  },
  // Essential Precautions
  {
    id: 'phishing',
    category: 'precaution',
    title: 'Phishing & Social Engineering',
    icon: 'shield_lock',
    description: 'Social engineering attacks manipulate people into revealing sensitive information or performing actions that compromise security. Awareness is the first line of defense.',
    tips: [
      'Verify sender identity before clicking links or attachments',
      'Look for urgency tactics and suspicious requests',
      'Report suspected phishing attempts immediately',
      'Conduct regular security awareness training'
    ],
    learnMoreUrl: '/learn#phishing'
  },
  {
    id: 'secrets',
    category: 'precaution',
    title: 'Secrets Management & Hygiene',
    icon: 'shield_lock',
    description: 'Proper handling of secrets (API keys, passwords, tokens) prevents unauthorized access. Never hardcode secrets and use dedicated tools for secure storage.',
    tips: [
      'Never commit secrets to version control',
      'Use environment variables or secret management tools',
      'Rotate secrets regularly and after any suspected breach',
      'Implement least privilege access to secret stores'
    ],
    learnMoreUrl: '/learn#secrets'
  },
  {
    id: 'backups',
    category: 'precaution',
    title: 'Reliable Data Backups',
    icon: 'shield_lock',
    description: 'Regular backups protect against data loss from ransomware, hardware failure, or accidental deletion. Follow the 3-2-1 rule for maximum protection.',
    tips: [
      'Keep 3 copies of data on 2 different media, 1 offsite',
      'Test backup restoration regularly',
      'Encrypt backups and protect access credentials',
      'Automate backup processes to ensure consistency'
    ],
    learnMoreUrl: '/learn#backups'
  },
  {
    id: 'logging',
    category: 'precaution',
    title: 'Comprehensive Logging',
    icon: 'shield_lock',
    description: 'Detailed logs enable detection of security incidents, forensic analysis, and compliance auditing. Log all security-relevant events and protect log integrity.',
    tips: [
      'Log authentication attempts, access to sensitive data, and admin actions',
      'Centralize logs for easier monitoring and analysis',
      'Set up alerts for suspicious patterns',
      'Retain logs according to compliance requirements'
    ],
    learnMoreUrl: '/learn#logging'
  }
];

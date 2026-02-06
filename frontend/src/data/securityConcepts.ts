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

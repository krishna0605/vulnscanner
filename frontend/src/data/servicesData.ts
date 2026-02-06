// Services data for the explorable Services page

export interface Service {
  id: string;
  title: string;
  icon: string;
  shortDescription: string;
  fullDescription: string;
  features: string[];
  benefits: string[];
  ctaText: string;
  ctaUrl: string;
}

export const services: Service[] = [
  {
    id: 'mdr',
    title: 'Managed Detection & Response',
    icon: 'travel_explore',
    shortDescription: '24/7 autonomous monitoring of your entire digital estate.',
    fullDescription: 'Our Managed Detection & Response service provides round-the-clock security monitoring powered by AI-driven threat detection. Our Security Operations Center (SOC) identifies, investigates, and neutralizes threats before they can impact your business operations.',
    features: [
      '24/7/365 security monitoring and alerting',
      'AI-powered threat detection and analysis',
      'Automated incident response playbooks',
      'Real-time threat intelligence integration',
      'Custom detection rules tailored to your environment',
      'Monthly security posture reports'
    ],
    benefits: [
      'Reduce mean time to detect (MTTD) by up to 80%',
      'Eliminate the need for an in-house SOC team',
      'Scale security coverage as your business grows',
      'Stay protected against zero-day threats'
    ],
    ctaText: 'Get Protected',
    ctaUrl: '/signup'
  },
  {
    id: 'audits',
    title: 'Security Audits & Compliance',
    icon: 'fact_check',
    shortDescription: 'Rigorous assessment against industry standards.',
    fullDescription: 'Our comprehensive security audits evaluate your infrastructure, policies, and procedures against leading industry frameworks. We provide a clear roadmap to compliance and help you maintain certifications.',
    features: [
      'SOC 2 Type I & Type II readiness assessments',
      'ISO 27001 gap analysis and implementation',
      'HIPAA security rule compliance audits',
      'PCI DSS compliance assessments',
      'GDPR and CCPA privacy assessments',
      'Vendor security questionnaire support'
    ],
    benefits: [
      'Accelerate your path to certification',
      'Identify and remediate compliance gaps',
      'Build customer trust with verified security',
      'Reduce regulatory and legal risks'
    ],
    ctaText: 'Start Assessment',
    ctaUrl: '/signup'
  },
  {
    id: 'incident',
    title: 'Incident Response',
    icon: 'emergency',
    shortDescription: 'Immediate expert intervention during security breaches.',
    fullDescription: 'When a security incident occurs, every minute counts. Our incident response team provides immediate expert intervention to contain threats, eradicate adversaries, and restore normal operations with minimal business impact.',
    features: [
      '15-minute response time SLA',
      'Forensic evidence collection and preservation',
      'Malware analysis and reverse engineering',
      'Breach containment and eradication',
      'Business continuity support',
      'Post-incident reporting and lessons learned'
    ],
    benefits: [
      'Minimize breach impact and downtime',
      'Preserve evidence for legal proceedings',
      'Meet regulatory breach notification requirements',
      'Learn from incidents to prevent recurrence'
    ],
    ctaText: 'Emergency Contact',
    ctaUrl: '/signup'
  },
  {
    id: 'pentest',
    title: 'Penetration Testing',
    icon: 'bug_report',
    shortDescription: 'Ethical hacking to expose vulnerabilities.',
    fullDescription: 'Our certified ethical hackers simulate real-world attacks to identify vulnerabilities in your applications, networks, and infrastructure before malicious actors can exploit them. We provide detailed findings and remediation guidance.',
    features: [
      'Web application penetration testing',
      'Mobile app security assessments (iOS & Android)',
      'Network and infrastructure testing',
      'API security testing',
      'Social engineering assessments',
      'Red team engagements'
    ],
    benefits: [
      'Identify vulnerabilities before attackers do',
      'Validate security controls effectiveness',
      'Meet compliance testing requirements',
      'Prioritize remediation with risk-based findings'
    ],
    ctaText: 'Schedule Test',
    ctaUrl: '/signup'
  },
  {
    id: 'cloud',
    title: 'Cloud Security Architecture',
    icon: 'shield',
    shortDescription: 'Secure your AWS, Azure, or GCP environments.',
    fullDescription: 'We design and implement security architectures for cloud environments that scale with your business while maintaining robust protection. Our cloud security experts help you leverage cloud-native security services effectively.',
    features: [
      'Cloud security architecture design',
      'Infrastructure as Code (IaC) security',
      'Identity and Access Management (IAM) optimization',
      'Cloud workload protection',
      'Container and Kubernetes security',
      'Multi-cloud security strategy'
    ],
    benefits: [
      'Reduce cloud security misconfigurations by 90%',
      'Enable secure cloud adoption and migration',
      'Optimize cloud security spending',
      'Maintain compliance in dynamic environments'
    ],
    ctaText: 'Secure My Cloud',
    ctaUrl: '/signup'
  },
  {
    id: 'vciso',
    title: 'Virtual CISO (vCISO)',
    icon: 'badge',
    shortDescription: 'Executive-level security leadership on demand.',
    fullDescription: 'Get access to experienced security executives without the full-time cost. Our vCISO service provides strategic security leadership, board-level reporting, and program management tailored to your organization\'s needs.',
    features: [
      'Security strategy development',
      'Board and executive security briefings',
      'Security program management',
      'Vendor and third-party risk management',
      'Security budget planning and optimization',
      'Security awareness program oversight'
    ],
    benefits: [
      'Access CISO expertise at a fraction of the cost',
      'Align security with business objectives',
      'Demonstrate security leadership to stakeholders',
      'Scale security leadership as needed'
    ],
    ctaText: 'Talk to a vCISO',
    ctaUrl: '/signup'
  }
];

export const getServiceById = (id: string): Service | undefined => {
  return services.find(s => s.id === id);
};

export const site = {
  name: 'Prysm Intelligence',
  hero: 'See the relationships behind financial risk.',
  description: 'An evidence-led workspace for investigating financial relationships, reviewing model signals, and making accountable decisions.',
  company: 'Abyssinia Associates',
  email: 'contact@example.com',
  github: 'https://github.com/',
};

export const navGroups = [
  { label: 'Research', href: '/research', items: [['Ethical AI','/research/ethical-ai'],['Fraud detection','/research/fraud-detection'],['Modeling','/research/modeling']] },
  { label: 'Report', href: '/report', items: [['Bug report','/report/bug'],['Resolution guide','/report/resolution-guide'],['Beta program','/beta'],['Contribute','/contribute']] },
  { label: 'Academy', href: '/academy', items: [['Data science','/academy/data-science'],['Python','/academy/python'],['Opportunities','/academy/opportunities'],['Institutions','/academy/institutions'],['Rules','/academy/rules']] },
  { label: 'Intelligence', href: '/intelligence', items: [['Models','/intelligence/models'],['Data','/intelligence/data'],['Playground','/intelligence/playground']] },
];

export const pageContent = {
  '/research': ['Research at Prysm','Methods should be open to scrutiny. Explore how Prysm approaches responsible financial intelligence, model interpretation, and human-led investigation.'],
  '/research/ethical-ai': ['Ethical AI','Responsible intelligence begins with provenance, consent, constrained access, and human oversight. Model outputs are signals, not verdicts, and false positives remain a material risk.'],
  '/research/fraud-detection': ['Fraud detection','Prysm brings transaction signals, relationships, evidence, and temporal context into one investigative workflow without presenting probability as certainty.'],
  '/research/modeling': ['Modeling','Graph models surface patterns across connected entities. Their outputs remain bounded by training data, evaluation scope, cutoff time, and the quality of available evidence.'],
  '/report': ['Report and support','Find reporting channels, practical resolution guidance, beta information, and ways to contribute.'],
  '/report/resolution-guide': ['Resolution guide','Record the request ID, note the action and time, retry transient failures once, then share the sanitized details with support. Never include passwords or access tokens.'],
  '/beta': ['Beta program','Help test workflows, accessibility, and clarity. Beta participation does not grant access to restricted data and remains subject to review.'],
  '/contribute': ['Contribute','Prysm welcomes careful contributions to research, documentation, interface quality, and responsible intelligence practice. Repository details are editable in the site configuration.'],
  '/academy': ['Prysm Academy','Practical learning paths for people building the technical and analytical foundations of responsible intelligence work.'],
  '/academy/data-science': ['Data Science Bootcamp','A planned learning track covering data quality, exploratory analysis, evaluation, graph concepts, and responsible interpretation.'],
  '/academy/python': ['Python Programming','A planned foundation in readable Python, data structures, testing, analysis workflows, and reproducible research.'],
  '/academy/opportunities': ['Opportunities','Future learning, research, and contributor opportunities will be published here after verification.'],
  '/academy/institutions': ['Institutions','A future space for verified educational collaboration. No institutional partnerships are currently claimed.'],
  '/academy/rules': ['Rules and regulations','Learning spaces should be rigorous, respectful, privacy-aware, and honest about authorship and evidence.'],
  '/intelligence': ['Intelligence, with context','Understand the models, data representation, and safe demonstrations behind Prysm without exposing production information.'],
  '/intelligence/models': ['Model intelligence','Prysm separates model metadata, evaluation scope, outputs, and limitations so analysts can understand what a signal does and does not mean.'],
  '/intelligence/data': ['Data representation','Subjects, events, relationships, findings, and evidence retain identifiers, timestamps, provenance, and classification boundaries.'],
  '/intelligence/playground': ['Safe playground','Explore a synthetic relationship network. This demonstration contains no customer, subject, or production data.'],
  '/terms': ['Terms of agreement','This editable placeholder describes acceptable use, controlled access, responsible interpretation, and user obligations. Legal review is required before release.'],
  '/privacy': ['Privacy policy','This editable placeholder describes minimal data collection, account security, audit records, retention, and user rights. Legal review is required before release.'],
};

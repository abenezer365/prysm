const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:4000/api/v1';

export class ApiError extends Error {
  constructor(message, { status, code, details, requestId } = {}) { super(message); this.name='ApiError'; this.status=status; this.code=code; this.details=details; this.requestId=requestId; }
}

export async function request(path, { token, body, signal, headers, ...options } = {}) {
  const response = await fetch(`${API_BASE}${path}`, { ...options, signal, headers: { ...(body ? {'Content-Type':'application/json'} : {}), ...(token ? {Authorization:`Bearer ${token}`} : {}), ...headers }, body: body ? JSON.stringify(body) : undefined });
  const requestId = response.headers.get('x-request-id');
  const payload = response.status === 204 ? null : await response.json().catch(() => null);
  if (!response.ok) { const err=payload?.error || {}; throw new ApiError(err.message || 'The service could not complete this request.', { status:response.status, code:err.code, details:err.details, requestId:err.requestId || requestId }); }
  return payload;
}

export const api = {
  login: body => request('/auth/login',{method:'POST',body}), logout: token => request('/auth/logout',{method:'POST',token}), refresh: refreshToken => request('/auth/refresh',{method:'POST',body:{refreshToken}}),
  me: token => request('/auth/me',{token}), permissions: token => request('/me/permissions',{token}), clearance: token => request('/me/clearance',{token}),
  apply: body => request('/applications',{method:'POST',body}), contact: body => request('/contact',{method:'POST',body}), bugReport: body => request('/bug-reports',{method:'POST',body}), betaApply: body => request('/beta/applications',{method:'POST',body}), news: () => request('/news'), datasets: () => request('/datasets'), publicChat: body => request('/chat/public',{method:'POST',body}), authorizedChat: (token,body) => request('/chat/authorized',{method:'POST',token,body}),
  health: () => request('/health'), readiness: () => request('/health/ready'), dependencies: token => request('/health/dependencies',{token}),
  search: (token,body) => request('/search',{method:'POST',token,body}), subject: (token,id) => request(`/subjects/${id}`,{token}), subjectProfile: (token,id) => request(`/subjects/${id}/profile`,{token}),
  dashboard: token => request('/dashboard/summary',{token}), topSuspects: token => request('/dashboard/top-suspects',{token}), activity: (token,query='') => request(`/activity${query}`,{token}), users: (token,query='') => request(`/users${query}`,{token}), updateUser: (token,id,body) => request(`/users/${id}`,{method:'PATCH',token,body}), settings: (token,body) => request('/me/settings',{method:'PATCH',token,body}), changePassword: (token,body) => request('/me/password',{method:'POST',token,body}), investigations: token => request('/investigations',{token}), investigation: (token,id) => request(`/investigations/${id}`,{token}), createInvestigation: (token,body) => request('/investigations',{method:'POST',token,body}), analyze: (token,id) => request(`/investigations/${id}/analyze`,{method:'POST',token,body:{}}),
  graph: (token,id,params='') => request(`/graph/subjects/${id}/subgraph${params}`,{token}), evidence: (token,id) => request(`/evidence/${id}`,{token}), models: token => request('/models',{token}), audit: token => request('/audit/events',{token}), ragIngest: (token,body) => request('/rag/ingest',{method:'POST',token,body}), ragDocuments: (token,query='') => request(`/rag/documents${query}`,{token}), updateRagDocument: (token,id,enabled) => request(`/rag/documents/${id}`,{method:'PATCH',token,body:{enabled}}), ragConversations: (token,query='') => request(`/rag/conversations${query}`,{token}),
  adminNews: token => request('/news/admin',{token}), createNews: (token,body) => request('/news',{method:'POST',token,body}), updateNews: (token,id,body) => { const {slug,...editable}=body; return request(`/news/${id}`,{method:'PATCH',token,body:editable}); },
  applications: (token,query='') => request(`/applications${query}`,{token}), reviewApplication: (token,id,body) => request(`/applications/${id}`,{method:'PATCH',token,body}), bugReports: (token,query='') => request(`/bug-reports${query}`,{token}), updateBug: (token,id,body) => request(`/bug-reports/${id}`,{method:'PATCH',token,body}), betaApplications: (token,query='') => request(`/beta/applications${query}`,{token}), reviewBeta: (token,id,body) => request(`/beta/applications/${id}`,{method:'PATCH',token,body}), contributors: (token,query='') => request(`/contributors/applications${query}`,{token}), reviewContributor: (token,id,body) => request(`/contributors/applications/${id}`,{method:'PATCH',token,body}),
};

export function friendlyError(error) { if (!error) return ''; const byStatus={400:'Check the information and try again.',401:'Your session has expired. Please sign in again.',403:'Your account does not have access to this resource.',404:'The requested resource was not found.',409:'This action conflicts with the current resource state.',413:'The submitted content is too large.',429:'Too many requests. Please wait and try again.',502:'An upstream intelligence service is unavailable.',503:'A required Prysm service is temporarily unavailable.'}; return byStatus[error.status] || error.message || 'Something went wrong.'; }

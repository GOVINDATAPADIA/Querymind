const API_BASE = '/api';

export async function sendQuery(question) {
  const response = await fetch(`${API_BASE}/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question }),
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: 'Network error' }));
    throw new Error(error.error || `HTTP ${response.status}`);
  }
  return response.json();
}

export async function fetchHealth() {
  try {
    const response = await fetch(`${API_BASE}/health`);
    if (!response.ok) throw new Error('Health check failed');
    return response.json();
  } catch {
    return { status: 'error', db_connected: false, llm_connected: false };
  }
}

export async function fetchSchema() {
  try {
    const response = await fetch(`${API_BASE}/schema`);
    if (!response.ok) throw new Error('Schema fetch failed');
    return response.json();
  } catch {
    return { tables: [] };
  }
}

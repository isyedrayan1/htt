// Simple frontend adapter for ANTIGRAVITY ML endpoints
// Usage: include this script in your frontend; adjust baseUrl as needed.

const baseUrl = window.__ANTIGRAVITY_API__ || 'http://localhost:8000';

async function handleErrorResponse(resp) {
  const contentType = resp.headers.get('content-type') || '';
  let body = null;
  try {
    if (contentType.includes('application/json')) {
      body = await resp.json();
    } else {
      body = await resp.text();
    }
  } catch (e) {
    body = await resp.text();
  }

  // Extract trace_id if present to show to user or log for support
  const traceId = body && body.trace_id ? body.trace_id : null;

  return {
    ok: resp.ok,
    status: resp.status,
    body,
    traceId,
  };
}

export async function fetchDPTAD(vehicleId, sessionFilter = null) {
  const params = new URLSearchParams();
  if (sessionFilter) params.set('session_filter', sessionFilter);

  const url = `${baseUrl}/api/ml/dptad/analyze/${encodeURIComponent(vehicleId)}?${params.toString()}`;
  const resp = await fetch(url, { method: 'GET', headers: { 'Accept': 'application/json' } });
  if (!resp.ok) return await handleErrorResponse(resp);
  const data = await resp.json();
  return { ok: true, data };
}

export async function fetchSIWTL(vehicleId, opts = { include_sectors: true, include_telemetry: false }) {
  const params = new URLSearchParams();
  params.set('include_sectors', opts.include_sectors ? 'true' : 'false');
  params.set('include_telemetry', opts.include_telemetry ? 'true' : 'false');

  const url = `${baseUrl}/api/ml/siwtl/calculate/${encodeURIComponent(vehicleId)}?${params.toString()}`;
  const resp = await fetch(url, { method: 'GET', headers: { 'Accept': 'application/json' } });
  if (!resp.ok) return await handleErrorResponse(resp);
  const data = await resp.json();
  return { ok: true, data };
}

export async function fetchComprehensive(vehicleId) {
  const url = `${baseUrl}/api/ml/comprehensive/${encodeURIComponent(vehicleId)}`;
  const resp = await fetch(url, { method: 'GET', headers: { 'Accept': 'application/json' } });
  if (!resp.ok) return await handleErrorResponse(resp);
  const data = await resp.json();
  return { ok: true, data };
}

// Simple renderer helpers (DOM must provide container elements)
export function renderAnomalies(containerEl, anomalies) {
  containerEl.innerHTML = '';
  if (!anomalies || anomalies.length === 0) {
    containerEl.textContent = 'No anomalies detected';
    return;
  }
  const ul = document.createElement('ul');
  anomalies.forEach(a => {
    const li = document.createElement('li');
    li.textContent = `${new Date(a.timestamp).toLocaleString ? new Date(a.timestamp).toLocaleString() : a.timestamp} - ${a.type} (${a.signal}) severity:${a.severity.toFixed(2)} - ${a.description || ''}`;
    ul.appendChild(li);
  });
  containerEl.appendChild(ul);
}

export function renderSIWTL(containerEl, siwtlResult) {
  containerEl.innerHTML = '';
  if (!siwtlResult || !siwtlResult.siwtl_lap) {
    containerEl.textContent = 'No SIWTL target available';
    return;
  }
  const p = document.createElement('p');
  p.textContent = `SIWTL target: ${siwtlResult.siwtl_lap.toFixed(3)}s (potential gain: ${siwtlResult.potential_gain_sec || 0}s, achievability: ${siwtlResult.achievability_score || 0})`;
  containerEl.appendChild(p);
}

// Example usage (uncomment in a browser environment):
// (async () => {
//   const d = await fetchDPTAD('GR86-030-18');
//   if (!d.ok) console.error('Error', d.body, 'trace', d.traceId);
//   else renderAnomalies(document.getElementById('anomalies'), d.data.anomalies);
//
//   const s = await fetchSIWTL('GR86-030-18');
//   if (!s.ok) console.error('Error', s.body, 'trace', s.traceId);
//   else renderSIWTL(document.getElementById('siwtl'), s.data.result);
// })();

export default {
  fetchDPTAD,
  fetchSIWTL,
  fetchComprehensive,
  renderAnomalies,
  renderSIWTL,
};

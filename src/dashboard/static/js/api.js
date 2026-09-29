// Centralized API handler
async function fetchApi(url, options = {}) {
  try {
    const res = await fetch(url, options);
    if (!res.ok) throw new Error(`API Error: ${res.status}`);
    const data = await res.json();
    return { ok: true, data, error: null };
  } catch (error) {
    return { ok: false, data: null, error: error.message };
  }
}

export const fetchHierarchy = () => fetchApi('/api/geo/hierarchy');
export const fetchPanchayatForecast = (gp_code) => fetchApi(`/api/panchayat/${gp_code}/forecast`);
export const fetchModelComparison = () => fetchApi('/api/model-comparison');
export const fetchSystemStatus = () => fetchApi('/api/system-status');
export const fetchFeedbackSummary = () => fetchApi('/api/feedback/summary');
export const fetchCrops = () => fetchApi('/api/crops');
export const fetchEvaluation = () => fetchApi('/api/evaluation');

export const postAdvisory = (payload) => fetchApi('/api/advisory', {
  method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload)
});
export const postChat = (payload) => fetchApi('/api/chat', {
  method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload)
});
export const postRisk = (payload) => fetchApi('/api/risk', {
  method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload)
});
export const postFeedback = (payload) => fetchApi('/api/feedback', {
  method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload)
});
export const postDownscaleRun = (gp_code) => fetchApi('/api/downscale/run', {
  method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({gp_code})
});

// Fallback to static geojson files from the previous structure
export const fetchPanchayatsGeojson = () => fetchApi('/static/data/pune_panchayats_web.geojson');
export const fetchBlocksGeojson = () => fetchApi('/static/data/pune_blocks_web.geojson');

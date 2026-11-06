/**
 * API Client for Route Accident Risk Prediction System
 * Communicates with FastAPI backend on /api/*
 */

const API_BASE = '/api';

export async function fetchHealth() {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error('Health check failed');
  return res.json();
}

export async function searchLocations(query) {
  if (!query || query.trim().length < 2) return [];
  const res = await fetch(`${API_BASE}/search?q=${encodeURIComponent(query.trim())}`);
  if (!res.ok) throw new Error('Location search failed');
  const data = await res.json();
  return data.results || [];
}

export async function fetchLiveWeather(lat, lon) {
  const res = await fetch(`${API_BASE}/live-weather?lat=${lat}&lon=${lon}`);
  if (!res.ok) throw new Error('Weather fetch failed');
  return res.json();
}

export async function analyzeRoute({
  originName,
  destinationName,
  originCoords,
  destCoords,
  departureHour,
  roadType,
  weatherOverride,
  plannedSpeedKmh = 60,
  vehicleType = 'Car / SUV',
  roadCondition = 'Dry Asphalt'
}) {
  const payload = {
    origin_name: originName,
    destination_name: destinationName,
    origin_coords: originCoords,
    dest_coords: destCoords,
    departure_hour: parseInt(departureHour, 10),
    road_type: roadType,
    weather_override: weatherOverride || null,
    planned_speed_kmh: parseInt(plannedSpeedKmh, 10),
    vehicle_type: vehicleType,
    road_condition: roadCondition
  };

  const res = await fetch(`${API_BASE}/analyze-route`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Route analysis failed' }));
    throw new Error(err.detail || 'Route analysis failed');
  }

  return res.json();
}

export async function fetchBlackspots() {
  const res = await fetch(`${API_BASE}/blackspots`);
  if (!res.ok) throw new Error('Blackspots fetch failed');
  const data = await res.json();
  return data.clusters || [];
}

export async function fetchModelPerformance() {
  const res = await fetch(`${API_BASE}/model-performance`);
  if (!res.ok) throw new Error('Model performance fetch failed');
  return res.json();
}

export async function fetchEdaCharts() {
  const res = await fetch(`${API_BASE}/eda-charts`);
  if (!res.ok) throw new Error('EDA charts fetch failed');
  const data = await res.json();
  return data.charts || [];
}

export async function fetchAccidentsSample(limit = 50) {
  const res = await fetch(`${API_BASE}/accidents-sample?limit=${limit}`);
  if (!res.ok) throw new Error('Sample fetch failed');
  return res.json();
}

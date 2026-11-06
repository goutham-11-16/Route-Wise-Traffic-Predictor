import React, { useEffect, useState, useRef } from 'react';
import { MapContainer, TileLayer, Polyline, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import {
  Play,
  Pause,
  RotateCcw,
  Eye,
  EyeOff,
  Navigation,
  AlertOctagon,
  Gauge,
  Compass,
  Crosshair
} from 'lucide-react';

// Custom DivIcons for Origin and Destination Pins with floating animation
const createPinIcon = (color, text) => {
  return L.divIcon({
    className: 'custom-pin-marker',
    html: `
      <div class="floating-pin-anim" style="
        background-color: ${color};
        color: white;
        width: 32px;
        height: 32px;
        border-radius: 50% 50% 50% 0;
        transform: rotate(-45deg);
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 6px 15px rgba(0,0,0,0.6);
        border: 2px solid white;
      ">
        <span style="transform: rotate(45deg); font-size: 13px; font-weight: 800;">${text}</span>
      </div>
    `,
    iconSize: [32, 32],
    iconAnchor: [16, 32],
    popupAnchor: [0, -32]
  });
};

const originIcon = createPinIcon('#10b981', 'A');
const destIcon = createPinIcon('#ef4444', 'B');

// Custom Radar Ripple Icon for Blackspots with Regulatory Speed Limit Sign
const createRadarBlackspotIcon = (riskLevel, clusterId, stopSpeedLimit = 30) => {
  const isHigh = riskLevel === 'High';
  const emitterClass = isHigh ? 'radar-emitter-high' : 'radar-emitter-med';
  const coreColor = isHigh ? '#ef4444' : '#f59e0b';

  return L.divIcon({
    className: 'custom-radar-marker',
    html: `
      <div class="radar-emitter ${emitterClass}" style="display: flex; flex-direction: column; align-items: center; justify-content: center;">
        <!-- Circular Speed Limit Sign at Hazard Stop -->
        <div style="
          background-color: #ffffff;
          color: #1e293b;
          border: 2px solid #ef4444;
          border-radius: 50%;
          width: 22px;
          height: 22px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 10px;
          font-weight: 900;
          font-family: monospace;
          margin-bottom: -4px;
          box-shadow: 0 3px 8px rgba(0,0,0,0.6);
          z-index: 10;
        ">
          ${stopSpeedLimit}
        </div>
        <div class="radar-wave"></div>
        <div style="
          width: 14px;
          height: 14px;
          background-color: ${coreColor};
          border: 2px solid #ffffff;
          border-radius: 50%;
          box-shadow: 0 0 8px ${coreColor};
          z-index: 2;
        "></div>
      </div>
    `,
    iconSize: [24, 34],
    iconAnchor: [12, 24],
    popupAnchor: [0, -22]
  });
};

// Custom Animated Vehicle Marker
const createVehicleIcon = (angle = 0) => {
  return L.divIcon({
    className: 'custom-vehicle-marker',
    html: `
      <div class="vehicle-glowing-marker" style="
        width: 36px;
        height: 36px;
        background: linear-gradient(135deg, #0284c7, #38bdf8);
        border: 2px solid #ffffff;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        box-shadow: 0 4px 15px rgba(2, 132, 199, 0.7);
        transform: rotate(${angle}deg);
        transition: transform 0.15s ease-out;
      ">
        <span style="font-size: 18px;">🚗</span>
      </div>
    `,
    iconSize: [36, 36],
    iconAnchor: [18, 18],
    popupAnchor: [0, -20]
  });
};

// Calculate heading angle between two points
function calculateBearing(lat1, lon1, lat2, lon2) {
  const y = Math.sin(lon2 - lon1) * Math.cos(lat2);
  const x =
    Math.cos(lat1) * Math.sin(lat2) -
    Math.sin(lat1) * Math.cos(lat2) * Math.cos(lon2 - lon1);
  const brng = Math.atan2(y, x);
  return ((brng * 180) / Math.PI + 360) % 360;
}

// Controller for map camera with smooth cinematic flyToBounds
function MapCameraController({ bounds, followCoords }) {
  const map = useMap();
  const prevBoundsRef = useRef(null);

  useEffect(() => {
    if (bounds && bounds.length > 0) {
      const boundsStr = JSON.stringify(bounds);
      if (prevBoundsRef.current !== boundsStr) {
        prevBoundsRef.current = boundsStr;
        map.flyToBounds(bounds, {
          padding: [55, 55],
          maxZoom: 14,
          duration: 1.4,
          easeLinearity: 0.25
        });
      }
    }
  }, [bounds, map]);

  useEffect(() => {
    if (followCoords) {
      map.panTo(followCoords, { animate: true, duration: 0.2 });
    }
  }, [followCoords, map]);

  return null;
}

export default function RouteMap({
  routeData,
  origin,
  destination,
  blackspots = [],
  speedMetrics = null
}) {
  const [showBlackspots, setShowBlackspots] = useState(true);
  const [isDriving, setIsDriving] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [playbackSpeed, setPlaybackSpeed] = useState(2); // 1x, 2x, 4x
  const [followVehicle, setFollowVehicle] = useState(false);

  const stopSpeedLimit = speedMetrics?.blackspot_stop_speed_limit_kmh || 30;

  const routePoints = routeData?.route_points || [];
  const totalPoints = routePoints.length;
  const riskColor = routeData?.risk_color || '#3b82f6';
  const riskTier = routeData?.journey_risk_tier || 'ANALYZED ROUTE';

  // Vehicle position & bearing
  const vehiclePos =
    totalPoints > 0 ? routePoints[Math.min(currentStep, totalPoints - 1)] : null;
  const nextPos =
    totalPoints > 1 && currentStep < totalPoints - 1
      ? routePoints[currentStep + 1]
      : vehiclePos;

  const vehicleBearing =
    vehiclePos && nextPos
      ? calculateBearing(
          (vehiclePos[0] * Math.PI) / 180,
          (vehiclePos[1] * Math.PI) / 180,
          (nextPos[0] * Math.PI) / 180,
          (nextPos[1] * Math.PI) / 180
        )
      : 0;

  // Animation driving loop
  useEffect(() => {
    if (!isDriving || totalPoints < 2) return;

    const intervalTime = Math.max(30, Math.floor(120 / playbackSpeed));
    const timer = setInterval(() => {
      setCurrentStep((prev) => {
        if (prev >= totalPoints - 1) {
          setIsDriving(false);
          return totalPoints - 1;
        }
        return prev + 1;
      });
    }, intervalTime);

    return () => clearInterval(timer);
  }, [isDriving, totalPoints, playbackSpeed]);

  // Reset simulation when route changes
  useEffect(() => {
    setCurrentStep(0);
    setIsDriving(false);
  }, [routePoints]);

  const handlePlayPause = () => {
    if (currentStep >= totalPoints - 1) {
      setCurrentStep(0);
    }
    setIsDriving(!isDriving);
  };

  const handleReset = () => {
    setIsDriving(false);
    setCurrentStep(0);
  };

  // Traveled portion of route points
  const traveledPoints =
    totalPoints > 0 ? routePoints.slice(0, currentStep + 1) : [];

  // Calculate bounding box
  let bounds = [];
  if (routePoints.length > 0) {
    bounds = routePoints;
  } else if (origin?.coords && destination?.coords) {
    bounds = [origin.coords, destination.coords];
  }

  const defaultCenter = origin?.coords || [28.6139, 77.2090];
  const progressPct =
    totalPoints > 1 ? Math.round((currentStep / (totalPoints - 1)) * 100) : 0;
  const currentKm =
    routeData?.distance_km && totalPoints > 1
      ? ((routeData.distance_km * currentStep) / (totalPoints - 1)).toFixed(1)
      : '0.0';

  // Helper: Haversine distance in km
  const getDistanceKm = (lat1, lon1, lat2, lon2) => {
    const R = 6371;
    const dLat = ((lat2 - lat1) * Math.PI) / 180;
    const dLon = ((lon2 - lon1) * Math.PI) / 180;
    const a =
      Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.cos((lat1 * Math.PI) / 180) *
        Math.cos((lat2 * Math.PI) / 180) *
        Math.sin(dLon / 2) *
        Math.sin(dLon / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c;
  };

  // Find nearest blackspot to vehicle in real-time
  const nearestHazard = vehiclePos && isDriving
    ? blackspots
        .map((b) => ({
          ...b,
          distMeters: Math.round(getDistanceKm(vehiclePos[0], vehiclePos[1], b.lat, b.lon) * 1000)
        }))
        .filter((b) => b.distMeters <= 750)
        .sort((a, b) => a.distMeters - b.distMeters)[0]
    : null;

  return (
    <div className="relative w-full h-[540px] rounded-2xl overflow-hidden border border-slate-700/80 shadow-2xl bg-slate-950">
      {/* Top Floating Controls Bar */}
      <div className="absolute top-3 left-3 right-3 z-[400] flex flex-wrap items-center justify-between gap-2 pointer-events-auto">
        {/* Risk Badge & Route Distance */}
        <div className="bg-slate-900/90 backdrop-blur-md px-3.5 py-1.5 rounded-xl border border-slate-700/80 shadow-lg flex items-center gap-2 text-xs">
          <div
            className="w-3 h-3 rounded-full animate-pulse"
            style={{ backgroundColor: riskColor }}
          ></div>
          <span className="font-extrabold text-white tracking-wide">{riskTier}</span>
          {routeData?.distance_km && (
            <span className="text-slate-400 font-mono pl-1.5 border-l border-slate-700">
              {routeData.distance_km} km • {routeData.estimated_minutes} mins
            </span>
          )}
        </div>

        {/* Action Controls: Drive Simulation & Blackspots Toggle */}
        <div className="flex items-center gap-1.5 bg-slate-900/90 backdrop-blur-md p-1 rounded-xl border border-slate-700/80 shadow-lg text-xs">
          {/* Play / Pause */}
          <button
            onClick={handlePlayPause}
            disabled={totalPoints < 2}
            className={`flex items-center gap-1 px-2.5 py-1.5 rounded-lg font-bold transition ${
              isDriving
                ? 'bg-amber-600 text-white shadow-md'
                : 'bg-blue-600 hover:bg-blue-500 text-white shadow-md shadow-blue-600/30'
            }`}
            title={isDriving ? 'Pause Trip' : 'Start Simulation'}
          >
            {isDriving ? <Pause className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5" />}
            <span>{isDriving ? 'Pause' : 'Drive'}</span>
          </button>

          {/* Reset */}
          <button
            onClick={handleReset}
            className="p-1.5 bg-slate-800 hover:bg-slate-700 rounded-lg text-slate-300 transition"
            title="Reset to Origin"
          >
            <RotateCcw className="w-3.5 h-3.5" />
          </button>

          {/* Playback Speed cycle */}
          <button
            onClick={() => {
              const speeds = [1, 2, 4];
              const nextIdx = (speeds.indexOf(playbackSpeed) + 1) % speeds.length;
              setPlaybackSpeed(speeds[nextIdx]);
            }}
            className="px-2 py-1 bg-slate-800 hover:bg-slate-700 rounded-lg font-mono text-[11px] font-bold text-sky-400"
            title="Simulation Speed"
          >
            {playbackSpeed}x
          </button>

          {/* Camera Follow Toggle */}
          <button
            onClick={() => setFollowVehicle(!followVehicle)}
            className={`px-2 py-1 rounded-lg text-[11px] font-bold transition flex items-center gap-1 ${
              followVehicle
                ? 'bg-sky-600/30 text-sky-300 border border-sky-500/50'
                : 'bg-slate-800 text-slate-400 hover:text-slate-200'
            }`}
            title="Auto Follow Car"
          >
            <span>Follow</span>
          </button>

          {/* Toggle Blackspots */}
          <button
            onClick={() => setShowBlackspots(!showBlackspots)}
            className={`px-2 py-1 rounded-lg text-[11px] font-semibold transition ${
              showBlackspots
                ? 'bg-rose-950/70 text-rose-300 border border-rose-800/80'
                : 'bg-slate-800 text-slate-400 hover:text-slate-200'
            }`}
          >
            Blackspots ({blackspots.length})
          </button>
        </div>
      </div>

      {/* Real-Time Hazard Proximity Alert HUD Banner */}
      {nearestHazard && (
        <div className="absolute top-16 left-3 right-3 z-[400] bg-rose-950/90 backdrop-blur-md border border-rose-500 text-white px-4 py-2 rounded-xl shadow-2xl flex items-center justify-between animate-bounce">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-full bg-rose-600 flex items-center justify-center font-bold text-sm shadow-md">
              {stopSpeedLimit}
            </div>
            <div>
              <div className="font-bold text-xs text-rose-200 flex items-center gap-1.5">
                <AlertOctagon className="w-3.5 h-3.5 text-rose-400" />
                <span>APPROACHING ACCIDENT BLACKSPOT (#{nearestHazard.cluster_id + 1})</span>
              </div>
              <div className="text-[11px] text-slate-300">
                Distance: <span className="font-mono font-bold text-rose-300">{nearestHazard.distMeters}m</span> away. Enforce mandatory stop speed limit of <span className="font-mono font-bold text-yellow-300">{stopSpeedLimit} km/h</span>.
              </div>
            </div>
          </div>
          <div className="hidden sm:block text-[11px] bg-rose-900/60 px-2.5 py-1 rounded-lg font-mono text-rose-200 border border-rose-700">
            Slow Down
          </div>
        </div>
      )}

      {/* Bottom Floating Telemetry Bar */}
      {totalPoints > 0 && (
        <div className="absolute bottom-3 left-3 z-[400] bg-slate-900/90 backdrop-blur-md px-3 py-2 rounded-xl border border-slate-700/80 text-xs shadow-xl flex items-center gap-3">
          <div className="flex items-center gap-1.5 text-sky-400 font-mono font-bold">
            <Gauge className="w-3.5 h-3.5" />
            <span>{currentKm} / {routeData?.distance_km || '0.0'} km</span>
          </div>
          {/* Progress bar */}
          <div className="w-24 sm:w-32 bg-slate-800 h-1.5 rounded-full overflow-hidden">
            <div
              style={{ width: `${progressPct}%` }}
              className="h-full bg-gradient-to-r from-blue-500 to-sky-400 transition-all duration-150"
            ></div>
          </div>
          <span className="font-mono text-slate-400 text-[11px]">{progressPct}%</span>
          {isDriving && (
            <span className="flex items-center gap-1 text-[10px] text-emerald-400 font-bold uppercase">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-ping"></span>
              Live Cruising
            </span>
          )}
        </div>
      )}

      {/* Bottom Attribution Notice */}
      <div className="absolute bottom-3 right-3 z-[400] bg-slate-900/80 backdrop-blur-sm px-2.5 py-1 rounded-lg border border-slate-800 text-[10px] text-slate-400 pointer-events-none">
        Routing: <span className="text-blue-400 font-medium">{routeData?.routing_source || 'OSRM Live Road Engine'}</span>
      </div>

      <MapContainer
        center={defaultCenter}
        zoom={11}
        scrollWheelZoom={true}
        style={{ height: '100%', width: '100%' }}
      >
        <MapCameraController
          bounds={bounds}
          followCoords={followVehicle && vehiclePos ? vehiclePos : null}
        />

        {/* Free OpenStreetMap Tiles */}
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {/* 1. Underlying Dark Glow Polyline */}
        {routePoints.length > 1 && (
          <Polyline
            positions={routePoints}
            pathOptions={{
              color: '#090d16',
              weight: 8,
              opacity: 0.6
            }}
          />
        )}

        {/* 2. Main Color-Coded Route Line */}
        {routePoints.length > 1 && (
          <Polyline
            positions={routePoints}
            pathOptions={{
              color: riskColor,
              weight: 5,
              opacity: 0.85
            }}
          />
        )}

        {/* 3. ANIMATED FLOWING DASH STREAM OVERLAY (Forward flow) */}
        {routePoints.length > 1 && (
          <Polyline
            positions={routePoints}
            pathOptions={{
              color: '#ffffff',
              weight: 3.5,
              opacity: 0.95,
              className: 'route-stream-animation'
            }}
          />
        )}

        {/* 4. Active Traveled Segment Polyline (Cyan glow ahead of car) */}
        {traveledPoints.length > 1 && (
          <Polyline
            positions={traveledPoints}
            pathOptions={{
              color: '#38bdf8',
              weight: 5,
              opacity: 0.95
            }}
          />
        )}

        {/* Origin Marker (Floating animation) */}
        {origin?.coords && (
          <Marker position={origin.coords} icon={originIcon}>
            <Popup>
              <div className="p-1 text-slate-900">
                <div className="font-bold text-xs text-emerald-600">Start Location (A)</div>
                <div className="font-semibold text-xs mt-0.5">{origin.name}</div>
                <div className="text-[10px] text-slate-500 font-mono mt-0.5">
                  [{origin.coords[0].toFixed(4)}, {origin.coords[1].toFixed(4)}]
                </div>
              </div>
            </Popup>
          </Marker>
        )}

        {/* Destination Marker (Floating animation) */}
        {destination?.coords && (
          <Marker position={destination.coords} icon={destIcon}>
            <Popup>
              <div className="p-1 text-slate-900">
                <div className="font-bold text-xs text-rose-600">Destination (B)</div>
                <div className="font-semibold text-xs mt-0.5">{destination.name}</div>
                <div className="text-[10px] text-slate-500 font-mono mt-0.5">
                  [{destination.coords[0].toFixed(4)}, {destination.coords[1].toFixed(4)}]
                </div>
              </div>
            </Popup>
          </Marker>
        )}

        {/* Animated Cruising Vehicle Marker */}
        {vehiclePos && (
          <Marker
            position={vehiclePos}
            icon={createVehicleIcon(vehicleBearing)}
            zIndexOffset={1000}
          >
            <Popup>
              <div className="p-1 text-slate-900">
                <div className="font-bold text-xs text-sky-600 flex items-center gap-1">
                  <span>🚗 Autonomous Route Navigator</span>
                </div>
                <div className="text-xs font-semibold mt-1">
                  Progress: <span className="font-mono text-blue-600">{progressPct}%</span> ({currentKm} km)
                </div>
                <div className="text-[10px] text-slate-500 font-mono mt-0.5">
                  GPS: [{vehiclePos[0].toFixed(5)}, {vehiclePos[1].toFixed(5)}]
                </div>
              </div>
            </Popup>
          </Marker>
        )}

        {/* 20 K-Means Accident Blackspots with Pulsing Radar Rings & Regulatory Speed Limits */}
        {showBlackspots &&
          blackspots.map((cluster) => {
            return (
              <Marker
                key={cluster.cluster_id}
                position={[cluster.lat, cluster.lon]}
                icon={createRadarBlackspotIcon(cluster.risk_level, cluster.cluster_id, stopSpeedLimit)}
              >
                <Popup>
                  <div className="p-1 text-slate-900 max-w-[200px]">
                    <div className="font-bold text-xs flex items-center gap-1 text-rose-700">
                      <AlertOctagon className="w-3.5 h-3.5" />
                      <span>Accident Blackspot #{cluster.cluster_id + 1}</span>
                    </div>
                    <div className="mt-1.5 p-1.5 bg-rose-50 border border-rose-200 rounded-lg flex items-center justify-between">
                      <span className="text-[11px] font-bold text-rose-900">Stop Speed Limit:</span>
                      <span className="text-xs font-mono font-black text-rose-600 bg-white px-1.5 py-0.5 rounded border border-rose-300">
                        {stopSpeedLimit} km/h
                      </span>
                    </div>
                    <div className="text-xs font-semibold mt-1.5">
                      Historical Severity Score:{' '}
                      <span className="text-rose-600 font-mono font-bold">
                        {cluster.risk_score}
                      </span>{' '}
                      / 3.0
                    </div>
                    <div className="text-[11px] text-slate-600">
                      Risk Tier:{' '}
                      <span
                        className={`font-bold ${
                          cluster.risk_level === 'High'
                            ? 'text-rose-600'
                            : 'text-amber-600'
                        }`}
                      >
                        {cluster.risk_level} Severity
                      </span>
                    </div>
                    <div className="text-[10px] text-slate-500 font-mono mt-1">
                      Centroid: [{cluster.lat}, {cluster.lon}]
                    </div>
                  </div>
                </Popup>
              </Marker>
            );
          })}
      </MapContainer>
    </div>
  );
}

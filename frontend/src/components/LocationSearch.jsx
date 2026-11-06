import React, { useState, useEffect, useRef } from 'react';
import { MapPin, Navigation, Search, Clock, Shield, Cloud, ArrowRight, Sparkles } from 'lucide-react';
import { searchLocations } from '../services/api';

const PRESETS = [
  {
    label: 'CP → Noida Sector 18',
    origin: { name: 'Connaught Place Delhi (Verified Hub)', coords: [28.6315, 77.2167] },
    destination: { name: 'Noida Sector 18 (Verified Hub)', coords: [28.5708, 77.3271] },
    hour: 18,
    road: 'Expressway'
  },
  {
    label: 'India Gate → Cyber City Gurugram',
    origin: { name: 'India Gate Delhi (Verified Hub)', coords: [28.6129, 77.2295] },
    destination: { name: 'Cyber City Gurgaon (Verified Hub)', coords: [28.4950, 77.0895] },
    hour: 9,
    road: 'Arterial'
  },
  {
    label: 'Delhi Airport → Anand Vihar',
    origin: { name: 'Delhi Airport (Verified Hub)', coords: [28.5562, 77.1000] },
    destination: { name: 'Anand Vihar (Verified Hub)', coords: [28.6469, 77.3160] },
    hour: 22,
    road: 'Arterial'
  }
];

export default function LocationSearch({
  origin,
  setOrigin,
  destination,
  setDestination,
  departureHour,
  setDepartureHour,
  roadType,
  setRoadType,
  weatherOverride,
  setWeatherOverride,
  plannedSpeed = 60,
  setPlannedSpeed,
  vehicleType = 'Car / SUV',
  setVehicleType,
  roadCondition = 'Dry Asphalt',
  setRoadCondition,
  onAnalyze,
  loading
}) {
  // Autocomplete search states
  const [originQuery, setOriginQuery] = useState(origin?.name || 'Connaught Place, Delhi');
  const [destQuery, setDestQuery] = useState(destination?.name || 'Noida Sector 18');
  const [originSuggestions, setOriginSuggestions] = useState([]);
  const [destSuggestions, setDestSuggestions] = useState([]);
  const [showOriginDropdown, setShowOriginDropdown] = useState(false);
  const [showDestDropdown, setShowDestDropdown] = useState(false);

  const originRef = useRef(null);
  const destRef = useRef(null);

  // Debounced search for Origin
  useEffect(() => {
    if (!originQuery || originQuery.length < 2) {
      setOriginSuggestions([]);
      return;
    }
    const timer = setTimeout(async () => {
      try {
        const results = await searchLocations(originQuery);
        setOriginSuggestions(results);
      } catch (e) {
        console.error(e);
      }
    }, 280);
    return () => clearTimeout(timer);
  }, [originQuery]);

  // Debounced search for Destination
  useEffect(() => {
    if (!destQuery || destQuery.length < 2) {
      setDestSuggestions([]);
      return;
    }
    const timer = setTimeout(async () => {
      try {
        const results = await searchLocations(destQuery);
        setDestSuggestions(results);
      } catch (e) {
        console.error(e);
      }
    }, 280);
    return () => clearTimeout(timer);
  }, [destQuery]);

  // Handle outside click to close dropdowns
  useEffect(() => {
    function handleClickOutside(e) {
      if (originRef.current && !originRef.current.contains(e.target)) {
        setShowOriginDropdown(false);
      }
      if (destRef.current && !destRef.current.contains(e.target)) {
        setShowDestDropdown(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const getTimeCategory = (hour) => {
    const h = parseInt(hour, 10);
    if (h >= 6 && h < 12) return { label: 'Morning (06:00 - 12:00)', color: 'text-amber-400 bg-amber-950/40 border-amber-800/50' };
    if (h >= 12 && h < 17) return { label: 'Afternoon (12:00 - 17:00)', color: 'text-orange-400 bg-orange-950/40 border-orange-800/50' };
    if (h >= 17 && h < 22) return { label: 'Evening (17:00 - 22:00)', color: 'text-rose-400 bg-rose-950/40 border-rose-800/50' };
    return { label: 'Night (22:00 - 06:00)', color: 'text-purple-400 bg-purple-950/40 border-purple-800/50' };
  };

  const applyPreset = (preset) => {
    setOrigin(preset.origin);
    setOriginQuery(preset.origin.name);
    setDestination(preset.destination);
    setDestQuery(preset.destination.name);
    setDepartureHour(preset.hour);
    setRoadType(preset.road);
  };

  return (
    <div className="bg-slate-800/90 backdrop-blur-md rounded-2xl p-5 border border-slate-700/80 shadow-xl space-y-4">
      {/* Quick Presets */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5 text-blue-400" />
            Quick Route Presets
          </span>
          <span className="text-[11px] text-slate-500">Instant Real OSRM Driving Road</span>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
          {PRESETS.map((p, idx) => (
            <button
              key={idx}
              onClick={() => applyPreset(p)}
              className="text-left text-xs px-3 py-2 rounded-xl bg-slate-900/70 hover:bg-slate-700/80 border border-slate-700/60 hover:border-blue-500/50 transition flex items-center justify-between text-slate-300 hover:text-white group"
            >
              <span className="font-medium truncate">{p.label}</span>
              <ArrowRight className="w-3.5 h-3.5 text-slate-500 group-hover:text-blue-400 transition transform group-hover:translate-x-0.5" />
            </button>
          ))}
        </div>
      </div>

      {/* Origin & Destination Inputs */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 relative">
        {/* Origin Search */}
        <div ref={originRef} className="relative">
          <label className="block text-xs font-semibold text-slate-300 mb-1 flex items-center gap-1.5">
            <MapPin className="w-4 h-4 text-emerald-400" />
            Origin Location (Start)
          </label>
          <div className="relative">
            <input
              type="text"
              value={originQuery}
              onChange={(e) => {
                setOriginQuery(e.target.value);
                setShowOriginDropdown(true);
              }}
              onFocus={() => setShowOriginDropdown(true)}
              placeholder="Search city, area, or landmark..."
              className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3.5 py-2.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
            />
            <Search className="w-4 h-4 text-slate-400 absolute right-3 top-3 pointer-events-none" />
          </div>

          {/* Autocomplete Dropdown */}
          {showOriginDropdown && originSuggestions.length > 0 && (
            <div className="absolute left-0 right-0 top-full mt-1 bg-slate-900 border border-slate-700 rounded-xl shadow-2xl z-50 max-h-56 overflow-y-auto divide-y divide-slate-800">
              {originSuggestions.map((item, idx) => (
                <button
                  key={idx}
                  onClick={() => {
                    setOrigin({ name: item.name, coords: item.coords });
                    setOriginQuery(item.name);
                    setShowOriginDropdown(false);
                  }}
                  className="w-full text-left px-3.5 py-2.5 hover:bg-slate-800/80 transition flex items-start gap-2 text-xs"
                >
                  <MapPin className="w-3.5 h-3.5 text-emerald-400 mt-0.5 shrink-0" />
                  <div className="flex-1 truncate">
                    <div className="font-semibold text-slate-200 truncate">{item.name}</div>
                    <div className="text-[11px] text-slate-400">
                      [{item.coords[0].toFixed(4)}, {item.coords[1].toFixed(4)}] • {item.source}
                    </div>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Destination Search */}
        <div ref={destRef} className="relative">
          <label className="block text-xs font-semibold text-slate-300 mb-1 flex items-center gap-1.5">
            <Navigation className="w-4 h-4 text-rose-400" />
            Destination Location (End)
          </label>
          <div className="relative">
            <input
              type="text"
              value={destQuery}
              onChange={(e) => {
                setDestQuery(e.target.value);
                setShowDestDropdown(true);
              }}
              onFocus={() => setShowDestDropdown(true)}
              placeholder="Search destination landmark or city..."
              className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3.5 py-2.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
            />
            <Search className="w-4 h-4 text-slate-400 absolute right-3 top-3 pointer-events-none" />
          </div>

          {/* Autocomplete Dropdown */}
          {showDestDropdown && destSuggestions.length > 0 && (
            <div className="absolute left-0 right-0 top-full mt-1 bg-slate-900 border border-slate-700 rounded-xl shadow-2xl z-50 max-h-56 overflow-y-auto divide-y divide-slate-800">
              {destSuggestions.map((item, idx) => (
                <button
                  key={idx}
                  onClick={() => {
                    setDestination({ name: item.name, coords: item.coords });
                    setDestQuery(item.name);
                    setShowDestDropdown(false);
                  }}
                  className="w-full text-left px-3.5 py-2.5 hover:bg-slate-800/80 transition flex items-start gap-2 text-xs"
                >
                  <Navigation className="w-3.5 h-3.5 text-rose-400 mt-0.5 shrink-0" />
                  <div className="flex-1 truncate">
                    <div className="font-semibold text-slate-200 truncate">{item.name}</div>
                    <div className="text-[11px] text-slate-400">
                      [{item.coords[0].toFixed(4)}, {item.coords[1].toFixed(4)}] • {item.source}
                    </div>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Primary Trip Parameters: Departure Hour, Road Infrastructure, Weather */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-1">
        {/* Departure Hour */}
        <div>
          <div className="flex items-center justify-between mb-1">
            <label className="text-xs font-semibold text-slate-300 flex items-center gap-1">
              <Clock className="w-3.5 h-3.5 text-sky-400" />
              Departure Time
            </label>
            <span className="text-xs font-bold text-sky-400">
              {String(departureHour).padStart(2, '0')}:00 hrs
            </span>
          </div>
          <input
            type="range"
            min="0"
            max="23"
            value={departureHour}
            onChange={(e) => setDepartureHour(parseInt(e.target.value, 10))}
            className="w-full accent-blue-500 cursor-pointer"
          />
          <div className={`mt-1 text-[11px] px-2 py-0.5 rounded-md border font-medium inline-block ${getTimeCategory(departureHour).color}`}>
            {getTimeCategory(departureHour).label}
          </div>
        </div>

        {/* Road Type */}
        <div>
          <label className="block text-xs font-semibold text-slate-300 mb-1 flex items-center gap-1">
            <Shield className="w-3.5 h-3.5 text-indigo-400" />
            Road Infrastructure Type
          </label>
          <select
            value={roadType}
            onChange={(e) => setRoadType(e.target.value)}
            className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="Arterial">Arterial Main Road (60 km/h limit)</option>
            <option value="Expressway">Expressway / Highway (100 km/h limit)</option>
            <option value="Collector">Collector Road (45 km/h limit)</option>
            <option value="Local">Local Urban Street (30 km/h limit)</option>
          </select>
        </div>

        {/* Weather Mode */}
        <div>
          <label className="block text-xs font-semibold text-slate-300 mb-1 flex items-center gap-1">
            <Cloud className="w-3.5 h-3.5 text-teal-400" />
            Weather Condition
          </label>
          <select
            value={weatherOverride || 'Auto'}
            onChange={(e) => setWeatherOverride(e.target.value === 'Auto' ? null : e.target.value)}
            className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="Auto">Auto Live Open-Meteo API (Real-Time)</option>
            <option value="Clear">Clear Skies (Dry Friction)</option>
            <option value="Rainy">Rain / Wet Asphalt (Friction -39%)</option>
            <option value="Foggy">Dense Fog / Low Visibility (&lt;1.5km)</option>
          </select>
        </div>
      </div>

      {/* Speed & Road Condition Kinematics Section */}
      <div className="bg-slate-900/60 rounded-xl p-3.5 border border-slate-700/60 space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-xs font-bold text-slate-300 flex items-center gap-1.5">
            <span className="text-base">⚡</span>
            Speed Profile & Pavement Friction Attributes
          </span>
          <span className="text-[11px] text-sky-400 font-mono font-semibold">
            Braking & Travel Time Physics
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          {/* Planned Cruising Speed */}
          <div>
            <div className="flex items-center justify-between mb-1">
              <label className="text-[11px] font-semibold text-slate-400">
                Planned Cruising Speed
              </label>
              <span className="text-xs font-black text-emerald-400 font-mono">
                {plannedSpeed} km/h
              </span>
            </div>
            <input
              type="range"
              min="30"
              max="130"
              step="5"
              value={plannedSpeed}
              onChange={(e) => setPlannedSpeed(parseInt(e.target.value, 10))}
              className="w-full accent-emerald-500 cursor-pointer"
            />
            <div className="flex items-center justify-between text-[10px] text-slate-500 mt-1">
              <span>30 km/h</span>
              <span className="text-slate-400 font-semibold">Max 130 km/h</span>
            </div>
          </div>

          {/* Vehicle Classification */}
          <div>
            <label className="block text-[11px] font-semibold text-slate-400 mb-1">
              Vehicle Classification
            </label>
            <select
              value={vehicleType}
              onChange={(e) => setVehicleType(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 rounded-xl px-2.5 py-1.5 text-xs text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="Car / SUV">🚗 Car / SUV / Sedan</option>
              <option value="Two-Wheeler">🏍️ Two-Wheeler (Motorcycle)</option>
              <option value="Commercial Truck">🚚 Commercial Freight Truck</option>
            </select>
          </div>

          {/* Road Surface Condition */}
          <div>
            <label className="block text-[11px] font-semibold text-slate-400 mb-1">
              Road Surface Friction
            </label>
            <select
              value={roadCondition}
              onChange={(e) => setRoadCondition(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 rounded-xl px-2.5 py-1.5 text-xs text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="Dry Asphalt">Dry Asphalt (Grip: 0.85 μ)</option>
              <option value="Wet Asphalt">Wet Asphalt (Grip: 0.52 μ - Wet)</option>
              <option value="Slippery / Low Grip">Slippery / Muddy (Grip: 0.35 μ)</option>
              <option value="Under Construction">Under Construction / Potholes</option>
            </select>
          </div>
        </div>
      </div>

      {/* Submit Action */}
      <button
        onClick={onAnalyze}
        disabled={loading}
        className="w-full py-3 px-4 rounded-xl bg-gradient-to-r from-blue-600 via-indigo-600 to-sky-600 hover:from-blue-500 hover:to-sky-500 text-white font-bold text-sm shadow-lg shadow-blue-600/30 flex items-center justify-center gap-2 transition transform active:scale-[0.99] disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {loading ? (
          <>
            <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
            <span>Evaluating Road Kinematics & Collision Hazards...</span>
          </>
        ) : (
          <>
            <Navigation className="w-4 h-4" />
            <span>Analyze Real Road Driving Path & Compute Safest Departure Time</span>
          </>
        )}
      </button>
    </div>
  );
}

import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import LocationSearch from './components/LocationSearch';
import LiveWeatherBadge from './components/LiveWeatherBadge';
import HazardAlerts from './components/HazardAlerts';
import SafeTimeCard from './components/SafeTimeCard';
import RouteMap from './components/RouteMap';
import EdaGallery from './components/EdaGallery';
import ModelMetrics from './components/ModelMetrics';
import DatasetExplorer from './components/DatasetExplorer';
import CourseInfoModal from './components/CourseInfoModal';
import { analyzeRoute, fetchBlackspots } from './services/api';
import { ShieldCheck, Compass, AlertTriangle, RefreshCw } from 'lucide-react';

export default function App() {
  const [activeTab, setActiveTab] = useState('route');
  const [showCourseModal, setShowCourseModal] = useState(false);

  // Core routing state
  const [origin, setOrigin] = useState({
    name: 'Connaught Place Delhi (Verified Hub)',
    coords: [28.6315, 77.2167]
  });
  const [destination, setDestination] = useState({
    name: 'Noida Sector 18 (Verified Hub)',
    coords: [28.5708, 77.3271]
  });
  const [departureHour, setDepartureHour] = useState(18);
  const [roadType, setRoadType] = useState('Expressway');
  const [weatherOverride, setWeatherOverride] = useState(null);
  const [plannedSpeed, setPlannedSpeed] = useState(60);
  const [vehicleType, setVehicleType] = useState('Car / SUV');
  const [roadCondition, setRoadCondition] = useState('Dry Asphalt');

  // Analysis result states
  const [analysisResult, setAnalysisResult] = useState(null);
  const [blackspots, setBlackspots] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Load blackspots on startup
  useEffect(() => {
    async function loadClusters() {
      try {
        const spots = await fetchBlackspots();
        setBlackspots(spots);
      } catch (err) {
        console.error('Failed to load blackspots:', err);
      }
    }
    loadClusters();
  }, []);

  // Perform route analysis
  const handleAnalyze = async () => {
    if (!origin?.coords || !destination?.coords) {
      setError('Please select valid origin and destination locations.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const data = await analyzeRoute({
        originName: origin.name,
        destinationName: destination.name,
        originCoords: origin.coords,
        destCoords: destination.coords,
        departureHour,
        roadType,
        weatherOverride,
        plannedSpeedKmh: plannedSpeed,
        vehicleType,
        roadCondition
      });
      setAnalysisResult(data);
    } catch (err) {
      console.error('Analysis error:', err);
      setError(err.message || 'Route analysis failed. Check network or server connection.');
    } finally {
      setLoading(false);
    }
  };

  // Run initial analysis once on mount
  useEffect(() => {
    handleAnalyze();
  }, []);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col justify-between">
      <div>
        {/* Navigation Top Bar */}
        <Navbar
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          onOpenCourseInfo={() => setShowCourseModal(true)}
        />

        {/* Main Workspace Content */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          {activeTab === 'route' && (
            <div className="space-y-6">
              {/* Top Banner / Error notice */}
              {error && (
                <div className="bg-rose-950/80 border border-rose-700 rounded-2xl p-4 flex items-center gap-3 text-rose-200 text-xs">
                  <AlertTriangle className="w-5 h-5 text-rose-400 shrink-0" />
                  <div className="flex-1">{error}</div>
                  <button
                    onClick={handleAnalyze}
                    className="px-3 py-1 bg-rose-900 hover:bg-rose-800 rounded-lg text-white font-bold text-xs"
                  >
                    Retry
                  </button>
                </div>
              )}

              {/* Grid: Search Inputs on Left/Top, Map on Right */}
              <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
                {/* Left Controls Column (5 cols on lg) */}
                <div className="lg:col-span-5 space-y-5">
                  <LocationSearch
                    origin={origin}
                    setOrigin={setOrigin}
                    destination={destination}
                    setDestination={setDestination}
                    departureHour={departureHour}
                    setDepartureHour={setDepartureHour}
                    roadType={roadType}
                    setRoadType={setRoadType}
                    weatherOverride={weatherOverride}
                    setWeatherOverride={setWeatherOverride}
                    plannedSpeed={plannedSpeed}
                    setPlannedSpeed={setPlannedSpeed}
                    vehicleType={vehicleType}
                    setVehicleType={setVehicleType}
                    roadCondition={roadCondition}
                    setRoadCondition={setRoadCondition}
                    onAnalyze={handleAnalyze}
                    loading={loading}
                  />

                  {/* Real-Time Meteorological Condition Card */}
                  <LiveWeatherBadge
                    weather={analysisResult?.weather}
                    speedMetrics={analysisResult?.route?.speed_time_metrics}
                  />

                  {/* Active Road Hazards & Blackspot Advisories */}
                  <HazardAlerts alerts={analysisResult?.route?.alerts} />
                </div>

                {/* Right Interactive Map Column (7 cols on lg) */}
                <div className="lg:col-span-7 space-y-5">
                  <RouteMap
                    routeData={analysisResult?.route}
                    origin={origin}
                    destination={destination}
                    blackspots={blackspots}
                    speedMetrics={analysisResult?.route?.speed_time_metrics}
                  />

                  {/* Dynamic Machine Learning Recommended Departure Time */}
                  <SafeTimeCard
                    recommendation={analysisResult?.recommendation}
                    selectedHour={departureHour}
                    onSelectHour={(h) => {
                      setDepartureHour(h);
                      // Trigger analysis with new hour
                    }}
                  />
                </div>
              </div>
            </div>
          )}

          {activeTab === 'eda' && <EdaGallery />}
          {activeTab === 'models' && <ModelMetrics />}
          {activeTab === 'data' && <DatasetExplorer />}
        </main>
      </div>

      {/* Footer */}
      <footer className="bg-slate-900/80 border-t border-slate-800/80 py-6 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-slate-400">
          <div>
            <span className="font-bold text-slate-200">Course 213CSE2301: Predictive Analytics</span> • Faculty Guide: <span className="text-slate-200 font-semibold">Dr. N. Subbulakshmi</span>
          </div>
          <div className="flex items-center gap-3 text-[11px]">
            <span>100% Free Open-Source Architecture</span>
            <span>•</span>
            <span className="text-blue-400">OSRM Road Geometry</span>
            <span>•</span>
            <span className="text-teal-400">Open-Meteo Weather</span>
          </div>
        </div>
      </footer>

      {/* Course & Faculty Info Modal */}
      <CourseInfoModal
        isOpen={showCourseModal}
        onClose={() => setShowCourseModal(false)}
      />
    </div>
  );
}

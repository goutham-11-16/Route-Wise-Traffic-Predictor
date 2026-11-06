import React from 'react';
import { Cloud, Thermometer, Wind, Droplets, CheckCircle, Gauge, AlertOctagon, Hourglass, ShieldAlert } from 'lucide-react';

export default function LiveWeatherBadge({ weather, speedMetrics }) {
  if (!weather) return null;

  const safeLimit = speedMetrics?.weather_safe_speed_limit_kmh || 60;
  const stopLimit = speedMetrics?.blackspot_stop_speed_limit_kmh || 30;
  const stoppingDist = speedMetrics?.stopping_distance_m || 40.0;
  const estMins = speedMetrics?.estimated_minutes;
  const idealMins = speedMetrics?.ideal_minutes;
  const delayMins = speedMetrics?.delay_minutes;
  const isOverspeed = speedMetrics?.speed_hazard?.includes('OVERSPEED');

  return (
    <div className="bg-slate-800/85 backdrop-blur-md rounded-2xl p-4 border border-slate-700/80 shadow-md space-y-3.5">
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
          <Cloud className="w-3.5 h-3.5 text-sky-400" />
          Live Route Meteorology (Open-Meteo API)
        </span>
        <span className="text-[11px] font-medium text-emerald-400 flex items-center gap-1">
          <CheckCircle className="w-3 h-3" />
          Real-Time Synced
        </span>
      </div>

      {/* Grid: 4 Weather Attributes */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
        {/* Condition */}
        <div className="bg-slate-900/60 rounded-xl p-2.5 border border-slate-800 flex items-center gap-2.5">
          <span className="text-2xl">{weather.icon || '☀️'}</span>
          <div>
            <div className="text-xs font-semibold text-white truncate">{weather.condition}</div>
            <div className="text-[10px] text-slate-400 truncate">{weather.description}</div>
          </div>
        </div>

        {/* Temperature */}
        <div className="bg-slate-900/60 rounded-xl p-2.5 border border-slate-800 flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-orange-950/60 border border-orange-800/60 flex items-center justify-center text-orange-400">
            <Thermometer className="w-4 h-4" />
          </div>
          <div>
            <div className="text-sm font-bold text-white">{weather.temperature}°C</div>
            <div className="text-[10px] text-slate-400">Ambient Temp</div>
          </div>
        </div>

        {/* Wind Speed */}
        <div className="bg-slate-900/60 rounded-xl p-2.5 border border-slate-800 flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-sky-950/60 border border-sky-800/60 flex items-center justify-center text-sky-400">
            <Wind className="w-4 h-4" />
          </div>
          <div>
            <div className="text-sm font-bold text-white">{weather.windspeed} km/h</div>
            <div className="text-[10px] text-slate-400">Wind Velocity</div>
          </div>
        </div>

        {/* Friction & Traction */}
        <div className="bg-slate-900/60 rounded-xl p-2.5 border border-slate-800 flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-blue-950/60 border border-blue-800/60 flex items-center justify-center text-blue-400">
            <Droplets className="w-4 h-4" />
          </div>
          <div>
            <div className="text-xs font-bold text-white truncate">
              {speedMetrics?.road_condition_status || (weather.condition === 'Rainy' ? 'Reduced Grip (-39%)' : 'Optimal Grip')}
            </div>
            <div className="text-[10px] text-slate-400">
              μ = {speedMetrics?.friction_coefficient || (weather.condition === 'Rainy' ? '0.52' : '0.85')}
            </div>
          </div>
        </div>
      </div>

      {/* Speed Limits & Estimated Travel Time Panel */}
      {speedMetrics && (
        <div className="bg-slate-900/80 rounded-xl p-3 border border-slate-800 space-y-2.5">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-bold uppercase tracking-wider text-slate-300 flex items-center gap-1.5">
              <Gauge className="w-3.5 h-3.5 text-indigo-400" />
              Weather-Adapted Speed Limits & Stopping Dynamics
            </span>
            {isOverspeed && (
              <span className="text-[10px] font-black uppercase px-2 py-0.5 rounded-full bg-rose-950 text-rose-300 border border-rose-700 animate-pulse">
                Over-speed Warning
              </span>
            )}
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 text-xs">
            {/* Weather Safe Speed Limit */}
            <div className={`rounded-lg p-2.5 border ${
              isOverspeed ? 'bg-rose-950/40 border-rose-800/70' : 'bg-slate-800/70 border-slate-700'
            }`}>
              <div className="text-[10px] text-slate-400 font-semibold">Weather Safe Cruising Limit</div>
              <div className="flex items-baseline gap-1.5 mt-0.5">
                <span className={`text-lg font-black font-mono ${isOverspeed ? 'text-rose-400' : 'text-emerald-400'}`}>
                  {safeLimit} km/h
                </span>
                <span className="text-[10px] text-slate-400">({weather.condition} mode)</span>
              </div>
              <div className="text-[10px] text-slate-500 mt-0.5">
                Planned: <span className="text-white font-semibold">{speedMetrics.planned_speed_kmh} km/h</span>
              </div>
            </div>

            {/* Speed Limit at Stops & Blackspots */}
            <div className="bg-slate-800/70 rounded-lg p-2.5 border border-slate-700">
              <div className="text-[10px] text-slate-400 font-semibold flex items-center gap-1">
                <AlertOctagon className="w-3 h-3 text-rose-400" />
                <span>Speed Limit at Stops / Blackspots</span>
              </div>
              <div className="flex items-baseline gap-1.5 mt-0.5">
                <span className="text-lg font-black font-mono text-rose-400">
                  🛑 {stopLimit} km/h
                </span>
                <span className="text-[10px] text-slate-400">Slowdown Zone</span>
              </div>
              <div className="text-[10px] text-slate-500 mt-0.5">
                Mandatory deceleration zone
              </div>
            </div>

            {/* Stopping Distance Physics */}
            <div className="bg-slate-800/70 rounded-lg p-2.5 border border-slate-700">
              <div className="text-[10px] text-slate-400 font-semibold flex items-center gap-1">
                <Hourglass className="w-3 h-3 text-sky-400" />
                <span>Stopping Distance Buffer</span>
              </div>
              <div className="flex items-baseline gap-1.5 mt-0.5">
                <span className="text-lg font-black font-mono text-sky-300">
                  {stoppingDist} meters
                </span>
              </div>
              <div className="text-[10px] text-slate-500 mt-0.5">
                Reaction (1.2s) + Braking distance
              </div>
            </div>
          </div>

          {/* Travel Duration Estimate Breakdown */}
          {estMins && (
            <div className="flex items-center justify-between pt-1 border-t border-slate-800 text-[11px]">
              <div className="text-slate-300">
                Estimated Travel Time: <span className="text-white font-black font-mono text-xs">{estMins} mins</span>
                {delayMins > 0 && (
                  <span className="text-amber-400 font-semibold ml-1.5">
                    (+{delayMins} mins delay for weather/traffic)
                  </span>
                )}
              </div>
              <div className="text-slate-500 font-mono text-[10px]">
                Effective Speed: {speedMetrics.effective_speed_kmh} km/h
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

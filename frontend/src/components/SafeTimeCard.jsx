import React from 'react';
import { Clock, ShieldCheck, TrendingDown, Calendar, AlertCircle } from 'lucide-react';

export default function SafeTimeCard({ recommendation, selectedHour, onSelectHour }) {
  if (!recommendation) return null;

  const {
    safest_hour,
    safest_hour_label,
    safest_time_category,
    safest_risk_tier,
    safest_risk_score,
    current_hour_risk_score,
    risk_reduction_pct,
    all_time_evaluations,
    hourly_24_evaluations
  } = recommendation;

  return (
    <div className="bg-slate-800/90 backdrop-blur-md rounded-2xl p-5 border border-slate-700/80 shadow-xl space-y-5">
      {/* Hero Recommendation Header */}
      <div className="bg-gradient-to-r from-blue-900/60 via-indigo-900/50 to-emerald-950/60 border border-blue-600/40 rounded-2xl p-4.5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3.5">
          <div className="w-12 h-12 rounded-2xl bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center text-emerald-400 shrink-0 shadow-lg shadow-emerald-500/20">
            <ShieldCheck className="w-7 h-7" />
          </div>
          <div>
            <span className="text-[11px] font-bold uppercase tracking-wider text-emerald-400 flex items-center gap-1">
              <Clock className="w-3.5 h-3.5" />
              Machine Learning Recommended Travel Window
            </span>
            <h3 className="text-xl sm:text-2xl font-extrabold text-white mt-0.5">
              Depart at <span className="text-emerald-400 font-black">{safest_hour_label}</span> ({safest_time_category})
            </h3>
            <p className="text-xs text-slate-300 mt-1">
              Minimal intersection between peak rush-hour volumes, wet asphalt, and accident cluster densities.
            </p>
          </div>
        </div>

        {/* Risk Reduction Badge */}
        {risk_reduction_pct > 0 ? (
          <div className="bg-emerald-950/80 border border-emerald-700/80 rounded-xl px-4 py-3 shrink-0 text-center shadow-lg">
            <div className="flex items-center justify-center gap-1 text-emerald-400 text-xs font-bold">
              <TrendingDown className="w-4 h-4" />
              <span>Safety Gain</span>
            </div>
            <div className="text-2xl font-black text-emerald-300 mt-0.5">
              -{risk_reduction_pct}%
            </div>
            <div className="text-[10px] text-emerald-400/80">Accident Risk Drop</div>
          </div>
        ) : (
          <div className="bg-blue-950/80 border border-blue-700/80 rounded-xl px-3.5 py-2.5 shrink-0 text-center">
            <div className="text-xs font-bold text-blue-300">Selected Hour Optimal</div>
            <div className="text-[11px] text-blue-400">Lowest route collision probability</div>
          </div>
        )}
      </div>

      {/* 4 Standard Academic Windows Comparison */}
      <div>
        <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2.5 flex items-center gap-1.5">
          <Calendar className="w-3.5 h-3.5 text-blue-400" />
          Time Window Risk Comparison (Academic Syllabus Breakdown)
        </h4>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
          {all_time_evaluations?.map((win, idx) => {
            const isSafest = win.time_category === safest_time_category;
            return (
              <div
                key={idx}
                className={`rounded-xl p-3 border transition ${
                  isSafest
                    ? 'bg-emerald-950/40 border-emerald-600/70 shadow-md shadow-emerald-600/10'
                    : 'bg-slate-900/60 border-slate-800'
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs font-bold text-white">{win.time_category}</span>
                  <span className="text-sm">{win.weather_icon || '☀️'}</span>
                </div>
                <div className="flex items-center justify-between text-xs mt-1.5">
                  <span
                    className="font-bold text-[10px] uppercase px-2 py-0.5 rounded-full"
                    style={{
                      color: win.risk_color,
                      backgroundColor: `${win.risk_color}18`,
                      border: `1px solid ${win.risk_color}40`
                    }}
                  >
                    {win.journey_risk_tier}
                  </span>
                  <span className="font-mono text-slate-400 text-[11px]">
                    {(win.mean_risk_score * 100).toFixed(1)}%
                  </span>
                </div>
                {isSafest && (
                  <div className="mt-2 pt-1.5 border-t border-emerald-800/40 text-[10px] font-bold text-emerald-400 text-center">
                    ★ Safest Window
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* 24-Hour Interactive Hourly Risk Trajectory Curve */}
      {hourly_24_evaluations && hourly_24_evaluations.length === 24 && (
        <div>
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">
              24-Hour Continuous Collision Risk Curve
            </span>
            <span className="text-[11px] text-slate-500">Click any hour to test route at that time</span>
          </div>

          <div className="bg-slate-900/80 rounded-xl p-3 border border-slate-800">
            <div className="grid grid-cols-12 sm:grid-cols-24 gap-1 items-end h-28 pt-4">
              {hourly_24_evaluations.map((hItem) => {
                const isCurrent = hItem.hour === selectedHour;
                const isSafest = hItem.hour === safest_hour;
                // Height scaled between 15% and 100%
                const heightPct = Math.max(15, Math.min(100, Math.round(hItem.mean_risk_score * 150)));

                return (
                  <button
                    key={hItem.hour}
                    onClick={() => onSelectHour && onSelectHour(hItem.hour)}
                    title={`Hour ${hItem.hour_label}: Risk Score ${(hItem.mean_risk_score * 100).toFixed(1)}% (${hItem.journey_risk_tier}) - Weather: ${hItem.weather}`}
                    className="group relative flex flex-col items-center h-full justify-end focus:outline-none"
                  >
                    {/* Pillar Bar */}
                    <div
                      style={{
                        height: `${heightPct}%`,
                        backgroundColor: hItem.risk_color
                      }}
                      className={`w-full rounded-t-sm transition-all duration-300 ${
                        isCurrent
                          ? 'ring-2 ring-white shadow-lg opacity-100'
                          : isSafest
                          ? 'ring-2 ring-emerald-400 opacity-95'
                          : 'opacity-70 group-hover:opacity-100'
                      }`}
                    ></div>

                    {/* Hour Number */}
                    <span className={`text-[9px] mt-1 font-mono ${
                      isCurrent
                        ? 'text-white font-black underline'
                        : isSafest
                        ? 'text-emerald-400 font-bold'
                        : 'text-slate-500'
                    }`}>
                      {hItem.hour}
                    </span>

                    {/* Tooltip on hover */}
                    <div className="absolute bottom-full mb-1 hidden group-hover:flex flex-col items-center z-30 pointer-events-none">
                      <div className="bg-slate-950 text-white text-[10px] rounded px-1.5 py-0.5 shadow-lg whitespace-nowrap border border-slate-700">
                        {hItem.hour_label} • {(hItem.mean_risk_score * 100).toFixed(0)}% • {hItem.weather}
                      </div>
                    </div>
                  </button>
                );
              })}
            </div>

            {/* Legend */}
            <div className="flex items-center justify-center gap-4 mt-3 pt-2 border-t border-slate-800/80 text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span>
                <span className="text-slate-400">Low Risk (&lt;35%)</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-amber-500"></span>
                <span className="text-slate-400">Moderate Risk (35-58%)</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-rose-500"></span>
                <span className="text-slate-400">High Risk (&gt;58%)</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

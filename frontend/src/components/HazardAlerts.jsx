import React from 'react';
import { AlertTriangle, ShieldAlert, CloudRain, Clock, AlertOctagon } from 'lucide-react';

export default function HazardAlerts({ alerts }) {
  if (!alerts || alerts.length === 0) {
    return (
      <div className="bg-emerald-950/40 border border-emerald-800/60 rounded-2xl p-4 flex items-center gap-3">
        <div className="w-8 h-8 rounded-full bg-emerald-900/80 border border-emerald-700 text-emerald-300 flex items-center justify-center shrink-0">
          ✓
        </div>
        <div>
          <h4 className="text-xs font-bold text-emerald-300">No Critical Road Hazard Alerts Detected</h4>
          <p className="text-[11px] text-emerald-400/80">
            Route clear of nearby high-risk blackspots (radius &gt; 1.2km) and normal weather conditions.
          </p>
        </div>
      </div>
    );
  }

  const getAlertStyles = (severity) => {
    switch (severity) {
      case 'CRITICAL':
        return {
          bg: 'bg-rose-950/60 border-rose-800/80',
          title: 'text-rose-300',
          badge: 'bg-rose-900 text-rose-200 border-rose-700',
          iconColor: 'text-rose-400'
        };
      case 'HIGH':
        return {
          bg: 'bg-amber-950/60 border-amber-800/80',
          title: 'text-amber-300',
          badge: 'bg-amber-900 text-amber-200 border-amber-700',
          iconColor: 'text-amber-400'
        };
      default:
        return {
          bg: 'bg-sky-950/60 border-sky-800/80',
          title: 'text-sky-300',
          badge: 'bg-sky-900 text-sky-200 border-sky-700',
          iconColor: 'text-sky-400'
        };
    }
  };

  return (
    <div className="space-y-2.5">
      <div className="flex items-center justify-between">
        <span className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
          <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
          Active Road Safety Advisories ({alerts.length})
        </span>
        <span className="text-[11px] text-slate-400">Rule-Based & Spatial Inference</span>
      </div>

      <div className="grid grid-cols-1 gap-2.5">
        {alerts.map((alert, idx) => {
          const style = getAlertStyles(alert.severity);
          return (
            <div
              key={idx}
              className={`${style.bg} border rounded-xl p-3.5 shadow-md flex items-start gap-3 transition hover:border-slate-600`}
            >
              <div className="text-2xl shrink-0 mt-0.5">{alert.icon || '⚠️'}</div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between gap-2 mb-1">
                  <h5 className={`text-xs font-bold ${style.title} truncate`}>{alert.title}</h5>
                  <span className={`text-[10px] font-extrabold uppercase px-2 py-0.5 rounded-full border ${style.badge}`}>
                    {alert.severity}
                  </span>
                </div>
                <p className="text-xs text-slate-300 leading-relaxed">{alert.message}</p>
                {alert.speed_limit_at_stops && (
                  <div className="mt-2 flex items-center gap-2">
                    <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-rose-900/80 border border-rose-600 text-rose-200 text-[11px] font-black font-mono shadow-sm">
                      <span>🛑 Hazard Stop Zone Speed Limit:</span>
                      <span className="text-white text-xs">{alert.speed_limit_at_stops} km/h</span>
                    </span>
                    <span className="text-[10px] text-slate-400">Strictly enforced slowdown zone</span>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

import React from 'react';
import { X, GraduationCap, Award, CheckCircle2, Shield, Heart } from 'lucide-react';

export default function CourseInfoModal({ isOpen, onClose }) {
  if (!isOpen) return null;

  return (
    <div
      onClick={onClose}
      className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 animate-in fade-in duration-200"
    >
      <div
        onClick={(e) => e.stopPropagation()}
        className="bg-slate-900 border border-slate-700 rounded-3xl max-w-2xl w-full p-6 shadow-2xl space-y-5"
      >
        {/* Header */}
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <div className="flex items-center gap-2.5">
            <div className="w-10 h-10 rounded-xl bg-blue-600/20 border border-blue-500/40 flex items-center justify-center text-blue-400">
              <GraduationCap className="w-6 h-6" />
            </div>
            <div>
              <div className="text-xs font-bold uppercase tracking-wider text-blue-400">
                Course: 213CSE2301 - Predictive Analytics
              </div>
              <h3 className="text-lg font-black text-white">Project Information & Architecture</h3>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Project Details */}
        <div className="space-y-4 text-xs text-slate-300">
          <div className="bg-slate-800/80 rounded-2xl p-4 border border-slate-700 space-y-2">
            <div className="flex items-center justify-between">
              <span className="font-bold text-slate-200 uppercase text-[10px] tracking-wider">
                Course Coordinator & Guide
              </span>
              <span className="px-2 py-0.5 rounded-full bg-blue-950 text-blue-300 border border-blue-700 font-semibold text-[11px]">
                Faculty Supervisor
              </span>
            </div>
            <div className="text-base font-extrabold text-white flex items-center gap-2">
              <Award className="w-5 h-5 text-amber-400" />
              <span>Dr. N. Subbulakshmi</span>
            </div>
            <p className="text-slate-400 text-[11px]">
              Associate Professor / Senior Faculty, Department of Computer Science and Engineering
            </p>
          </div>

          {/* Project Title & Abstract */}
          <div className="bg-slate-800/80 rounded-2xl p-4 border border-slate-700 space-y-2">
            <div className="font-bold text-white text-sm">
              Route - Wise AI: Traffic Accident Risk Prediction and Safer Travel Time Recommendation System
            </div>
            <p className="text-slate-300 leading-relaxed text-[11px]">
              This project integrates spatial road geometry routing with machine learning collision models and live meteorological data. Rather than predicting accidents as static points, it segments entire travel corridors, identifies nearby high-fatality blackspots, and recommends optimal departure times to maximize driver safety.
            </p>
          </div>

          {/* 100% Free Architecture Guarantee */}
          <div className="bg-emerald-950/40 rounded-2xl p-4 border border-emerald-800/60 space-y-2">
            <div className="font-bold text-emerald-300 flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>100% Free & Open-Source Stack (Zero API Costs)</span>
            </div>
            <ul className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-[11px] text-emerald-400/90 pt-1">
              <li>• Routing: OSRM (Open Source Routing Machine)</li>
              <li>• Weather: Open-Meteo 24h Hourly Forecast</li>
              <li>• Map Tiles: OpenStreetMap Foundation</li>
              <li>• ML Engine: Scikit-Learn (Random Forest & K-Means)</li>
            </ul>
          </div>
        </div>

        {/* Footer Close */}
        <div className="pt-2 flex justify-end">
          <button
            onClick={onClose}
            className="px-5 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs shadow-md transition"
          >
            Got it, Close
          </button>
        </div>
      </div>
    </div>
  );
}

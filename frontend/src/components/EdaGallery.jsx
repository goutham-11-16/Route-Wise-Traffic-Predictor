import React, { useState, useEffect } from 'react';
import { fetchEdaCharts } from '../services/api';
import { BarChart3, Maximize2, X, Sparkles, ExternalLink } from 'lucide-react';

export default function EdaGallery() {
  const [charts, setCharts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedChart, setSelectedChart] = useState(null);

  useEffect(() => {
    async function load() {
      try {
        const data = await fetchEdaCharts();
        setCharts(data);
      } catch (err) {
        console.error('Failed to load charts:', err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center p-16">
        <div className="w-8 h-8 border-3 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-slate-800/80 backdrop-blur-md rounded-2xl p-6 border border-slate-700/80">
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-2">
              <span className="px-2.5 py-1 rounded-md bg-blue-900/60 border border-blue-700 text-blue-300 text-xs font-bold uppercase">
                Final PA Presentation Artifacts
              </span>
              <span className="text-xs text-slate-400">Exact match with slide decks 5, 6, 8, 9</span>
            </div>
            <h2 className="text-xl sm:text-2xl font-black text-white mt-1.5">
              Exploratory Data Analysis & Empirical Slide Figures
            </h2>
            <p className="text-xs text-slate-300 mt-1">
              Generated from the verified 6,469 cleaned collision records across Morning, Afternoon, Evening, and Night intervals.
            </p>
          </div>
        </div>
      </div>

      {/* Grid of Slide Charts */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {charts.map((chart) => (
          <div
            key={chart.id}
            className="bg-slate-800/90 rounded-2xl border border-slate-700/80 overflow-hidden shadow-xl hover:border-blue-500/50 transition group flex flex-col justify-between"
          >
            <div>
              {/* Image Container */}
              <div
                onClick={() => setSelectedChart(chart)}
                className="relative h-56 bg-slate-950 overflow-hidden cursor-pointer flex items-center justify-center p-2"
              >
                <img
                  src={chart.url}
                  alt={chart.title}
                  className="max-h-full max-w-full object-contain group-hover:scale-105 transition duration-300"
                />
                <div className="absolute inset-0 bg-slate-900/40 opacity-0 group-hover:opacity-100 transition flex items-center justify-center gap-2 text-white text-xs font-bold">
                  <Maximize2 className="w-4 h-4" />
                  <span>Click to Expand</span>
                </div>
              </div>

              {/* Meta info */}
              <div className="p-4 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="px-2 py-0.5 rounded text-[10px] font-extrabold uppercase bg-slate-700 text-sky-300 border border-slate-600">
                    {chart.slide}
                  </span>
                </div>
                <h3 className="font-bold text-sm text-white group-hover:text-blue-400 transition">
                  {chart.title}
                </h3>
                <p className="text-xs text-slate-300 leading-relaxed">
                  {chart.description}
                </p>
              </div>
            </div>

            <div className="px-4 pb-4 pt-1 border-t border-slate-700/50">
              <button
                onClick={() => setSelectedChart(chart)}
                className="w-full py-2 rounded-xl bg-slate-900/80 hover:bg-blue-600 hover:text-white text-xs font-semibold text-slate-300 transition flex items-center justify-center gap-1.5"
              >
                <Maximize2 className="w-3.5 h-3.5" />
                <span>Enlarge Figure</span>
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Fullscreen Image Modal */}
      {selectedChart && (
        <div
          onClick={() => setSelectedChart(null)}
          className="fixed inset-0 z-50 bg-black/85 backdrop-blur-sm flex items-center justify-center p-4"
        >
          <div
            onClick={(e) => e.stopPropagation()}
            className="bg-slate-900 border border-slate-700 rounded-2xl max-w-4xl w-full overflow-hidden shadow-2xl space-y-4 p-5 animate-in fade-in zoom-in-95 duration-200"
          >
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div>
                <span className="text-[11px] font-bold uppercase text-blue-400">
                  {selectedChart.slide} Reference
                </span>
                <h3 className="text-base font-bold text-white mt-0.5">{selectedChart.title}</h3>
              </div>
              <button
                onClick={() => setSelectedChart(null)}
                className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white transition"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="bg-slate-950 rounded-xl p-3 flex items-center justify-center max-h-[70vh]">
              <img
                src={selectedChart.url}
                alt={selectedChart.title}
                className="max-h-[65vh] object-contain rounded-lg"
              />
            </div>

            <p className="text-xs text-slate-300 leading-relaxed">
              {selectedChart.description}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

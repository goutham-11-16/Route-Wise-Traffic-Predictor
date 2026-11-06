import React, { useState, useEffect } from 'react';
import { fetchAccidentsSample } from '../services/api';
import { Database, Filter, Search, CheckCircle } from 'lucide-react';

export default function DatasetExplorer() {
  const [data, setData] = useState({ records: [], total_in_dataset: 6469 });
  const [loading, setLoading] = useState(true);
  const [severityFilter, setSeverityFilter] = useState('ALL');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    async function load() {
      try {
        const res = await fetchAccidentsSample(100);
        setData(res);
      } catch (err) {
        console.error('Failed to load dataset:', err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const filteredRecords = data.records.filter((rec) => {
    const matchesSev = severityFilter === 'ALL' || rec.Severity === severityFilter;
    const matchesSearch =
      searchTerm === '' ||
      rec.Weather?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      rec.Road_Type?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      rec.Time_Category?.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesSev && matchesSearch;
  });

  return (
    <div className="space-y-6">
      {/* Header & Dataset Metrics */}
      <div className="bg-slate-800/80 backdrop-blur-md rounded-2xl p-6 border border-slate-700/80 shadow-xl space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <div className="flex items-center gap-2">
              <span className="px-2.5 py-1 rounded-md bg-emerald-950/80 border border-emerald-700 text-emerald-300 text-xs font-bold uppercase flex items-center gap-1.5">
                <CheckCircle className="w-3.5 h-3.5" />
                Verified Cleaned Dataset
              </span>
              <span className="text-xs text-slate-400">Total Observations: 6,469</span>
            </div>
            <h2 className="text-xl sm:text-2xl font-black text-white mt-1.5">
              Accident Records & Empirical Training Data
            </h2>
          </div>
        </div>

        {/* Academic Syllabus Distribution Metrics */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-2">
          <div className="bg-slate-900/80 rounded-xl p-3 border border-slate-800">
            <div className="text-[11px] text-slate-400">Morning (Slide 5)</div>
            <div className="text-lg font-bold text-white mt-0.5">1,910</div>
            <div className="text-[10px] text-slate-500">29.5% of records</div>
          </div>
          <div className="bg-slate-900/80 rounded-xl p-3 border border-slate-800">
            <div className="text-[11px] text-slate-400">Afternoon (Slide 5)</div>
            <div className="text-lg font-bold text-white mt-0.5">2,230</div>
            <div className="text-[10px] text-slate-500">34.5% of records</div>
          </div>
          <div className="bg-slate-900/80 rounded-xl p-3 border border-slate-800">
            <div className="text-[11px] text-slate-400">Evening (Slide 5)</div>
            <div className="text-lg font-bold text-white mt-0.5">1,090</div>
            <div className="text-[10px] text-slate-500">16.8% of records</div>
          </div>
          <div className="bg-slate-900/80 rounded-xl p-3 border border-slate-800">
            <div className="text-[11px] text-slate-400">Night (Slide 5)</div>
            <div className="text-lg font-bold text-white mt-0.5">1,239</div>
            <div className="text-[10px] text-slate-500">19.2% of records</div>
          </div>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-slate-800/90 rounded-2xl p-4 border border-slate-700/80 flex flex-col sm:flex-row items-center justify-between gap-3">
        <div className="flex items-center gap-2 w-full sm:w-auto">
          <Filter className="w-4 h-4 text-slate-400" />
          <span className="text-xs font-bold text-slate-300">Severity:</span>
          {['ALL', 'High', 'Medium', 'Low'].map((s) => (
            <button
              key={s}
              onClick={() => setSeverityFilter(s)}
              className={`px-3 py-1 rounded-lg text-xs font-semibold transition ${
                severityFilter === s
                  ? 'bg-blue-600 text-white shadow-md'
                  : 'bg-slate-900 text-slate-400 hover:text-white'
              }`}
            >
              {s}
            </button>
          ))}
        </div>

        <div className="relative w-full sm:w-64">
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search weather, road..."
            className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <Search className="w-3.5 h-3.5 text-slate-400 absolute right-3 top-2.5" />
        </div>
      </div>

      {/* Records Table */}
      <div className="bg-slate-800/90 rounded-2xl border border-slate-700/80 shadow-xl overflow-hidden">
        {loading ? (
          <div className="flex items-center justify-center p-12">
            <div className="w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-slate-900/80 border-b border-slate-700 text-[11px] font-extrabold uppercase text-slate-400">
                  <th className="py-3 px-3">Hour</th>
                  <th className="py-3 px-3">Time Window</th>
                  <th className="py-3 px-3">Weather</th>
                  <th className="py-3 px-3">Road Type</th>
                  <th className="py-3 px-3">Latitude</th>
                  <th className="py-3 px-3">Longitude</th>
                  <th className="py-3 px-3">Accident Severity</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800 text-xs">
                {filteredRecords.map((r, idx) => (
                  <tr key={idx} className="hover:bg-slate-750 transition">
                    <td className="py-2.5 px-3 font-mono font-bold text-sky-300">
                      {String(r.Hour).padStart(2, '0')}:00
                    </td>
                    <td className="py-2.5 px-3">{r.Time_Category}</td>
                    <td className="py-2.5 px-3">{r.Weather}</td>
                    <td className="py-2.5 px-3">{r.Road_Type}</td>
                    <td className="py-2.5 px-3 font-mono text-slate-400">{r.Latitude}</td>
                    <td className="py-2.5 px-3 font-mono text-slate-400">{r.Longitude}</td>
                    <td className="py-2.5 px-3">
                      <span
                        className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase border ${
                          r.Severity === 'High'
                            ? 'bg-rose-950/80 text-rose-300 border-rose-700'
                            : r.Severity === 'Medium'
                            ? 'bg-amber-950/80 text-amber-300 border-amber-700'
                            : 'bg-emerald-950/80 text-emerald-300 border-emerald-700'
                        }`}
                      >
                        {r.Severity}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

"use client";
import { useState, useEffect } from "react";
import { scoutAnomaly, getClusters } from "@/lib/api";

const ANOMALY_DEFAULTS = {
  goals: 14, assists: 8, minutes_played: 2400,
  pass_accuracy: 0.82, cards: 3, xg: 12.5, performance_trend: 0.8,
};

export default function ScoutPage() {
  const [input, setInput] = useState(ANOMALY_DEFAULTS);
  const [result, setResult] = useState<any>(null);
  const [clusters, setClusters] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    getClusters().then(setClusters).catch(() => {});
  }, []);

  const handleAnomaly = async () => {
    setLoading(true);
    try { setResult(await scoutAnomaly(input)); } catch { setResult({ error: "Failed" }); }
    setLoading(false);
  };

  const Num = ({ label, value, onChange, step = 1 }: { label: string; value: number; onChange: (v: number) => void; step?: number }) => (
    <label className="flex flex-col gap-1">
      <span className="text-xs text-zinc-500 uppercase">{label}</span>
      <input type="number" step={step} value={value} onChange={e => onChange(parseFloat(e.target.value) || 0)}
        className="bg-zinc-800 rounded px-3 py-2 text-sm border border-zinc-700 focus:border-emerald-500 outline-none" />
    </label>
  );

  return (
    <div className="space-y-10">
      <h1 className="text-3xl font-bold">Scouting</h1>

      {/* Anomaly Detection */}
      <section className="bg-zinc-900 rounded-lg p-6 border border-zinc-800">
        <h2 className="text-xl font-semibold mb-4">🔍 Anomaly Detector</h2>
        <p className="text-zinc-400 text-sm mb-4">Detect statistically unusual player performances</p>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
          <Num label="Goals" value={input.goals} onChange={v => setInput({...input, goals: v})} />
          <Num label="Assists" value={input.assists} onChange={v => setInput({...input, assists: v})} />
          <Num label="Minutes" value={input.minutes_played} onChange={v => setInput({...input, minutes_played: v})} step={100} />
          <Num label="Pass Acc" value={input.pass_accuracy} onChange={v => setInput({...input, pass_accuracy: v})} step={0.01} />
          <Num label="Cards" value={input.cards} onChange={v => setInput({...input, cards: v})} />
          <Num label="xG" value={input.xg} onChange={v => setInput({...input, xg: v})} step={0.1} />
          <Num label="Trend" value={input.performance_trend} onChange={v => setInput({...input, performance_trend: v})} step={0.1} />
        </div>
        <button onClick={handleAnomaly} disabled={loading}
          className="bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 px-6 py-2 rounded font-medium transition">
          {loading ? "Detecting..." : "Detect Anomaly"}
        </button>
        {result && !result.error && (
          <div className="mt-6 flex gap-8">
            <div className={`text-center px-8 py-4 rounded-lg ${result.is_anomaly ? "bg-red-500/20 border border-red-500/30" : "bg-emerald-500/20 border border-emerald-500/30"}`}>
              <p className={`text-2xl font-bold ${result.is_anomaly ? "text-red-400" : "text-emerald-400"}`}>
                {result.is_anomaly ? "ANOMALY" : "NORMAL"}
              </p>
              <p className="text-xs text-zinc-500 mt-1">Score: {result.anomaly_score.toFixed(3)}</p>
            </div>
          </div>
        )}
      </section>

      {/* Clusters */}
      <section className="bg-zinc-900 rounded-lg p-6 border border-zinc-800">
        <h2 className="text-xl font-semibold mb-4">👥 Player Clusters</h2>
        {clusters?.clusters ? (
          <div className="grid gap-4 md:grid-cols-2">
            {clusters.clusters.map((c: any, i: number) => (
              <div key={i} className="bg-zinc-800 rounded-lg p-4 border border-zinc-700">
                <p className="font-semibold text-emerald-400">{c.cluster_name || `Cluster ${c.cluster_id}`}</p>
                <p className="text-xs text-zinc-500 mt-1">ID: {c.cluster_id}</p>
                {c.centroid_values && (
                  <div className="mt-2 grid grid-cols-3 gap-2 text-xs">
                    {Object.entries(c.centroid_values).slice(0, 6).map(([k, v]: any) => (
                      <span key={k}><span className="text-zinc-500">{k}:</span> {typeof v === "number" ? v.toFixed(2) : v}</span>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <p className="text-zinc-500">Loading clusters...</p>
        )}
      </section>
    </div>
  );
}
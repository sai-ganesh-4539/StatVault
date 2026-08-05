"use client";
import { useEffect, useState } from "react";
import { getHealth, getLiveScores, getStandings } from "@/lib/api";

export default function Dashboard() {
  const [health, setHealth] = useState<any>(null);
  const [live, setLive] = useState<any>(null);
  const [standings, setStandings] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const [h, l, s] = await Promise.allSettled([
          getHealth(),
          getLiveScores(),
          getStandings("PL"),
        ]);
        if (h.status === "fulfilled") setHealth(h.value);
        if (l.status === "fulfilled") setLive(l.value);
        if (s.status === "fulfilled") setStandings(s.value);
      } catch {}
      setLoading(false);
    }
    load();
  }, []);

  if (loading) return <p className="text-zinc-500 animate-pulse">Loading...</p>;

  const matches = live?.matches || [];
  const table = standings?.standings?.[0]?.table || [];

  return (
    <div className="space-y-8">
      {/* Hero */}
      <div className="flex items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold">Football Intelligence</h1>
          <p className="text-zinc-400 mt-1">
            AI predictions · Anomaly scouting · Live data
          </p>
        </div>
        {health && (
          <span className={`ml-auto px-3 py-1 rounded-full text-xs font-medium ${
            health.status === "ok" ? "bg-emerald-500/20 text-emerald-400" : "bg-amber-500/20 text-amber-400"
          }`}>
            {health.status === "ok" ? "All Systems Go" : "Degraded"}
          </span>
        )}
      </div>

      {/* Model Status */}
      {health?.models_loaded && (
        <div className="grid grid-cols-3 gap-4">
          {Object.entries(health.models_loaded).map(([name, ok]: any) => (
            <div key={name} className="bg-zinc-900 rounded-lg p-4 border border-zinc-800">
              <p className="text-xs text-zinc-500 uppercase tracking-wider">{name.replace(/_/g, " ")}</p>
              <p className={`text-lg font-semibold mt-1 ${ok ? "text-emerald-400" : "text-red-400"}`}>
                {ok ? "Loaded" : "Missing"}
              </p>
            </div>
          ))}
        </div>
      )}

      {/* Live Scores */}
      <section>
        <h2 className="text-xl font-semibold mb-4">🔴 Live Scores</h2>
        {matches.length === 0 ? (
          <p className="text-zinc-500">No live matches right now</p>
        ) : (
          <div className="grid gap-3">
            {matches.slice(0, 6).map((m: any) => (
              <div key={m.id} className="bg-zinc-900 rounded-lg p-4 border border-zinc-800 flex items-center justify-between">
                <div className="flex-1">
                  <p className="font-medium">{m.homeTeam?.shortName || m.homeTeam?.name}</p>
                  <p className="text-zinc-500 text-sm">{m.awayTeam?.shortName || m.awayTeam?.name}</p>
                </div>
                <div className="text-center px-4">
                  <p className="text-xl font-bold">
                    {m.score?.fullTime?.home ?? "-"} - {m.score?.fullTime?.away ?? "-"}
                  </p>
                  <p className="text-xs text-emerald-400">{m.status || "LIVE"}</p>
                </div>
                <div className="flex-1 text-right">
                  <p className="text-xs text-zinc-500">{m.competition?.name || ""}</p>
                  <p className="text-xs text-zinc-600">{m.minute ? `${m.minute}'` : ""}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Standings */}
      {table.length > 0 && (
        <section>
          <h2 className="text-xl font-semibold mb-4">🏆 Premier League</h2>
          <div className="bg-zinc-900 rounded-lg border border-zinc-800 overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-zinc-800/50">
                <tr>
                  <th className="text-left p-3">#</th>
                  <th className="text-left p-3">Team</th>
                  <th className="text-center p-3">P</th>
                  <th className="text-center p-3">W</th>
                  <th className="text-center p-3">D</th>
                  <th className="text-center p-3">L</th>
                  <th className="text-center p-3">Pts</th>
                </tr>
              </thead>
              <tbody>
                {table.slice(0, 10).map((t: any) => (
                  <tr key={t.position} className="border-t border-zinc-800">
                    <td className="p-3 text-zinc-500">{t.position}</td>
                    <td className="p-3 font-medium">{t.team?.shortName || t.team?.name}</td>
                    <td className="p-3 text-center">{t.playedGames}</td>
                    <td className="p-3 text-center">{t.won}</td>
                    <td className="p-3 text-center">{t.draw}</td>
                    <td className="p-3 text-center">{t.lost}</td>
                    <td className="p-3 text-center font-bold text-emerald-400">{t.points}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}
    </div>
  );
}
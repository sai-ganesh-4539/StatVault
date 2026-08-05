"use client";
import { useEffect, useState } from "react";
import { getStandings, getScorers } from "@/lib/api";

const COMPS = [
  { code: "PL", name: "Premier League" },
  { code: "BL1", name: "Bundesliga" },
  { code: "SA", name: "Serie A" },
  { code: "PD", name: "La Liga" },
  { code: "FL1", name: "Ligue 1" },
];

export default function StandingsPage() {
  const [comp, setComp] = useState("PL");
  const [standings, setStandings] = useState<any>(null);
  const [scorers, setScorers] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    Promise.allSettled([getStandings(comp), getScorers(comp)]).then(([s, sc]) => {
      if (s.status === "fulfilled") setStandings(s.value);
      if (sc.status === "fulfilled") setScorers(sc.value);
      setLoading(false);
    });
  }, [comp]);

  const table = standings?.standings?.[0]?.table || [];
  const scorerList = scorers?.scorers || [];

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Standings</h1>
        <select value={comp} onChange={e => setComp(e.target.value)}
          className="bg-zinc-800 rounded px-4 py-2 border border-zinc-700 text-sm">
          {COMPS.map(c => <option key={c.code} value={c.code}>{c.name}</option>)}
        </select>
      </div>

      {loading ? <p className="text-zinc-500 animate-pulse">Loading...</p> : (
        <>
          {/* Table */}
          {table.length > 0 && (
            <div className="bg-zinc-900 rounded-lg border border-zinc-800 overflow-hidden">
              <table className="w-full text-sm">
                <thead className="bg-zinc-800/50">
                  <tr>
                    <th className="p-3 text-left">#</th>
                    <th className="p-3 text-left">Team</th>
                    <th className="p-3 text-center">P</th>
                    <th className="p-3 text-center">W</th>
                    <th className="p-3 text-center">D</th>
                    <th className="p-3 text-center">L</th>
                    <th className="p-3 text-center">GD</th>
                    <th className="p-3 text-center">Pts</th>
                  </tr>
                </thead>
                <tbody>
                  {table.map((t: any) => (
                    <tr key={t.position} className="border-t border-zinc-800">
                      <td className="p-3 text-zinc-500">{t.position}</td>
                      <td className="p-3 font-medium">{t.team?.shortName || t.team?.name}</td>
                      <td className="p-3 text-center">{t.playedGames}</td>
                      <td className="p-3 text-center">{t.won}</td>
                      <td className="p-3 text-center">{t.draw}</td>
                      <td className="p-3 text-center">{t.lost}</td>
                      <td className="p-3 text-center">{t.goalDifference > 0 ? `+${t.goalDifference}` : t.goalDifference}</td>
                      <td className="p-3 text-center font-bold text-emerald-400">{t.points}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Top Scorers */}
          {scorerList.length > 0 && (
            <section>
              <h2 className="text-xl font-semibold mb-4">⚽ Top Scorers</h2>
              <div className="bg-zinc-900 rounded-lg border border-zinc-800 overflow-hidden">
                <table className="w-full text-sm">
                  <thead className="bg-zinc-800/50">
                    <tr>
                      <th className="p-3 text-left">#</th>
                      <th className="p-3 text-left">Player</th>
                      <th className="p-3 text-left">Team</th>
                      <th className="p-3 text-center">Goals</th>
                      <th className="p-3 text-center">Assists</th>
                    </tr>
                  </thead>
                  <tbody>
                    {scorerList.slice(0, 10).map((s: any, i: number) => (
                      <tr key={i} className="border-t border-zinc-800">
                        <td className="p-3 text-zinc-500">{i + 1}</td>
                        <td className="p-3 font-medium">{s.player?.name}</td>
                        <td className="p-3 text-zinc-400">{s.team?.shortName || s.team?.name}</td>
                        <td className="p-3 text-center font-bold text-emerald-400">{s.goals || s.goalsScored}</td>
                        <td className="p-3 text-center">{s.assists ?? "-"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
          )}
        </>
      )}
    </div>
  );
}
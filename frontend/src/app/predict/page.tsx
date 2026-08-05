"use client";
import { useState } from "react";
import { predictMatch, predictMarketValue } from "@/lib/api";

const MATCH_DEFAULTS = {
  home_team: "Arsenal", away_team: "Chelsea",
  home_form_wins: 3, home_form_draws: 1, home_form_losses: 1,
  away_form_wins: 2, away_form_draws: 1, away_form_losses: 2,
  home_goals_avg: 1.8, away_goals_avg: 1.2,
  home_xg_avg: 1.6, away_xg_avg: 1.1,
  home_win_rate: 0.6, away_win_rate: 0.4,
  home_odds: 2.0, draw_odds: 3.3, away_odds: 2.5,
  h2h_home_wins: 3, h2h_away_wins: 2,
};

const MV_DEFAULTS = {
  age: 23, overall_rating: 85, potential: 90,
  pace: 88, shooting: 80, passing: 82,
  dribbling: 86, defending: 40, physical: 75,
  height_cm: 178, weight_kg: 70,
  preferred_foot: "Right", position: "RW,CAM",
};

interface NumInputProps {
  label: string;
  value: number;
  onChange: (v: number) => void;
  step?: number;
}

function NumInput({ label, value, onChange, step = 1 }: NumInputProps) {
  return (
    <label className="flex flex-col gap-1">
      <span className="text-xs text-zinc-500 uppercase">{label}</span>
      <input
        type="number"
        step={step}
        value={value}
        onChange={(e) => onChange(parseFloat(e.target.value) || 0)}
        className="bg-zinc-800 rounded px-3 py-2 text-sm border border-zinc-700 focus:border-emerald-500 outline-none"
      />
    </label>
  );
}

export default function PredictPage() {
  const [matchInput, setMatchInput] = useState(MATCH_DEFAULTS);
  const [mvInput, setMvInput] = useState(MV_DEFAULTS);
  const [matchResult, setMatchResult] = useState<any>(null);
  const [mvResult, setMvResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleMatch = async () => {
    setLoading(true);
    try {
      setMatchResult(await predictMatch(matchInput));
    } catch {
      setMatchResult({ error: "Prediction failed" });
    }
    setLoading(false);
  };

  const handleMV = async () => {
    setLoading(true);
    try {
      setMvResult(await predictMarketValue(mvInput));
    } catch {
      setMvResult({ error: "Prediction failed" });
    }
    setLoading(false);
  };

  return (
    <div className="space-y-10">
      <h1 className="text-3xl font-bold">Predictions</h1>

      {/* Match Prediction */}
      <section className="bg-zinc-900 rounded-lg p-6 border border-zinc-800">
        <h2 className="text-xl font-semibold mb-4">⚽ Match Outcome</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
          <label className="col-span-2 flex flex-col gap-1">
            <span className="text-xs text-zinc-500 uppercase">Home Team</span>
            <input
              value={matchInput.home_team}
              onChange={(e) => setMatchInput({ ...matchInput, home_team: e.target.value })}
              className="bg-zinc-800 rounded px-3 py-2 text-sm border border-zinc-700 focus:border-emerald-500 outline-none"
            />
          </label>
          <label className="col-span-2 flex flex-col gap-1">
            <span className="text-xs text-zinc-500 uppercase">Away Team</span>
            <input
              value={matchInput.away_team}
              onChange={(e) => setMatchInput({ ...matchInput, away_team: e.target.value })}
              className="bg-zinc-800 rounded px-3 py-2 text-sm border border-zinc-700 focus:border-emerald-500 outline-none"
            />
          </label>
          <NumInput label="Home W" value={matchInput.home_form_wins} onChange={(v) => setMatchInput({ ...matchInput, home_form_wins: v })} />
          <NumInput label="Home D" value={matchInput.home_form_draws} onChange={(v) => setMatchInput({ ...matchInput, home_form_draws: v })} />
          <NumInput label="Home L" value={matchInput.home_form_losses} onChange={(v) => setMatchInput({ ...matchInput, home_form_losses: v })} />
          <NumInput label="Away W" value={matchInput.away_form_wins} onChange={(v) => setMatchInput({ ...matchInput, away_form_wins: v })} />
          <NumInput label="Home xG" value={matchInput.home_xg_avg} onChange={(v) => setMatchInput({ ...matchInput, home_xg_avg: v })} step={0.1} />
          <NumInput label="Away xG" value={matchInput.away_xg_avg} onChange={(v) => setMatchInput({ ...matchInput, away_xg_avg: v })} step={0.1} />
          <NumInput label="Home Odds" value={matchInput.home_odds} onChange={(v) => setMatchInput({ ...matchInput, home_odds: v })} step={0.1} />
          <NumInput label="Away Odds" value={matchInput.away_odds} onChange={(v) => setMatchInput({ ...matchInput, away_odds: v })} step={0.1} />
        </div>
        <button
          onClick={handleMatch}
          disabled={loading}
          className="bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 px-6 py-2 rounded font-medium transition"
        >
          {loading ? "Predicting..." : "Predict"}
        </button>
        {matchResult && !matchResult.error && (
          <div className="mt-6 grid grid-cols-3 gap-4">
            <div className="text-center">
              <p className="text-3xl font-bold text-emerald-400">{(matchResult.probabilities?.H * 100).toFixed(1)}%</p>
              <p className="text-xs text-zinc-500 mt-1">Home Win</p>
            </div>
            <div className="text-center">
              <p className="text-3xl font-bold text-amber-400">{(matchResult.probabilities?.D * 100).toFixed(1)}%</p>
              <p className="text-xs text-zinc-500 mt-1">Draw</p>
            </div>
            <div className="text-center">
              <p className="text-3xl font-bold text-red-400">{(matchResult.probabilities?.A * 100).toFixed(1)}%</p>
              <p className="text-xs text-zinc-500 mt-1">Away Win</p>
            </div>
            <div className="col-span-3 text-center mt-2">
              <span className="text-lg font-semibold">Result: </span>
              <span
                className={`text-lg font-bold ${
                  matchResult.predicted_label === "H" ? "text-emerald-400" : matchResult.predicted_label === "A" ? "text-red-400" : "text-amber-400"
                }`}
              >
                {matchResult.predicted_label === "H" ? `${matchResult.home_team} Win` : matchResult.predicted_label === "A" ? `${matchResult.away_team} Win` : "Draw"}
              </span>
              <span className="text-zinc-500 ml-2">({(matchResult.confidence * 100).toFixed(1)}% conf)</span>
            </div>
          </div>
        )}
        {matchResult?.error && <p className="mt-4 text-red-400">{matchResult.error}</p>}
      </section>

      {/* Market Value */}
      <section className="bg-zinc-900 rounded-lg p-6 border border-zinc-800">
        <h2 className="text-xl font-semibold mb-4">💰 Market Value</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
          <NumInput label="Age" value={mvInput.age} onChange={(v) => setMvInput({ ...mvInput, age: v })} />
          <NumInput label="Overall" value={mvInput.overall_rating} onChange={(v) => setMvInput({ ...mvInput, overall_rating: v })} />
          <NumInput label="Potential" value={mvInput.potential} onChange={(v) => setMvInput({ ...mvInput, potential: v })} />
          <NumInput label="Pace" value={mvInput.pace} onChange={(v) => setMvInput({ ...mvInput, pace: v })} />
          <NumInput label="Shooting" value={mvInput.shooting} onChange={(v) => setMvInput({ ...mvInput, shooting: v })} />
          <NumInput label="Passing" value={mvInput.passing} onChange={(v) => setMvInput({ ...mvInput, passing: v })} />
          <NumInput label="Dribbling" value={mvInput.dribbling} onChange={(v) => setMvInput({ ...mvInput, dribbling: v })} />
          <NumInput label="Defending" value={mvInput.defending} onChange={(v) => setMvInput({ ...mvInput, defending: v })} />
          <label className="flex flex-col gap-1">
            <span className="text-xs text-zinc-500 uppercase">Position</span>
            <input
              value={mvInput.position}
              onChange={(e) => setMvInput({ ...mvInput, position: e.target.value })}
              className="bg-zinc-800 rounded px-3 py-2 text-sm border border-zinc-700 focus:border-emerald-500 outline-none"
            />
          </label>
        </div>
        <button
          onClick={handleMV}
          disabled={loading}
          className="bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 px-6 py-2 rounded font-medium transition"
        >
          {loading ? "Estimating..." : "Estimate Value"}
        </button>
        {mvResult && !mvResult.error && (
          <div className="mt-6 text-center">
            <p className="text-4xl font-bold text-emerald-400">€{(mvResult.estimated_value_eur / 1_000_000).toFixed(1)}M</p>
            <p className="text-zinc-500 mt-1">Estimated Market Value</p>
          </div>
        )}
        {mvResult?.error && <p className="mt-4 text-red-400">{mvResult.error}</p>}
      </section>
    </div>
  );
}
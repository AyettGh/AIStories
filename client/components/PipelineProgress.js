"use client";

import {
  BookOpenText,
  Check,
  CircleDashed,
  Clapperboard,
  Image as ImageIcon,
  MonitorPlay,
  Sparkles,
  UsersRound,
} from "lucide-react";

const stages = [
  { key: "story", label: "Story", icon: BookOpenText, start: 5 },
  { key: "script", label: "Scenes", icon: Sparkles, start: 14 },
  { key: "characters", label: "Cast", icon: UsersRound, start: 23 },
  { key: "storyboard", label: "Storyboard", icon: Clapperboard, start: 34 },
  { key: "frames", label: "Frames", icon: ImageIcon, start: 48 },
  { key: "video", label: "Animation", icon: MonitorPlay, start: 66 },
  { key: "concat", label: "Export", icon: Check, start: 90 },
];

export default function PipelineProgress({ progress, currentMessage, status, logs }) {
  return (
    <div className="soft-card overflow-hidden rounded-[28px]">
      <div className="border-b border-[#e7ebe7] px-5 py-5 md:px-7">
        <div className="flex items-start justify-between gap-4">
          <div>
            <p className="text-xs font-black uppercase tracking-[0.16em] text-[#1db954]">Production flow</p>
            <h2 className="mt-1 text-xl font-black tracking-tight text-[#191414]">
              {status === "completed" ? "Production complete" : status === "failed" ? "Production stopped" : "Building your story"}
            </h2>
          </div>
          <span className="rounded-full bg-[#eef2ed] px-3 py-1.5 text-sm font-black text-[#303630]">{Math.max(0, progress)}%</span>
        </div>
        <div className="mt-5 h-2.5 overflow-hidden rounded-full bg-[#e8ede8]">
          <div
            className="h-full rounded-full bg-[#1db954] transition-all duration-500"
            style={{ width: `${Math.max(2, progress)}%` }}
          />
        </div>
        <p className="mt-3 text-sm font-semibold text-[#647064]">{currentMessage}</p>
      </div>

      <div className="grid gap-2 p-5 sm:grid-cols-2 md:grid-cols-4 md:p-7 lg:grid-cols-7">
        {stages.map(({ key, label, icon: Icon, start }) => {
          const completed = progress > start + 10 || status === "completed";
          const active = progress >= start && !completed && status === "running";
          return (
            <div
              key={key}
              className={`rounded-2xl border p-3 transition ${
                completed
                  ? "border-[#bfe9cd] bg-[#edfaf1]"
                  : active
                    ? "border-[#1db954] bg-white shadow-sm"
                    : "border-[#e2e7e2] bg-[#fafbfa]"
              }`}
            >
              <div className={`mb-2 flex h-8 w-8 items-center justify-center rounded-full ${completed || active ? "bg-[#1db954] text-white" : "bg-[#e9ede9] text-[#879087]"}`}>
                {active ? <CircleDashed size={16} className="animate-spin" /> : completed ? <Check size={16} /> : <Icon size={16} />}
              </div>
              <p className="text-xs font-black text-[#3f473f]">{label}</p>
            </div>
          );
        })}
      </div>

      {logs.length > 0 && (
        <details className="border-t border-[#e7ebe7] px-5 py-4 md:px-7">
          <summary className="cursor-pointer text-xs font-black uppercase tracking-[0.13em] text-[#788278]">View activity log</summary>
          <div className="mt-4 max-h-56 space-y-2 overflow-y-auto pr-2">
            {logs.slice().reverse().map((log, index) => (
              <div key={`${log.time}-${index}`} className="flex gap-3 rounded-xl bg-[#f5f7f5] px-3 py-2 text-xs">
                <span className="shrink-0 font-mono text-[#99a199]">{log.time}</span>
                <span className="font-medium text-[#5f695f]">{log.message}</span>
              </div>
            ))}
          </div>
        </details>
      )}
    </div>
  );
}

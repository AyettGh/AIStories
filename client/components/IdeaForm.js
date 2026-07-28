"use client";

import { useMemo, useState } from "react";
import {
  ArrowRight,
  Clapperboard,
  FileText,
  Sparkles,
  UserRound,
  WandSparkles,
} from "lucide-react";

const styles = ["Editorial", "Cinematic", "Anime", "Romantic", "Documentary"];

export default function IdeaForm({ onSubmit, isSubmitting }) {
  const [mode, setMode] = useState("idea2video");
  const [idea, setIdea] = useState("");
  const [script, setScript] = useState("");
  const [requirements, setRequirements] = useState("");
  const [style, setStyle] = useState("Editorial");
  const [creatorName, setCreatorName] = useState("Ayett");

  const primaryText = mode === "idea2video" ? idea : script;
  const canSubmit = primaryText.trim().length >= 3 && !isSubmitting;
  const counter = useMemo(() => primaryText.length, [primaryText]);

  const submit = (event) => {
    event.preventDefault();
    if (!canSubmit) return;
    onSubmit({
      mode,
      idea: mode === "idea2video" ? idea.trim() : script.trim().slice(0, 3000),
      script: mode === "script2video" ? script.trim() : "",
      user_requirement: requirements.trim(),
      style,
      creator_name: creatorName.trim() || "Ayett",
    });
  };

  return (
    <form onSubmit={submit} className="soft-card rounded-[28px] p-5 md:p-7">
      <div className="mb-6 flex items-center justify-between gap-4">
        <div>
          <p className="text-xs font-bold uppercase tracking-[0.18em] text-[#1db954]">
            Create a new story
          </p>
          <h2 className="mt-1 text-2xl font-black tracking-tight text-[#191414]">
            Start with an idea or script
          </h2>
        </div>
        <div className="hidden h-11 w-11 items-center justify-center rounded-full bg-[#e5f8eb] text-[#1db954] md:flex">
          <WandSparkles size={21} />
        </div>
      </div>

      <div className="mb-5 grid grid-cols-2 gap-2 rounded-2xl bg-[#eef2ed] p-1.5">
        <button
          type="button"
          onClick={() => setMode("idea2video")}
          className={`flex items-center justify-center gap-2 rounded-xl px-3 py-3 text-sm font-bold transition ${
            mode === "idea2video"
              ? "bg-white text-[#191414] shadow-sm"
              : "text-[#667066] hover:text-[#191414]"
          }`}
        >
          <Sparkles size={16} />
          Idea to video
        </button>
        <button
          type="button"
          onClick={() => setMode("script2video")}
          className={`flex items-center justify-center gap-2 rounded-xl px-3 py-3 text-sm font-bold transition ${
            mode === "script2video"
              ? "bg-white text-[#191414] shadow-sm"
              : "text-[#667066] hover:text-[#191414]"
          }`}
        >
          <FileText size={16} />
          Script to video
        </button>
      </div>

      <label className="mb-2 block text-sm font-bold text-[#303630]">
        {mode === "idea2video" ? "Your micro-drama idea" : "Your scene script"}
      </label>
      <div className="relative">
        <textarea
          value={mode === "idea2video" ? idea : script}
          onChange={(event) =>
            mode === "idea2video" ? setIdea(event.target.value) : setScript(event.target.value)
          }
          maxLength={mode === "idea2video" ? 3000 : 12000}
          rows={mode === "idea2video" ? 5 : 8}
          placeholder={
            mode === "idea2video"
              ? "A young architect finds a forgotten voice message that changes her final presentation..."
              : "INT. STUDIO — MORNING\nAyett opens the old notebook and notices a sentence written in green ink..."
          }
          className="w-full resize-none rounded-2xl border border-[#dfe5df] bg-[#fbfcfa] px-4 py-4 text-[15px] leading-7 text-[#191414] outline-none transition placeholder:text-[#9ba39b] focus:border-[#1db954] focus:bg-white focus:ring-4 focus:ring-[#1db954]/10"
        />
        <span className="absolute bottom-3 right-4 text-[11px] font-semibold text-[#9ba39b]">
          {counter}
        </span>
      </div>

      <div className="mt-5 grid gap-4 md:grid-cols-2">
        <div>
          <label className="mb-2 block text-sm font-bold text-[#303630]">Visual style</label>
          <div className="relative">
            <Clapperboard className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-[#1db954]" size={17} />
            <select
              value={style}
              onChange={(event) => setStyle(event.target.value)}
              className="w-full appearance-none rounded-2xl border border-[#dfe5df] bg-[#fbfcfa] py-3.5 pl-11 pr-4 text-sm font-semibold text-[#303630] outline-none transition focus:border-[#1db954] focus:bg-white focus:ring-4 focus:ring-[#1db954]/10"
            >
              {styles.map((item) => (
                <option key={item}>{item}</option>
              ))}
            </select>
          </div>
        </div>
        <div>
          <label className="mb-2 block text-sm font-bold text-[#303630]">Creator credit</label>
          <div className="relative">
            <UserRound className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-[#1db954]" size={17} />
            <input
              value={creatorName}
              onChange={(event) => setCreatorName(event.target.value)}
              maxLength={60}
              className="w-full rounded-2xl border border-[#dfe5df] bg-[#fbfcfa] py-3.5 pl-11 pr-4 text-sm font-semibold text-[#303630] outline-none transition focus:border-[#1db954] focus:bg-white focus:ring-4 focus:ring-[#1db954]/10"
            />
          </div>
        </div>
      </div>

      <div className="mt-5">
        <label className="mb-2 block text-sm font-bold text-[#303630]">
          Extra direction <span className="font-medium text-[#8a938a]">(optional)</span>
        </label>
        <input
          value={requirements}
          onChange={(event) => setRequirements(event.target.value)}
          maxLength={3000}
          placeholder="Warm ending, two characters, no violence, social-media friendly..."
          className="w-full rounded-2xl border border-[#dfe5df] bg-[#fbfcfa] px-4 py-3.5 text-sm text-[#303630] outline-none transition placeholder:text-[#9ba39b] focus:border-[#1db954] focus:bg-white focus:ring-4 focus:ring-[#1db954]/10"
        />
      </div>

      <div className="mt-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <p className="max-w-sm text-xs leading-5 text-[#768076]">
          No paid image or video API. Frames and the MP4 are generated locally; Groq is optional.
        </p>
        <button
          type="submit"
          disabled={!canSubmit}
          className="green-shadow inline-flex min-h-12 items-center justify-center gap-2 rounded-full bg-[#1db954] px-6 py-3 text-sm font-black text-white transition hover:scale-[1.02] hover:bg-[#1ed760] disabled:cursor-not-allowed disabled:opacity-45 disabled:hover:scale-100"
        >
          {isSubmitting ? "Starting studio..." : "Generate free video"}
          {!isSubmitting && <ArrowRight size={17} />}
        </button>
      </div>
    </form>
  );
}

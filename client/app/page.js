"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import {
  BadgeCheck,
  CirclePlay,
  Film,
  Gauge,
  Leaf,
  Sparkles,
} from "lucide-react";
import IdeaForm from "../components/IdeaForm";

const benefits = [
  { icon: Gauge, title: "Fast writing", text: "Groq or a built-in offline fallback." },
  { icon: Leaf, title: "Zero paid media", text: "Pillow and FFmpeg render locally." },
  { icon: BadgeCheck, title: "CV ready", text: "Personalized branding and clean architecture." },
];

export default function HomePage() {
  const router = useRouter();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (formData) => {
    setIsSubmitting(true);
    setError("");
    try {
      const response = await fetch("/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Could not start generation.");
      router.push(`/generate/${data.job_id}`);
    } catch (requestError) {
      setError(requestError.message || "Could not reach the backend.");
      setIsSubmitting(false);
    }
  };

  return (
    <main className="mesh-background min-h-screen">
      <header className="mx-auto flex max-w-7xl items-center justify-between px-6 py-6 lg:px-8">
        <div className="flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-full bg-[#1db954] text-white shadow-lg shadow-[#1db954]/20">
            <CirclePlay size={25} fill="currentColor" />
          </div>
          <div>
            <p className="text-lg font-black tracking-[-0.03em] text-[#191414]">AYETT STORIES</p>
            <p className="text-[10px] font-bold uppercase tracking-[0.2em] text-[#788278]">Free creator studio</p>
          </div>
        </div>
        <div className="hidden items-center gap-2 rounded-full border border-[#dfe5df] bg-white/80 px-4 py-2 text-xs font-bold text-[#4f584f] md:flex">
          <Sparkles size={14} className="text-[#1db954]" />
          Light Spotify-inspired edition
        </div>
      </header>

      <section className="mx-auto grid max-w-7xl items-center gap-14 px-6 pb-20 pt-8 lg:grid-cols-[0.9fr_1.1fr] lg:px-8 lg:pb-28 lg:pt-14">
        <div className="animate-rise">
          <div className="mb-6 inline-flex items-center gap-2 rounded-full bg-[#e0f7e8] px-3.5 py-2 text-xs font-black uppercase tracking-[0.14em] text-[#117a39]">
            <Film size={14} />
            Your idea, your visual story
          </div>
          <h1 className="max-w-2xl text-5xl font-black leading-[0.96] tracking-[-0.055em] text-[#191414] md:text-7xl">
            Turn a spark into a <span className="text-[#1db954]">micro-drama.</span>
          </h1>
          <p className="mt-7 max-w-xl text-base leading-7 text-[#657065] md:text-lg md:leading-8">
            Ayett Stories writes, storyboards, illustrates, animates, and exports a short video through a simple personalized workflow—without a paid media API.
          </p>

          <div className="mt-9 grid gap-3 sm:grid-cols-3 lg:grid-cols-1 xl:grid-cols-3">
            {benefits.map(({ icon: Icon, title, text }) => (
              <div key={title} className="rounded-2xl border border-white/80 bg-white/65 p-4 backdrop-blur-sm">
                <Icon size={19} className="mb-3 text-[#1db954]" />
                <p className="text-sm font-black text-[#252125]">{title}</p>
                <p className="mt-1 text-xs leading-5 text-[#748074]">{text}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="animate-rise" style={{ animationDelay: "80ms" }}>
          {error && (
            <div className="mb-4 rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm font-semibold text-red-700">
              {error}
            </div>
          )}
          <IdeaForm onSubmit={handleSubmit} isSubmitting={isSubmitting} />
        </div>
      </section>

      <footer className="border-t border-[#e1e6e1] bg-white/55">
        <div className="mx-auto flex max-w-7xl flex-col gap-2 px-6 py-6 text-xs text-[#758075] sm:flex-row sm:items-center sm:justify-between lg:px-8">
          <span>Ayett Stories — personalized portfolio project</span>
          <span>Groq optional · Pillow + FFmpeg local media</span>
        </div>
      </footer>
    </main>
  );
}

"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { ArrowLeft, CirclePlay } from "lucide-react";
import PipelineProgress from "../../../components/PipelineProgress";
import VideoResult from "../../../components/VideoResult";

export default function GeneratePage() {
  const { jobId } = useParams();
  const [status, setStatus] = useState("running");
  const [videoUrl, setVideoUrl] = useState("");
  const [errorMsg, setErrorMsg] = useState("");
  const [progress, setProgress] = useState(0);
  const [currentMessage, setCurrentMessage] = useState("Starting your free production pipeline...");
  const [logs, setLogs] = useState([]);
  const finishedRef = useRef(false);

  useEffect(() => {
    if (!jobId) return undefined;
    const source = new EventSource(`/api/status/${jobId}`);

    const addLog = (event) => {
      setLogs((current) => [
        ...current,
        {
          time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" }),
          message: event.message || event.stage || event.type,
        },
      ]);
    };

    source.onmessage = (message) => {
      try {
        const event = JSON.parse(message.data);
        addLog(event);
        if (event.type === "progress") {
          setProgress(event.progress || 0);
          setCurrentMessage(event.message || "Working...");
        }
        if (event.type === "complete") {
          finishedRef.current = true;
          setStatus("completed");
          setProgress(100);
          setVideoUrl(event.video_url);
          setCurrentMessage("Your Ayett Stories video is ready.");
          source.close();
        }
        if (event.type === "error") {
          finishedRef.current = true;
          setStatus("failed");
          setErrorMsg(event.message || "Generation failed.");
          setCurrentMessage("The production stopped.");
          source.close();
        }
      } catch (error) {
        console.error("Invalid progress event", error);
      }
    };

    source.onerror = async () => {
      source.close();
      if (finishedRef.current) return;
      try {
        const response = await fetch(`/api/result/${jobId}`);
        const data = await response.json();
        if (data.status === "completed") {
          finishedRef.current = true;
          setStatus("completed");
          setProgress(100);
          setVideoUrl(data.video_url);
          setCurrentMessage("Your Ayett Stories video is ready.");
        } else if (data.status === "failed") {
          finishedRef.current = true;
          setStatus("failed");
          setErrorMsg(data.error || "Generation failed.");
        }
      } catch {
        setErrorMsg("The live connection ended. Check that the backend is still running.");
      }
    };

    return () => source.close();
  }, [jobId]);

  return (
    <main className="mesh-background min-h-screen">
      <header className="sticky top-0 z-20 border-b border-[#e2e7e2] bg-white/90 backdrop-blur-xl">
        <div className="mx-auto flex max-w-7xl items-center gap-4 px-6 py-4 lg:px-8">
          <Link href="/" className="flex items-center gap-2 text-sm font-black text-[#596359] transition hover:text-[#1db954]">
            <ArrowLeft size={17} /> New story
          </Link>
          <div className="h-5 w-px bg-[#dfe5df]" />
          <div className="flex items-center gap-2">
            <CirclePlay size={21} className="text-[#1db954]" fill="currentColor" />
            <span className="font-black tracking-tight text-[#191414]">AYETT STORIES</span>
          </div>
          <div className="ml-auto">
            <span className={`inline-flex items-center gap-2 rounded-full px-3 py-1.5 text-xs font-black ${
              status === "completed"
                ? "bg-[#e2f8e9] text-[#14763a]"
                : status === "failed"
                  ? "bg-red-100 text-red-700"
                  : "bg-[#fff3d7] text-[#875c08]"
            }`}>
              <span className={`h-2 w-2 rounded-full ${status === "completed" ? "bg-[#1db954]" : status === "failed" ? "bg-red-500" : "animate-pulse bg-amber-500"}`} />
              {status === "completed" ? "Complete" : status === "failed" ? "Failed" : "Producing"}
            </span>
          </div>
        </div>
      </header>

      <div className="mx-auto max-w-6xl space-y-7 px-6 py-10 lg:px-8 lg:py-14">
        {status === "completed" && videoUrl && <VideoResult videoUrl={videoUrl} jobId={jobId} />}

        {status === "failed" && (
          <div className="animate-rise rounded-[24px] border border-red-200 bg-red-50 p-5 text-red-800">
            <p className="font-black">Generation failed</p>
            <p className="mt-1 text-sm leading-6">{errorMsg}</p>
          </div>
        )}

        <PipelineProgress
          progress={progress}
          currentMessage={currentMessage}
          status={status}
          logs={logs}
        />
      </div>
    </main>
  );
}

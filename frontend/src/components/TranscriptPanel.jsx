import { useEffect, useRef } from "react";

export default function TranscriptPanel({ transcript }) {
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [transcript]);

  return (
    <section className="flex h-full flex-col">
      <p className="section-label">Live Transcript</p>
      <div className="mt-3 flex-1 overflow-y-auto pr-2">
        {transcript.length === 0 ? (
          <div className="flex items-center justify-center h-full text-[var(--color-text-secondary)]">
            <div className="text-center">
              <div className="text-2xl mb-2">🎤</div>
              <div>Listening for audio...</div>
              <div className="text-xs mt-2">Transcription will appear here</div>
              <div className="text-xs mt-1">(15-30s delay expected)</div>
            </div>
          </div>
        ) : (
          <div className="flex flex-col gap-3 text-sm">
            {transcript.map((line, index) => (
              <div key={`${line.time}-${index}`} className="leading-[var(--line-height-base)]">
                <span className="text-[11px] text-[var(--color-text-secondary)]">{line.time}</span>
                <span className="mx-2 text-[var(--color-text-muted)]">|</span>
                <span className="font-bold text-[var(--color-text-primary)]">{line.speaker}</span>
                <span className="text-[var(--color-text-secondary)]">: </span>
                {line.isRisk ? <span className="risk-highlight">{line.text}</span> : <span>{line.text}</span>}
              </div>
            ))}
            <div ref={endRef} />
          </div>
        )}
      </div>
    </section>
  );
}

import { useEffect, useRef } from "react";

const speakerColor = {
  CALLER: "var(--color-text-primary)",
  OPERATOR: "var(--verdict-low)",
};

export default function TranscriptPanel({ transcript }) {
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [transcript]);

  return (
    <section className="flex h-full flex-col">
      <div className="flex items-center justify-between">
        <p className="section-label">Live Transcript</p>
        <span className="text-[11px] text-[var(--color-text-muted)] uppercase tracking-[var(--letter-spacing-caps)]">
          {transcript.length} lines
        </span>
      </div>

      <div className="mt-3 flex-1 overflow-y-auto pr-2">
        {transcript.length === 0 ? (
          <div className="flex h-full items-center justify-center">
            <p className="text-[13px] text-[var(--color-text-muted)]">Waiting for call to begin...</p>
          </div>
        ) : (
          <div className="flex flex-col gap-3">
            {transcript.map((line, index) => (
              <div
                key={`${line.time}-${index}`}
                className="leading-[var(--line-height-base)]"
              >
                <span className="text-[11px] text-[var(--color-text-muted)]">{line.time}</span>
                <span className="mx-2 text-[var(--color-text-muted)]">|</span>
                <span
                  className="font-bold text-[12px] uppercase tracking-[var(--letter-spacing-caps)]"
                  style={{ color: speakerColor[line.speaker] ?? "var(--color-text-secondary)" }}
                >
                  {line.speaker}
                </span>
                <span className="text-[var(--color-text-muted)]">: </span>
                {line.isRisk
                  ? <span className="risk-highlight text-[14px]">{line.text}</span>
                  : <span className="text-[14px] text-[var(--color-text-secondary)]">{line.text}</span>
                }
              </div>
            ))}
            <div ref={endRef} />
          </div>
        )}
      </div>
    </section>
  );
}
